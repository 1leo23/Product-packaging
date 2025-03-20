from fastapi import APIRouter, HTTPException
from models import Member, LoginRequest, MemberQuery, UpdatePasswordRequest
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# 載入 .env 環境變數
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

# 連接 MongoDB
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# 創建 FastAPI 路由
router = APIRouter()

# 1️⃣ 註冊會員
@router.post("/member/register")
def register_member(member: Member):
    if collection.find_one({"id": member.id}):
        raise HTTPException(status_code=400, detail="該身份證字號已被註冊")

    birthdate = f"{member.yyyy}{member.mm:02d}{member.dd:02d}"
    member_data = {
        "id": member.id,
        "sex": member.sex,
        "name": member.name,
        "password": birthdate,  # 預設密碼
        "birthdate": birthdate
    }

    collection.insert_one(member_data)
    return {"message": "註冊成功", "default_password": birthdate}

# 2️⃣ 會員登入
@router.post("/member/signup")
def member_login(login_data: LoginRequest):
    user = collection.find_one({"id": login_data.id})
    
    if not user or user["password"] != login_data.password:
        raise HTTPException(status_code=401, detail="帳號或密碼錯誤")
    
    return {"message": "登入成功"}

# 3️⃣ 獲取會員資訊
@router.post("/member/info")
def get_member_info(query: MemberQuery):
    user = collection.find_one({"id": query.id}, {"_id": 0, "password": 0})

    if not user:
        raise HTTPException(status_code=404, detail="找不到該會員")
    
    return user

# 4️⃣ 變更密碼
@router.put("/member/update_password")
def update_password(request: UpdatePasswordRequest):
    user = collection.find_one({"id": request.id})

    if not user or user["password"] != request.old_password:
        raise HTTPException(status_code=401, detail="舊密碼錯誤")

    collection.update_one({"id": request.id}, {"$set": {"password": request.new_password}})
    return {"message": "密碼變更成功"}

# 5️⃣ 登出 (僅作為 API 結構，實際應用應該在前端刪除 Token)
@router.post("/member/logout")
def logout_member(query: MemberQuery):
    user = collection.find_one({"id": query.id})

    if not user:
        raise HTTPException(status_code=404, detail="找不到該會員")

    return {"message": "登出成功"}