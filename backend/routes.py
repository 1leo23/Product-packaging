from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from models import Member, LoginRequest, MemberQuery, UpdatePasswordRequest, Manager, ManagerToken, Record
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import jwt
import datetime

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

# 管理員註冊
@router.post("/manager/Manager_Signup")
def manager_signup(manager: Manager):
    if manager_collection.find_one({"id": manager.id}):
        raise HTTPException(status_code=400, detail="該醫生編號已註冊")

    manager_data = manager.dict()
    manager_data["numMembers"] = 0  # 初始沒有病人
    manager_collection.insert_one(manager_data)

    return {"message": "醫師註冊成功"}

# 管理員登入
@router.post("/manager/Signin")
def manager_signin(signin_data: LoginRequest):
    manager = manager_collection.find_one({"id": signin_data.id})

    if not manager or manager["password"] != signin_data.password:
        raise HTTPException(status_code=401, detail="帳號或密碼錯誤")
    
    manager_token = create_jwt_token({"id": signin_data.id})
    return {"manager_token": manager_token, "message": f"{signin_data.id} 成功登入"}

# 會員註冊
@router.post("/manager/Member_Signup")
def member_signup(member: Member, manager_token: ManagerToken):
    manager_id = jwt.decode(manager_token.token, SECRET_KEY, algorithms=["HS256"])["id"]
    if not manager_collection.find_one({"id": manager_id}):
        raise HTTPException(status_code=401, detail="無效的管理員 Token")

    if member_collection.find_one({"id": member.id}):
        raise HTTPException(status_code=400, detail="該身份證字號已被註冊")

    # 自動設定密碼
    member.generate_password()

    member_data = member.dict()
    member_data["managerID"] = manager_id

    manager_collection.update_one({"id": manager_id}, {"$inc": {"numMembers": 1}})

    return {"message": "成員註冊成功", "default_password": member.password}

# 獲取管理員資料
@router.post("/manager/Info")
def get_manager_info(manager_token: ManagerToken):
    manager_id = jwt.decode(manager_token.token, SECRET_KEY, algorithms=["HS256"])["id"]
    manager = manager_collection.find_one({"id": manager_id}, {"_id": 0, "password": 0})

    if not manager:
        raise HTTPException(status_code=404, detail="找不到該管理員")
    
    return manager

# 獲取成員資料
@router.post("/manager/MemberList")
def get_member_list(manager_token: ManagerToken):
    manager_id = jwt.decode(manager_token.token, SECRET_KEY, algorithms=["HS256"])["id"]
    members = member_collection.find({"managerID": manager_id}, {"_id": 0, "password": 0})

    return [member for member in members]

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
        raise HTTPException(status_code=404, detail="找不到該成員")
    
    return member

# AI 計算
@router.post("/ai")
def ai_calculation(image_path: str):
    #假數據
    return {"brainAge": 45, "riskScore": 5}

# 上傳拍攝記錄
@router.post("/upload/Record")
def upload_record(record: Record):
    member = member_collection.find_one({"id": record.member_id}, {"_id": 0, "yyyy": 1, "mm": 1, "dd": 1})

    if not member:
        raise HTTPException(status_code=404, detail="找不到該成員")

    # 將會員出生年月日轉換為 YYYY-MM-DD 格式
    birthdate = f"{member['yyyy']}-{str(member['mm']).zfill(2)}-{str(member['dd']).zfill(2)}"

    # 計算 actual_age
    record.compute_actual_age(birthdate)

    # 更新紀錄
    member_collection.update_one({"id": record.member_id}, {"$push": {"RecordList": record.dict()}})
    
    return {"message": "成功上傳紀錄", "actual_age": record.actual_age}


# 登出
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
token_blacklist = set()
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