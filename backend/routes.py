from fastapi import APIRouter, HTTPException, Depends, Form, UploadFile, File
from fastapi.security import OAuth2PasswordBearer
from models import Member, LoginRequest, MemberQuery, Manager, ManagerToken, Record
from pymongo import MongoClient
from dotenv import load_dotenv
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

### 管理員註冊 ###
# 本地存儲路徑
MANAGER_PROFILE_DIR = r"C:\Users\User\Pictures\manager_profile"
os.makedirs(MANAGER_PROFILE_DIR, exist_ok=True)
MEMBER_PROFILE_DIR = r"C:\Users\User\Pictures\member_profile"
os.makedirs(MEMBER_PROFILE_DIR, exist_ok=True)

### 取得醫生個人照 ###
@router.get("/manager/profile/{manager_id}")
def get_manager_profile(manager_id: str):
    manager = manager_collection.find_one({"id": manager_id})
    if not manager or "manager_profile_path" not in manager:
        raise HTTPException(status_code=404, detail="找不到該醫生或個人照")
    
    profile_path = manager["manager_profile_path"]
    if not os.path.exists(profile_path):
        raise HTTPException(status_code=404, detail="個人照不存在")

    return FileResponse(profile_path)

### 取得會員個人照 ###
@router.get("/member/profile/{member_id}")
def get_member_profile(member_id: str):
    member = member_collection.find_one({"id": member_id})
    if not member or "member_profile_path" not in member:
        raise HTTPException(status_code=404, detail="找不到該會員或個人照")
    
    profile_path = member["member_profile_path"]
    if not os.path.exists(profile_path):
        raise HTTPException(status_code=404, detail="個人照不存在")

    return FileResponse(profile_path)

# 管理員註冊
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

    # 存入資料庫
    manager_data = {
        "id": id,
        "password": password,
        "department": department,
        "name": name,
        "profile_image_path": profile_image_path,
        "numMembers": 0  # 初始沒有病人
    }
    manager_collection.insert_one(manager_data)

    return {"message": "醫師註冊成功"}


### 管理員登入 ###
@router.post("/manager/Signin")
def manager_signin(signin_data: LoginRequest):
    manager = manager_collection.find_one({"id": signin_data.id})

    if not manager or manager["password"] != signin_data.password:
        raise HTTPException(status_code=401, detail="帳號或密碼錯誤")
    
    manager_token = create_jwt_token({"id": signin_data.id})
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
    
    # 替換個人照 URL
    manager["manager_profile_path"] = f"/manager_profile/{manager_id}"
    
    return manager

### 取得成員列表 ###
@router.post("/manager/MemberList")
def get_member_list(manager_token: ManagerToken):
    manager_id = jwt.decode(manager_token.token, SECRET_KEY, algorithms=["HS256"])["id"]
    members = member_collection.find({"managerID": manager_id}, {"_id": 0, "password": 0})
    
    # 替換個人照 URL
    result = []
    for member in members:
        member["member_profile_path"] = f"/member_profile/{member['id']}"
        result.append(member)
    
    return result

# 成員登入
@router.post("/member/Signin")
def member_signin(signin_data: LoginRequest):
    member = member_collection.find_one({"id": signin_data.id})

    if not member:
        raise HTTPException(status_code=401, detail="帳號或密碼錯誤")

    # 產生應該匹配的密碼
    expected_password = f"{member['yyyy']}{str(member['mm']).zfill(2)}{str(member['dd']).zfill(2)}"

    if signin_data.password != expected_password:
        raise HTTPException(status_code=401, detail="帳號或密碼錯誤")

    member_token = create_jwt_token({"id": signin_data.id})
    return {"member_token": member_token, "message": f"{signin_data.id} 成功登入"}


# 成員拍攝紀錄
@router.post("/member/RecordsList")
def get_member_records(member_token: ManagerToken):
    member_id = jwt.decode(member_token.token, SECRET_KEY, algorithms=["HS256"])["id"]
    records = member_collection.find_one({"id": member_id}, {"_id": 0, "password": 0, "managerID": 0})

    if not records:
        raise HTTPException(status_code=404, detail="找不到該成員")

    return sorted(records.get("RecordList", []), key=lambda x: x["date"])

# 獲取成員基本資料
@router.post("/member/Info")
def get_member_info(member_token: ManagerToken, member_id: str):
    member = member_collection.find_one({"id": member_id}, {"_id": 0, "password": 0})
    
    if not member:
        raise HTTPException(status_code=404, detail="找不到該會員")
    
    # 替換個人照 URL
    member["member_profile_path"] = f"/member_profile/{member_id}"
    
    return member

# AI 計算
@router.post("/ai")
def ai_calculation(image_path: str):
    #假數據
    return {"brainAge": 45, "riskScore": 5}

# 上傳拍攝記錄
BRAIN_IMAGE_DIR = r"C:\Users\User\Pictures\brain_image"
os.makedirs(BRAIN_IMAGE_DIR, exist_ok=True)
@router.post("/upload/Record")
def upload_record(
    managerToken: str = Form(...),
    member_id: str = Form(...),
    date: str = Form(...),
    image_file: UploadFile = File(...)
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

    # **確認成員是否存在**
    member = member_collection.find_one({"id": member_id})
    if not member:
        raise HTTPException(status_code=404, detail="找不到該成員")

    # **取得 RecordList 數量**
    record_count = member.get("record_count", 0) + 1  # 取得當前記錄數量，+1 表示新的記錄

    # **檢查檔案格式**
    file_extension = image_file.filename.split(".")[-1]
    if file_extension not in ["nii", "gz"]:
        raise HTTPException(status_code=400, detail="檔案格式錯誤，僅支援 .nii 和 .nii.gz")

    # **設定 folder_path**
    member_folder = os.path.join(BRAIN_IMAGE_DIR, f"{member_id}_{record_count}")
    os.makedirs(member_folder, exist_ok=True)
    
    # **儲存檔案**
    if file_extension == "gz":
        original_image_path = os.path.join(member_folder, "original.nii.gz")
    else:
        original_image_path = os.path.join(member_folder, "original.nii")
    with open(original_image_path, "wb") as buffer:
        shutil.copyfileobj(image_file.file, buffer)

    # **計算實際年齡**
    birthdate = member["birthdate"]
    record = Record(
        member_id=member_id,
        date=date,
        original_image_path=original_image_path,
        folder_path=member_folder
    )
    record.compute_actual_age(birthdate)

    # **存入資料庫**
    member_collection.update_one(
        {"id": member_id},
        {
            "$push": {"RecordList": record.dict()},
            "$set": {"record_count": record_count}  # 更新 RecordList 記錄數量
        }
    )

    return {"message": "成功上傳紀錄"}


# 登出
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/Logout")
def logout(token: str = Depends(oauth2_scheme)):
    # 將 Token 加入黑名單，讓它失效
    token_blacklist.add(token)
    return {"message": "登出成功，Token 已失效"}

# Token 驗證中間件
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