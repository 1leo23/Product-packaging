from fastapi import FastAPI
from dotenv import dotenv_values
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware
from routes import router as member_router

config = dotenv_values(".env") #讀取.env

app = FastAPI() #設置主要的API

# 設置允許串接ip，等等前端才能連進來
origins = [
    "http://127.0.0.1:5500"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup") #連接DB
def startup_db_client():
    app.mongodb_client = MongoClient(config["ATLAS_URI"])
    app.database = app.mongodb_client[config["DB_NAME"]]
#https://cloud.mongodb.com/v2/67dac89a9232f91d8221876b#/metrics/replicaSet/67daca31450c303f4976a9db/explorer/member/member_data/find

@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()

# member_router是會員系統的router,若有需求可以設置多個router
app.include_router(member_router, tags=["membership"], prefix="/membership")