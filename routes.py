from fastapi import APIRouter, HTTPException, Form, UploadFile, File
from fastapi.responses import FileResponse
from models import Member, Manager, LoginRequest, ManagerToken, MemberToken, Record
from pymongo import MongoClient
from dotenv import load_dotenv
from pathlib import Path
from typing import Union, Optional
from BrainAge.BrainAge import runPreprocessing
from BrainAge.BrainAge import runBrainage
from AD_prediction.AD_prediction import runModel as runPreAD
from nii_to_2D.nii_to_2D import runModel as runSlice
import os
import jwt
import datetime
import shutil

# 載入 .env 環境變數
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")
MEMBER_COLLECTION = os.getenv("MEMBER_COLLECTION")
MANAGER_COLLECTION = os.getenv("MANAGER_COLLECTION")
SECRET_KEY = os.getenv("SECRET_KEY")
STORAGE_ROOT = os.getenv("STORAGE_ROOT","data")

# 連接 MongoDB
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
member_collection = db[MEMBER_COLLECTION]
manager_collection = db[MANAGER_COLLECTION]

# 創建 FastAPI 路由
router = APIRouter()

token_blacklist = set()

def check_token_valid(token: str):
    if token in token_blacklist:
        raise HTTPException(status_code=401, detail="Token 已失效")
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token 已過期")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="無效的 Token")

# 創建 JWT Token
def create_jwt_token(data: dict, expires_delta: datetime.timedelta = datetime.timedelta(hours=1)):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

# 本地存儲路徑
MANAGER_PROFILE_DIR = os.path.join(STORAGE_ROOT, "manager_profile")
MEMBER_PROFILE_DIR = os.path.join(STORAGE_ROOT, "member_profile")
BRAIN_IMAGE_DIR = os.path.join(STORAGE_ROOT, "brain_image")
for path in [MANAGER_PROFILE_DIR, MEMBER_PROFILE_DIR, BRAIN_IMAGE_DIR]:
    os.makedirs(path, exist_ok=True)
Path(STORAGE_ROOT).mkdir(parents=True, exist_ok=True)

### 取得醫生個人照 ###
@router.get("/manager/Profile/{manager_id}")
def get_manager_profile(manager_id: str):
    manager = manager_collection.find_one({"id": manager_id})
    if not manager or "profile_image_path" not in manager:
        raise HTTPException(status_code=404, detail="找不到該醫生或個人照")
    profile_path = manager["profile_image_path"]
    if not os.path.exists(profile_path):
        raise HTTPException(status_code=404, detail="個人照不存在")
    return FileResponse(profile_path)

### 取得會員個人照 ###
@router.get("/member/Profile/{member_id}")
def get_member_profile(member_id: str):
    member = member_collection.find_one({"id": member_id})
    if not member or "profile_image_path" not in member:
        raise HTTPException(status_code=404, detail="找不到該會員或個人照")
    profile_path = member["profile_image_path"]
    if not os.path.exists(profile_path):
        raise HTTPException(status_code=404, detail="個人照不存在")
    return FileResponse(profile_path)

### 取得Slice切片 ###
@router.get("/ai/slice/{member_id}/{record_count}/{plane}/{index}")
def get_slice_image(
    member_id: str,
    record_count: int,
    plane: str,
    index: int
):
    record_id = f"record{str(record_count).zfill(3)}"
    result = member_collection.find_one(
        {"id": member_id},
        {"_id": 0, "RecordList": {"$elemMatch": {"record_id": record_id}}}
    )
    if not result or "RecordList" not in result or len(result["RecordList"]) == 0:
        raise HTTPException(status_code=404, detail="找不到指定的紀錄")

    record = result["RecordList"][0]
    folder_path = record["folder_path"]

    plane = plane.lower()
    if plane not in {"sagittal", "coronal", "axial"}:
        raise HTTPException(status_code=400, detail="plane 參數錯誤，請使用 sagittal、coronal 或 axial")
    png_filename = f"{index:03d}.png"
    png_path = os.path.join(folder_path, plane, png_filename)

    if not os.path.exists(png_path):
        raise HTTPException(status_code=404, detail="找不到指定的切片圖檔")

    return FileResponse(png_path, media_type="image/png")

### 管理員註冊 ###
@router.post("/manager/Manager_Signup")
def manager_signup(
    id: str = Form(...),
    password: str = Form(...),
    department: str = Form(...),
    name: str = Form(...),
    profile_image_file: UploadFile = File(...)
):
    if manager_collection.find_one({"id": id}):
        raise HTTPException(status_code=400, detail="該醫生編號已註冊")

    profile_path = os.path.join(MANAGER_PROFILE_DIR, f"{id}.jpg")
    with open(profile_path, "wb") as f:
        shutil.copyfileobj(profile_image_file.file, f)

    new_manager = Manager(
        id=id,
        password=password,
        department=department,
        name=name,
        profile_image_path=profile_path,
        numMembers=0
    )
    manager_collection.insert_one(new_manager.dict())
    return {"message": "醫師註冊成功"}

### 管理員登入 ###
@router.post("/manager/Signin")
def manager_signin(signin_data: LoginRequest):
    manager = manager_collection.find_one({"id": signin_data.id})
    if not manager or manager["password"] != signin_data.password:
        raise HTTPException(status_code=401, detail="帳號或密碼錯誤")
    
    manager_token = create_jwt_token({"id": signin_data.id, "role": "manager"})

    return {"manager_token": manager_token, "message": f"{signin_data.id} 成功登入"}

### 會員註冊 ###
@router.post("/manager/Member_Signup")
def member_signup(
    id: str = Form(...),
    sex: str = Form(...),
    name: str = Form(...),
    birthdate: str = Form(...),
    profile_image_file: UploadFile = File(...),
    managerToken: str = Form(...)
):
    decoded_token = check_token_valid(managerToken)
    if decoded_token["role"] != "manager":
        raise HTTPException(status_code=403, detail="僅限醫師新增會員")
    manager_id = decoded_token["id"]
    
    if member_collection.find_one({"id": id}):
        raise HTTPException(status_code=400, detail="該身份證字號已被註冊")

    profile_image_path = os.path.join(MEMBER_PROFILE_DIR, f"{id}.jpg")
    with open(profile_image_path, "wb") as buffer:
        shutil.copyfileobj(profile_image_file.file, buffer)

    new_member = Member(
        id=id,
        sex=sex,
        name=name,
        birthdate=birthdate,
        profile_image_path=profile_image_path,
        managerID=manager_id
    )

    new_member.generate_password()

    member_data = new_member.dict()
    member_collection.insert_one(member_data)

    manager_collection.update_one({"id": manager_id}, {"$inc": {"numMembers": 1}})

    return {"message": "成員註冊成功。"}

### 取得醫生資訊 ###
@router.post("/manager/Info")
def get_manager_info(manager_token: ManagerToken):
    manager_id = jwt.decode(manager_token.token, SECRET_KEY, algorithms=["HS256"])["id"]
    manager = manager_collection.find_one({"id": manager_id}, {"_id": 0, "password": 0})
    if not manager:
        raise HTTPException(status_code=404, detail="找不到該醫生")
    return manager

### 取得成員列表 ###
@router.post("/manager/MemberList")
def get_member_list(manager_token: ManagerToken):
    decoded_token = check_token_valid(manager_token.token)
    if decoded_token["role"] != "manager":
        raise HTTPException(status_code=403, detail="無權限")
    manager_id = decoded_token["id"]
    members = list(member_collection.find({"managerID": manager_id}, {"_id": 0, "password": 0}))
    return members

### 成員登入 ###
@router.post("/member/Signin")
def member_signin(signin_data: LoginRequest):
    member = member_collection.find_one({"id": signin_data.id})
    if not member or signin_data.password != member["birthdate"]:
        raise HTTPException(status_code=401, detail="帳號或密碼錯誤")
    token = create_jwt_token({"id": signin_data.id, "role": "member"})
    return {"member_token": token, "message": f"{signin_data.id} 成功登入"}

### 取得成員拍攝紀錄 ###
@router.post("/member/RecordsList")
def get_member_records(token: Union[MemberToken, ManagerToken], member_id: str):
    decoded = check_token_valid(token.token)
    user_id = decoded["id"]
    user_role = decoded["role"]

    if user_role == "manager":
        records = member_collection.find_one({"id": member_id}, {"_id": 0, "password": 0, "managerID": 0})
    elif user_role == "member" and user_id == member_id:
        records = member_collection.find_one({"id": member_id}, {"_id": 0, "password": 0, "managerID": 0})
    else:
        raise HTTPException(status_code=403, detail="無權查看此成員的紀錄")

    if not records:
        raise HTTPException(status_code=404, detail="找不到該成員的紀錄")

    return sorted(records.get("RecordList", []), key=lambda x: x["date"])

### 獲取單一成員基本資料 ###
@router.post("/member/Info")
def get_member_info(token: Union[MemberToken, ManagerToken], member_id: str):
    decoded = check_token_valid(token.token)
    user_id = decoded["id"]
    user_role = decoded["role"]

    if user_role == "manager":
        member = member_collection.find_one({"id": member_id}, {"_id": 0, "password": 0, "managerID": 0})
    elif user_role == "member" and user_id == member_id:
        member = member_collection.find_one({"id": member_id}, {"_id": 0, "password": 0, "managerID": 0})
    else:
        raise HTTPException(status_code=403, detail="無權查看此成員資料")

    if not member:
        raise HTTPException(status_code=404, detail="找不到該會員")

    return member

### 上傳拍攝記錄 + 前處理 ###
## bottom：建立紀錄 ##
@router.post("/ai/upload/Record")
def upload_record(
    managerToken: str = Form(...),
    member_id: str = Form(...),
    date: str = Form(...),
    MMSE_score: Optional[int] = Form(None),
    image_file: UploadFile = File(...)
):
    decoded_token = check_token_valid(managerToken)
    if decoded_token["role"] != "manager":
        raise HTTPException(status_code=403, detail="非醫師帳號")
    member = member_collection.find_one({"id": member_id})
    if not member:
        raise HTTPException(status_code=404, detail="找不到該成員")

    record_count = member.get("record_count", 0) + 1
    record_id = f"record{str(record_count).zfill(3)}"
    member_folder = os.path.join(BRAIN_IMAGE_DIR, f"{member_id}_{str(record_count).zfill(3)}")
    os.makedirs(member_folder, exist_ok=True)

    if not image_file.filename.lower().endswith(".nii.gz"):
        raise HTTPException(status_code=400, detail="請上傳 .nii.gz 檔案")
    original_path = os.path.join(member_folder, "original.nii.gz")
    with open(original_path, "wb") as f:
        shutil.copyfileobj(image_file.file, f)

    abs_path = os.path.abspath(original_path)
    try:
        preprocessing_path = runPreprocessing(abs_path)
        if not preprocessing_path or not preprocessing_path.endswith(".nii.gz"):
            raise ValueError("前處理回傳路徑錯誤")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"前處理失敗: {str(e)}")

    final_pp_path = os.path.join(member_folder, "preprocessing.nii.gz")
    shutil.move(preprocessing_path, final_pp_path)

    birthdate = member["birthdate"]
    record = Record(
        member_id=member_id,
        record_id=record_id,
        date=date,
        MMSE_score=MMSE_score,
        folder_path=member_folder
    )
    record.compute_actual_age(birthdate)
    member_collection.update_one(
        {"id": member_id},
        {
            "$push": {"RecordList": record.dict()},
            "$set": {"record_count": record_count}
        }
    )
    return {"message": "成功上傳紀錄並完成前處理"}

### AI 推論（模型 + 風險）###
## bottom：AI計算 ##
@router.post("/ai/{member_id}")
def ai_brain_age(
    member_id: str,
    record_count: int,
    manager_token: str = Form(...)
):
    decoded_token = check_token_valid(manager_token)
    if decoded_token["role"] != "manager":
        raise HTTPException(status_code=403, detail="非醫師帳號")

    record_id = f"record{str(record_count).zfill(3)}"
    result = member_collection.find_one(
        {"id": member_id},
        {"_id": 0, "RecordList": {"$elemMatch": {"record_id": record_id}}}
    )
    if not result or "RecordList" not in result or len(result["RecordList"]) == 0:
        raise HTTPException(status_code=404, detail="找不到指定的紀錄")
    record_data = result["RecordList"][0]
    folder_path = os.path.join(os.path.dirname(__file__), record_data["folder_path"])
    actual_age = record_data["actual_age"]
    MMSE_score = record_data.get("MMSE_score")
    
    OG_image_path = os.path.join(folder_path, "original.nii.gz")
    PP_image_path = os.path.join(folder_path, "preprocessing.nii.gz")
    if not os.path.exists(OG_image_path) or not os.path.exists(PP_image_path):
        raise HTTPException(status_code=404, detail="找不到 MRI 檔案")

    sex = member_collection.find_one({"id": member_id}, {"_id": 0, "sex": 1}).get("sex")
    try:
        brain_age = runBrainage(PP_image_path)
        risk_score = runPreAD(MMSE_score=MMSE_score, original_image_path=OG_image_path,
                              actual_age=actual_age, sex=sex) if MMSE_score else None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"模型推論失敗: {str(e)}")

    update_result = member_collection.update_one(
        {"id": member_id, "RecordList.record_id": record_id},
        {"$set": {"RecordList.$.brain_age": brain_age, "RecordList.$.risk_score": risk_score}}
    )

    if update_result.modified_count == 0:
        raise HTTPException(status_code=500, detail="結果寫入資料庫失敗")

    return {
        "message": "AI 預測完成",
        "record_id": record_id,
        "brainAge": brain_age,
        "riskScore": risk_score
    }

### 2D切片+儲存結果 ###
## bottom：儲存 ##
@router.post("/ai/restore/{member_id}")
def ai_brain_age(
    member_id: str,
    record_count: int,
    manager_token: str = Form(...)
):
    decoded_token = check_token_valid(manager_token)
    if decoded_token["role"] != "manager":
        raise HTTPException(status_code=403, detail="非醫師帳號")

    record_id = f"record{str(record_count).zfill(3)}"
    result = member_collection.find_one(
        {"id": member_id},
        {"_id": 0, "RecordList": {"$elemMatch": {"record_id": record_id}}}
    )

    if not result or "RecordList" not in result or len(result["RecordList"]) == 0:
        raise HTTPException(status_code=404, detail="找不到指定的紀錄")

    record_data = result["RecordList"][0]
    folder_path = os.path.join(os.path.dirname(__file__), record_data["folder_path"])
    PP_image_path = os.path.join(folder_path, "preprocessing.nii.gz")

    if not os.path.exists(PP_image_path):
        raise HTTPException(status_code=404, detail="找不到前處理 MRI 檔案")

    try:
        output_dir = runSlice(PP_image_path, folder_path)
        return {"outputDirection": output_dir}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"切片失敗: {str(e)}")

### 登出 ###
@router.post("/Logout")
def logout(token: str = Form(...)):
    decoded = check_token_valid(token)
    if decoded.get("role") not in {"member", "manager"}:
        raise HTTPException(status_code=403, detail="不支援的角色")
    token_blacklist.add(token)
    return {"message": f"{decoded['role']} 已成功登出"}