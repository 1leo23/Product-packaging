from fastapi import FastAPI
from routes import router  # 引入 routes.py

app = FastAPI()

# 註冊 API 路由
app.include_router(router)
@app.get("/")
def home():
    return {"message": "API 正常運行中"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
