from fastapi import FastAPI
from routes import router  # 引入 routes.py
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# 註冊 API 路由
app.include_router(router)
app.mount("/images", StaticFiles(directory="C:/Users/User/Pictures/brain_image"), name="images")
app.mount("/images", StaticFiles(directory="C:/Users/User/Pictures/manager_profile"), name="images")
app.mount("/images", StaticFiles(directory="C:/Users/User/Pictures/member_profile"), name="images")
@app.get("/")
def home():
    return {"message": "API 正常運行中"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
