from fastapi import APIRouter, HTTPException, Depends, Form, UploadFile, File
from fastapi.security import OAuth2PasswordBearer
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
import re

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

# 創建 JWT Token
def create_jwt_token(data: dict, expires_delta: datetime.timedelta = datetime.timedelta(hours=1)):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

# Token 驗證中間件
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
token_blacklist = set()
def verify_token(token: str = Depends(oauth2_scheme)):
    if token in token_blacklist:
        raise HTTPException(status_code=401, detail="Token 已失效")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token 已過期")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="無效的 Token")

# 本地存儲路徑
MANAGER_PROFILE_DIR = os.path.join(STORAGE_ROOT, "manager_profile")
os.makedirs(MANAGER_PROFILE_DIR, exist_ok=True)
MEMBER_PROFILE_DIR = os.path.join(STORAGE_ROOT, "member_profile")
os.makedirs(MEMBER_PROFILE_DIR, exist_ok=True)
BRAIN_IMAGE_DIR = os.path.join(STORAGE_ROOT, "brain_image")
os.makedirs(BRAIN_IMAGE_DIR, exist_ok=True)
Path(STORAGE_ROOT).mkdir(parents=True, exist_ok=True)

### 取得醫生個人照 ###
@router.get("/manager/profile/{manager_id}")
def get_manager_profile(manager_id: str):
    manager = manager_collection.find_one({"id": manager_id})
    if not manager or "profile_image_path" not in manager:
        raise HTTPException(status_code=404, detail="找不到該醫生或個人照")
    
    profile_path = manager["profile_image_path"]
    if not os.path.exists(profile_path):
        raise HTTPException(status_code=404, detail="個人照不存在")

    return FileResponse(profile_path)

### 取得會員個人照 ###
@router.get("/member/profile/{member_id}")
def get_member_profile(member_id: str):
    member = member_collection.find_one({"id": member_id})
    if not member or "profile_image_path" not in member:
        raise HTTPException(status_code=404, detail="找不到該會員或個人照")
    
    profile_path = member["profile_image_path"]
    if not os.path.exists(profile_path):
        raise HTTPException(status_code=404, detail="個人照不存在")

    return FileResponse(profile_path)

@router.get("/slice/{member_id}/{record_count}/{plane}/{index}")
def get_slice_image(
    member_id: str,
    record_count: int,
    plane: str,
    index: int
):
    """
    根據 member_id + record_count + plane + index 回傳對應切片圖檔：
    - plane: 'sagittal' | 'coronal' | 'axial'
    - index: 圖檔編號（整數）
    """
    record_id = f"record{str(record_count).zfill(3)}"

    # === 查詢該筆紀錄資料 ===
    result = member_collection.find_one(
        {"id": member_id},
        {"_id": 0, "RecordList": {"$elemMatch": {"record_id": record_id}}}
    )
    if not result or "RecordList" not in result or len(result["RecordList"]) == 0:
        raise HTTPException(status_code=404, detail="找不到指定的紀錄")

    record = result["RecordList"][0]
    folder_path = record["folder_path"]

    # === 判別 plane 子資料夾 ===
    plane = plane.lower()
    if plane not in {"sagittal", "coronal", "axial"}:
        raise HTTPException(status_code=400, detail="plane 參數錯誤，請使用 sagittal、coronal 或 axial")

    # === 組合檔案路徑 ===
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
    # 檢查是否已存在該管理員
    if manager_collection.find_one({"id": id}):
        raise HTTPException(status_code=400, detail="該醫生編號已註冊")

    # 儲存圖片
    profile_image_path = os.path.join(MANAGER_PROFILE_DIR, f"{id}.jpg")
    with open(profile_image_path, "wb") as buffer:
        shutil.copyfileobj(profile_image_file.file, buffer)
    path = os.path.join(BRAIN_IMAGE_DIR)

    # 存入資料庫
    new_manager = Manager(
        id=id,
        password=password,
        department=department,
        name=name,
        profile_image_path=profile_image_path,
        numMembers=0  # 初始沒有病人
    )
    manager_collection.insert_one(new_manager.dict())

    return {"message": "醫師註冊成功"}

### 管理員登入 ###
@router.post("/manager/Signin")
def manager_signin(signin_data: LoginRequest):
    manager = manager_collection.find_one({"id": signin_data.id})

    if not manager or manager["password"] != signin_data.password:
        raise HTTPException(status_code=401, detail="帳號或密碼錯誤")

    # 生成管理員的 token，並加上 "role" 欄位
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
    # **驗證管理員 Token**
    try:
        manager_data = jwt.decode(managerToken, SECRET_KEY, algorithms=["HS256"])
        manager_id = manager_data["id"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token 已過期")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="無效的 Token")

    if not manager_collection.find_one({"id": manager_id}):
        raise HTTPException(status_code=401, detail="無效的管理員 Token")

    # **檢查會員是否已存在**
    if member_collection.find_one({"id": id}):
        raise HTTPException(status_code=400, detail="該身份證字號已被註冊")

    # **儲存圖片**
    profile_image_path = os.path.join(MEMBER_PROFILE_DIR, f"{id}.jpg")
    with open(profile_image_path, "wb") as buffer:
        shutil.copyfileobj(profile_image_file.file, buffer)

    # **創建會員物件**
    new_member = Member(
        id=id,
        sex=sex,
        name=name,
        birthdate=birthdate,
        profile_image_path=profile_image_path,
        managerID=manager_id
    )

    # **生成預設密碼**
    new_member.generate_password()

    # **插入會員資料**
    member_data = new_member.dict()
    member_collection.insert_one(member_data)

    # **更新醫生的會員數**
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
    manager_id = jwt.decode(manager_token.token, SECRET_KEY, algorithms=["HS256"])["id"]
    members_cursor = member_collection.find({"managerID": manager_id}, {"_id": 0, "password": 0})
    members = list(members_cursor)
    return members

### 成員登入 ###
@router.post("/member/Signin")
def member_signin(signin_data: LoginRequest):
    member = member_collection.find_one({"id": signin_data.id})

    if not member:
        raise HTTPException(status_code=401, detail="帳號或密碼錯誤")

    # 產生應該匹配的密碼
    expected_password = f"{member['birthdate']}"

    if signin_data.password != expected_password:
        raise HTTPException(status_code=401, detail="帳號或密碼錯誤")

    # 生成成員的 token，並加上 "role" 欄位
    member_token = create_jwt_token({"id": signin_data.id, "role": "member"})
    return {"member_token": member_token, "message": f"{signin_data.id} 成功登入"}

### 取得成員拍攝紀錄 ###
@router.post("/member/RecordsList")
def get_member_records(token: Union[MemberToken, ManagerToken], member_id: str):
    # 解析 token 以獲取角色和 ID
    decoded_token = jwt.decode(token.token, SECRET_KEY, algorithms=["HS256"])
    user_id = decoded_token.get("id")  # 使用 .get() 確保不會拋出 KeyError
    user_role = decoded_token.get("role")  # 使用 .get() 確保不會拋出 KeyError

    # 檢查是否為管理者或該成員自己
    if user_role == "manager":
        # 管理者可以查看任何成員的紀錄
        records = member_collection.find_one({"id": member_id}, {"_id": 0, "password": 0, "managerID": 0})
    elif user_role == "member" and user_id == member_id:
        # 成員只能查看自己的紀錄
        records = member_collection.find_one({"id": member_id}, {"_id": 0, "password": 0, "managerID": 0})
    else:
        # 非法訪問：如果是成員但請求查看其他人的紀錄，則返回錯誤
        raise HTTPException(status_code=403, detail="無權查看此成員的紀錄")

    if not records:
        raise HTTPException(status_code=404, detail="找不到該成員的紀錄")

    # 根據日期排序紀錄
    return sorted(records.get("RecordList", []), key=lambda x: x["date"])

### 獲取單一成員基本資料 ###
@router.post("/member/Info")
def get_member_info(token: Union[MemberToken, ManagerToken], member_id: str):
    # 解析 token 以獲取角色和 ID
    decoded_token = jwt.decode(token.token, SECRET_KEY, algorithms=["HS256"])
    user_id = decoded_token.get("id")  # 使用 .get() 確保不會拋出 KeyError
    user_role = decoded_token.get("role")  # 使用 .get() 確保不會拋出 KeyError

    # 檢查是否為管理者或該成員自己
    if user_role == "manager":
        # 管理者可以查看任何成員的紀錄
        member = member_collection.find_one({"id": member_id}, {"_id": 0, "password": 0, "managerID": 0})
    elif user_role == "member" and user_id == member_id:
        # 成員只能查看自己的紀錄
        member = member_collection.find_one({"id": member_id}, {"_id": 0, "password": 0, "managerID": 0})
    else:
        # 非法訪問：如果是成員但請求查看其他人的紀錄，則返回錯誤
        raise HTTPException(status_code=403, detail="無權查看此成員資料")
  
    if not member:
        raise HTTPException(status_code=404, detail="找不到該會員")
    
    return member

### 上傳拍攝記錄 + 前處理 ###
## bottom：建立紀錄 ##
@router.post("/upload/Record")
def upload_record(
    managerToken: str = Form(...),
    member_id: str = Form(...),
    date: str = Form(...),
    MMSE_score: Optional[int] = Form(None),
    image_file: UploadFile = File(...)
):
    # === 驗證管理員 Token ===
    try:
        manager_data = jwt.decode(managerToken, SECRET_KEY, algorithms=["HS256"])
        manager_id = manager_data["id"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token 已過期")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="無效的 Token")

    if not manager_collection.find_one({"id": manager_id}):
        raise HTTPException(status_code=401, detail="無效的管理員 Token")

    # === 確認成員是否存在 ===
    member = member_collection.find_one({"id": member_id})
    if not member:
        raise HTTPException(status_code=404, detail="找不到該成員")

    # === 組合資料路徑與檔案 ===
    record_count = member.get("record_count") + 1
    record_id = f"record{str(record_count).zfill(3)}"

    filename = image_file.filename.lower()
    if not filename.endswith(".nii.gz"):
        raise HTTPException(status_code=400, detail="檔案格式錯誤，僅支援 .nii.gz")

    member_folder = os.path.join(BRAIN_IMAGE_DIR, f"{member_id}_{str(record_count).zfill(3)}")
    os.makedirs(member_folder, exist_ok=True)

    # === 儲存原始影像 ===
    OG_image_path = os.path.join(member_folder, "original.nii.gz")

    with open(OG_image_path, "wb") as buffer:
        shutil.copyfileobj(image_file.file, buffer)

    # === 前處理 ===
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))  
        OG_image_path = os.path.join(base_dir,OG_image_path)  # 轉為絕對路徑
        preprocessing_path = runPreprocessing(OG_image_path)
        if not preprocessing_path:
            raise ValueError("前處理未回傳任何路徑")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"前處理失敗: {str(e)}")

    # === 搬移並重新命名為 preprocessing.nii.gz ===
    if preprocessing_path.endswith(".nii.gz"):
        new_filename = "preprocessing.nii.gz"
    else:
        raise HTTPException(status_code=400, detail="預處理檔案格式錯誤")

    destination_path = os.path.join(member_folder, new_filename)

    try:
        shutil.move(preprocessing_path, destination_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搬移預處理檔案失敗: {str(e)}")

    # === 計算實際年齡與建構 Record ===
    birthdate = member["birthdate"]
    record = Record(
        member_id=member_id,
        record_id=record_id,
        date=date,
        MMSE_score=MMSE_score,
        folder_path=member_folder,
    )
    record.compute_actual_age(birthdate)

    # === 寫入資料庫 ===
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
    # === 驗證角色 ===
    decoded_token = jwt.decode(manager_token, SECRET_KEY, algorithms=["HS256"])
    user_role = decoded_token.get("role")
    if user_role != "manager":
        raise HTTPException(status_code=403, detail="此功能僅限醫生使用")

    # === 組合 record_id ===
    record_id = f"record{str(record_count).zfill(3)}"

    # === 查詢紀錄資料 ===
    result = member_collection.find_one(
        {"id": member_id},
        {"_id": 0, "RecordList": {"$elemMatch": {"record_id": record_id}}}
    )

    if not result or "RecordList" not in result or len(result["RecordList"]) == 0:
        raise HTTPException(status_code=404, detail="找不到指定的紀錄")

    record_data = result["RecordList"][0]
    folder_path = record_data["folder_path"]
    base_dir = os.path.dirname(os.path.abspath(__file__))
    folder_path =  os.path.join(base_dir,folder_path)
    actual_age = record_data["actual_age"]
    MMSE_score = record_data.get("MMSE_score")
    if os.path.exists(os.path.join(folder_path, "original.nii.gz")):
        OG_image_path = os.path.join(folder_path, "original.nii.gz")
    else:
        raise HTTPException(status_code=404, detail="找不到原始MRI檔案")

    sex = member_collection.find_one(
        {"id": member_id},
        {"_id": 0, "sex": 1}
    ).get("sex")

    # === 使用 preprocessing.nii(.gz) 作推論輸入 ===
    if os.path.exists(os.path.join(folder_path, "preprocessing.nii.gz")):
        PP_image_path = os.path.join(folder_path, "preprocessing.nii.gz")
    else:
        raise HTTPException(status_code=404, detail="找不到預處理檔案")
    # === 模型推論與風險分數 ===
    try:
        brain_age = runBrainage(PP_image_path)

        if MMSE_score is not None:
            risk_score = runPreAD(
                MMSE_score=MMSE_score,
                OG_image_path=OG_image_path,
                actual_age=actual_age,
                sex=sex
            )
        else:
            risk_score = None

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=(
                f"runPreAD 執行失敗\n"
                f"錯誤訊息: {str(e)}\n"
                f"參數資訊: MMSE={MMSE_score}, actual_age={actual_age}, sex={sex}, path={OG_image_path}"
            )
        )
    print(risk_score)
    # === 寫入預測結果 ===
    update_result = member_collection.update_one(
        {"id": member_id, "RecordList.record_id": record_id},
        {
            "$set": {
                "RecordList.$.brain_age": brain_age,
                "RecordList.$.risk_score": risk_score
            }
        }
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
    # === 驗證角色 ===
    decoded_token = jwt.decode(manager_token, SECRET_KEY, algorithms=["HS256"])
    user_role = decoded_token.get("role")
    if user_role != "manager":
        raise HTTPException(status_code=403, detail="此功能僅限醫生使用")

    # === 組合 record_id ===
    record_id = f"record{str(record_count).zfill(3)}"
    # === 查詢紀錄資料 ===
    result = member_collection.find_one(
        {"id": member_id},
        {"_id": 0, "RecordList": {"$elemMatch": {"record_id": record_id}}}
    )

    if not result or "RecordList" not in result or len(result["RecordList"]) == 0:
        raise HTTPException(status_code=404, detail="找不到指定的紀錄")

    record_data = result["RecordList"][0]
    folder_path = record_data["folder_path"]
    base_dir = os.path.dirname(os.path.abspath(__file__))
    folder_path =  os.path.join(base_dir,folder_path)

    if os.path.exists(os.path.join(folder_path, "preprocessing.nii.gz")):
        OG_image_path = os.path.join(folder_path, "preprocessing.nii.gz")
    else:
        raise HTTPException(status_code=404, detail="找不到前處理MRI檔案")
    
    try:
        folder_path = runSlice(OG_image_path,folder_path)
        return {"outputDirection" : folder_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"切片失敗: {str(e)}")

### 登出 ###
@router.post("/Logout")
def logout(token: str = Depends(oauth2_scheme)):
    # 將 Token 加入黑名單，讓它失效
    token_blacklist.add(token)
    return {"message": "登出成功，Token 已失效"}