import os
import tempfile
import base64
from io import BytesIO

import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
from pymongo import MongoClient
from bson import ObjectId

# ========== 1. MongoDB Atlas 連線 ========== #
MONGO_URI = (
    "mongodb+srv://forever60204:aaa09843@cluster0.mjnv5.mongodb.net/"
    "?retryWrites=true&w=majority&appName=Cluster0"
)
client = MongoClient(MONGO_URI)
db = client["my_database"]          # 指定/建立 "my_database"
collection = db["nii_slices"]       # 指定/建立 "nii_slices"

# ========== 2. FastAPI + CORS ========== #
app = FastAPI()

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

# ========== 3. 工具函式 ========== #
def slice_2d_to_base64(slice_2d: np.ndarray) -> str:
    """將2D影像用matplotlib輸出PNG，再轉成Base64。"""
    plt.imshow(slice_2d.T, cmap='gray', origin='lower')
    plt.axis('off')
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
    plt.close()
    buf.seek(0)
    png_bytes = buf.getvalue()
    return base64.b64encode(png_bytes).decode('utf-8')

def get_sagittal_slices(data_3d: np.ndarray):
    """回傳Sagittal方向全部切片 (list of 2D numpy array)。"""
    X, Y, Z = data_3d.shape
    slices = []
    for x in range(X):
        slice_2d = data_3d[x, :, :]
        slices.append(slice_2d)
    return slices

def get_coronal_slices(data_3d: np.ndarray):
    """回傳Coronal方向全部切片。"""
    X, Y, Z = data_3d.shape
    slices = []
    for y in range(Y):
        slice_2d = data_3d[:, y, :]
        slices.append(slice_2d)
    return slices

def get_axial_slices(data_3d: np.ndarray):
    """回傳Axial方向全部切片。"""
    X, Y, Z = data_3d.shape
    slices = []
    for z in range(Z):
        slice_2d = data_3d[:, :, z]
        slices.append(slice_2d)
    return slices

# ========== 4. API: 上傳NIfTI => 存三方向全部切片 ========== #
@app.post("/upload_nii_3plane/")
async def upload_nii_3plane(file: UploadFile = File(...)):
    """
    1) 接收NIfTI (.nii/.nii.gz)
    2) 讀取後，對Sagittal, Coronal, Axial三方向，各取所有切片 => Base64陣列
    3) 一併存入同一個 document
    4) 回傳 doc_id
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

    # 取得三個方向的所有切片
    sag_slices = get_sagittal_slices(data_3d)  # list of 2D array
    cor_slices = get_coronal_slices(data_3d)
    axi_slices = get_axial_slices(data_3d)

    # 轉成Base64
    sag_b64_list = [slice_2d_to_base64(slc) for slc in sag_slices]
    cor_b64_list = [slice_2d_to_base64(slc) for slc in cor_slices]
    axi_b64_list = [slice_2d_to_base64(slc) for slc in axi_slices]

    # 寫入MongoDB
    doc = {
        "Sagittal": sag_b64_list,
        "Coronal": cor_b64_list,
        "Axial": axi_b64_list
    }
    result = collection.insert_one(doc)
    doc_id = str(result.inserted_id)

    return {
        "document_id": doc_id,
        "message": f"三方向全部切片已存 (檔名:{file.filename})",
        "num_slices": {
            "sagittal": len(sag_b64_list),
            "coronal": len(cor_b64_list),
            "axial": len(axi_b64_list)
        }
    }

# ========== 5. API: 取得該doc的三方向切片陣列 ========== #
@app.get("/get_3plane_slices/{doc_id}")
def get_3plane_slices(doc_id: str):
    doc = collection.find_one({"_id": ObjectId(doc_id)})
    if not doc:
        return {"error": "找不到此文件或 doc_id 無效"}

    return {
        "Sagittal": doc.get("Sagittal", []),
        "Coronal": doc.get("Coronal", []),
        "Axial": doc.get("Axial", [])
    }

# ========== 6. 運行程式 ========== #
if __name__ == "__main__":
   uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
