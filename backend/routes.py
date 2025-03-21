from fastapi import APIRouter, HTTPException, Depends
from models import Member, Manager, LoginRequest, MemberQuery
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import jwt
import datetime

# 載入環境變數
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")
MEMBER_COLLECTION = os.getenv("MEMBER_COLLECTION")
MANAGER_COLLECTION = os.getenv("MANAGER_COLLECTION")
SECRET_KEY = os.getenv("SECRET_KEY")

# 連接 MongoDB
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
members_collection = db[MEMBER_COLLECTION]
managers_collection = db[MANAGER_COLLECTION]

# 創建 FastAPI 路由
router = APIRouter()

### 🔹 產生 JWT Token ###
def create_token(data: dict):
    payload = data.copy()
    payload.update({"exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)})
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

### 🔹 解析 Token ###
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token 已過期")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="無效的 Token")

### 🔹 新增成員 (/manager/memberRegister) ###
@router.post("/manager/memberRegister")
def register_member(member: Member):
    if members_collection.find_one({"id": member.id}):
        raise HTTPException(status_code=400, detail="該身份證字號已被註冊")

    birthdate = f"{member.yyyy}{member.mm:02d}{member.dd:02d}"
    member_data = member.dict()
    member_data["password"] = birthdate  # 預設密碼

    members_collection.insert_one(member_data)
    return {"message": "成員註冊成功"}

### 🔹 新增管理員 (/manager/managerRegister) ###
@router.post("/manager/managerRegister")
def register_manager(manager: Manager):
    if managers_collection.find_one({"id": manager.id}):
        raise HTTPException(status_code=400, detail="該醫師編號已被註冊")

    managers_collection.insert_one(manager.dict())
    return {"message": "醫師註冊成功"}

### 🔹 管理員登入 (/manager/signin) ###
@router.post("/manager/signin")
def manager_login(login_data: LoginRequest):
    manager = managers_collection.find_one({"id": login_data.id})

    if not manager or manager["password"] != login_data.password:
        raise HTTPException(status_code=401, detail="帳號或密碼錯誤(ID預設為身份證字號，密碼預設為8位之西元生日)")

    token = create_token({"id": manager["id"], "role": "manager"})
    return {"managerToken": token}

### 🔹 獲取管理員資料 (/manager/info) ###
@router.get("/manager/info")
def get_manager_info(token: str = Depends(verify_token)):
    manager = managers_collection.find_one({"id": token["id"]}, {"_id": 0, "password": 0})
    if not manager:
        raise HTTPException(status_code=404, detail="找不到該管理員")
    return manager

### 🔹 獲取成員列表 (/manager/memberList) ###
@router.get("/manager/memberList")
def get_member_list(token: str = Depends(verify_token)):
    members = list(members_collection.find({}, {"_id": 0, "password": 0}))
    return {"members": members}

### 🔹 成員登入 (/member/signin) ###
@router.post("/member/signin")
def member_login(login_data: LoginRequest):
    member = members_collection.find_one({"id": login_data.id})

    if not member or member["password"] != login_data.password:
        raise HTTPException(status_code=401, detail="帳號或密碼錯誤")

    token = create_token({"id": member["id"], "role": "member"})
    return {"memberToken": token, "message": f"{member['name']} 成功登入"}

### 🔹 獲取成員基本資料 (/member/info) ###
@router.get("/member/info")
def get_member_info(member_id: str, token: str = Depends(verify_token)):
    member = members_collection.find_one({"id": member_id}, {"_id": 0, "password": 0})
    if not member:
        raise HTTPException(status_code=404, detail="找不到該成員")
    return member

### 🔹 登出 (/logout) ###
@router.post("/logout")
def logout():
    return {"message": "登出成功"}
