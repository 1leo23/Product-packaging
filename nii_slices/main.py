import os
import tempfile
import base64
from io import BytesIO

import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware   # <== 新增 CORS
import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
from pymongo import MongoClient
from bson import ObjectId

# === 1. Atlas 連線字串 (請自行替換 <db_password> === #
MONGO_URI = (
    "mongodb+srv://forever60204:aaa09843@cluster0.mjnv5.mongodb.net/"
    "?retryWrites=true&w=majority&appName=Cluster0"
)
client = MongoClient(MONGO_URI)
db = client["my_database"]        # 指定/建立"my_database"
collection = db["nii_slices"]     # 指定/建立"nii_slices"

def store_slices_in_mongo(sag_b64: str, cor_b64: str, axi_b64: str) -> str:
    doc = {
        "sagittal_b64": sag_b64,
        "coronal_b64": cor_b64,
        "axial_b64": axi_b64
    }
    result = collection.insert_one(doc)
    return str(result.inserted_id)

def get_slices_from_mongo(doc_id: str):
    try:
        oid = ObjectId(doc_id)
    except:
        return None
    return collection.find_one({"_id": oid})

# === 2. 建立 FastAPI 應用程式 ===
app = FastAPI()

# === 3. CORS 設定: 允許 http://127.0.0.1:5500 來源 ===
origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_mid_slices(data_3d: np.ndarray):
    """ 取得三個方向的中間切片 """
    X, Y, Z = data_3d.shape
    mid_x = X // 2
    mid_y = Y // 2
    mid_z = Z // 2
    sagittal_slice = data_3d[mid_x, :, :]
    coronal_slice  = data_3d[:, mid_y, :]
    axial_slice    = data_3d[:, :, mid_z]
    return sagittal_slice, coronal_slice, axial_slice

def slice_to_base64(slice_2d: np.ndarray) -> str:
    """ 2D array → PNG → Base64 """
    plt.imshow(slice_2d.T, cmap='gray', origin='lower')
    plt.axis('off')
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
    plt.close()
    buf.seek(0)
    png_bytes = buf.getvalue()
    return base64.b64encode(png_bytes).decode('utf-8')

@app.post("/upload_nii/")
async def upload_nii(file: UploadFile = File(...)):
    """
    1. 接收.nii/.nii.gz (multipart/form-data)
    2. 寫入臨時檔後，用 nibabel 讀取
    3. 取三方向中間切片 → 轉成 Base64
    4. 存入 MongoDB → 回傳 document_id
    """
    file_bytes = await file.read()
    suffix = ".nii.gz" if file.filename.endswith(".nii.gz") else ".nii"

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        nii_img = nib.load(tmp_path, mmap=False)
        data_3d = nii_img.get_fdata()
    except Exception as e:
        os.remove(tmp_path)
        return {"error": f"無法讀取 NIfTI 檔: {e}"}
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    sag_2d, cor_2d, axi_2d = get_mid_slices(data_3d)
    sag_b64 = slice_to_base64(sag_2d)
    cor_b64 = slice_to_base64(cor_2d)
    axi_b64 = slice_to_base64(axi_2d)

    doc_id = store_slices_in_mongo(sag_b64, cor_b64, axi_b64)

    return {
        "document_id": doc_id,
        "message": f"上傳並處理三張切片成功 (檔名:{file.filename})"
    }

@app.get("/get_slices/{doc_id}")
def get_slices(doc_id: str):
    doc = get_slices_from_mongo(doc_id)
    if doc is None:
        return {"error": "找不到此文件或 doc_id 無效"}

    return {
        "sagittal_b64": doc.get("sagittal_b64"),
        "coronal_b64": doc.get("coronal_b64"),
        "axial_b64": doc.get("axial_b64")
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
