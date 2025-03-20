from fastapi import FastAPI
from routes import router
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 創建 FastAPI 應用
app = FastAPI()

# 註冊路由
app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "會員管理 API 啟動成功"}