import os
import tempfile
from io import BytesIO

import uvicorn
from fastapi import FastAPI, File, UploadFile, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
from pymongo import MongoClient
from bson import ObjectId

# ========== 1. MongoDB 連線 ========== #
MONGO_URI = (
    "mongodb+srv://forever60204:aaa09843@cluster0.mjnv5.mongodb.net/"
    "?retryWrites=true&w=majority&appName=Cluster0"
)
client = MongoClient(MONGO_URI)
db = client["my_database"]
collection = db["nii_slices"]

# ========== 2. FastAPI + CORS ========== #
app = FastAPI()

origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 靜態檔案掛載：將 C:\API_Brain\id 資料夾掛載到 /files
app.mount("/files", StaticFiles(directory=r"C:\API_Brain\id"), name="files")


# ========== 工具函式 ========== #
def save_slice_as_png(slice_2d: np.ndarray, save_path: str):
    """
    用 matplotlib 將 2D 切片存成 PNG 檔。
    """
    plt.imshow(slice_2d.T, cmap='gray', origin='lower')
    plt.axis('off')
    plt.savefig(save_path, bbox_inches='tight', pad_inches=0)
    plt.close()

def get_sagittal_slices(data_3d: np.ndarray):
    X, Y, Z = data_3d.shape
    slices = []
    for x in range(X):
        slices.append(data_3d[x, :, :])
    return slices

def get_coronal_slices(data_3d: np.ndarray):
    X, Y, Z = data_3d.shape
    slices = []
    for y in range(Y):
        slices.append(data_3d[:, y, :])
    return slices

def get_axial_slices(data_3d: np.ndarray):
    X, Y, Z = data_3d.shape
    slices = []
    for z in range(Z):
        slices.append(data_3d[:, :, z])
    return slices


# ========== 3. 上傳API：只在DB存 id / folderPath / originalNii ========== #
@app.post("/upload_nii_png_local")
async def upload_nii_png_local(file: UploadFile = File(...)):
    """
    1) 接收 NIfTI (.nii/.nii.gz)
    2) nibabel 讀取 3D array
    3) 建立資料夾：C:\API_Brain\id\<doc_id>_<baseName>
       下再建立 Sagittal/Coronal/Axial 子資料夾
    4) 備份原始檔 => 命名 original.nii / original.nii.gz
    5) 每個切片存成 PNG 檔到對應子資料夾
    6) 在 MongoDB 中只存：
        - _id
        - folderPath
        - originalNii
    """
    original_name = file.filename
    base_name = original_name
    # 判斷是否為 .nii.gz
    is_gz = False
    if base_name.endswith(".nii.gz"):
        base_name = base_name[:-7]
        is_gz = True
    elif base_name.endswith(".nii"):
        base_name = base_name[:-4]

    file_bytes = await file.read()
    suffix = ".nii.gz" if is_gz else ".nii"

    # 先存到臨時檔
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        # 讀取 NIfTI
        nii_img = nib.load(tmp_path, mmap=False)
        data_3d = nii_img.get_fdata()
    except Exception as e:
        os.remove(tmp_path)
        return {"error": f"無法讀取 NIfTI 檔: {e}"}
    finally:
        # 稍後再刪temp
        pass

    doc_id_str = str(ObjectId())

    # 建立最上層資料夾
    root_dir = r"C:\API_Brain\id"
    folder_name = f"{doc_id_str}_{base_name}"
    doc_folder = os.path.join(root_dir, folder_name)
    sag_dir = os.path.join(doc_folder, "Sagittal")
    cor_dir = os.path.join(doc_folder, "Coronal")
    axi_dir = os.path.join(doc_folder, "Axial")
    os.makedirs(sag_dir, exist_ok=True)
    os.makedirs(cor_dir, exist_ok=True)
    os.makedirs(axi_dir, exist_ok=True)

    # 備份原始檔
    original_nii_name = "original" + suffix  # original.nii or original.nii.gz
    original_nii_path = os.path.join(doc_folder, original_nii_name)
    with open(original_nii_path, "wb") as out_f:
        out_f.write(file_bytes)

    # 生成三方向PNG
    sag_slices = get_sagittal_slices(data_3d)
    for i, slc in enumerate(sag_slices):
        png_path = os.path.join(sag_dir, f"sag_{i}.png")
        save_slice_as_png(slc, png_path)

    cor_slices = get_coronal_slices(data_3d)
    for i, slc in enumerate(cor_slices):
        png_path = os.path.join(cor_dir, f"cor_{i}.png")
        save_slice_as_png(slc, png_path)

    axi_slices = get_axial_slices(data_3d)
    for i, slc in enumerate(axi_slices):
        png_path = os.path.join(axi_dir, f"axi_{i}.png")
        save_slice_as_png(slc, png_path)

    # 刪除臨時檔
    if os.path.exists(tmp_path):
        os.remove(tmp_path)

    # 只存三欄: _id / folderPath / originalNii
    doc = {
        "_id": ObjectId(doc_id_str),
        "folderPath": doc_folder,
        "originalNii": original_nii_name
    }
    collection.insert_one(doc)

    return {
        "document_id": doc_id_str,
        "folderPath": doc_folder,
        "originalNii": original_nii_name,
        "message": f"切片PNG+原檔備份完畢",
        "num_slices": {
            "Sagittal": len(sag_slices),
            "Coronal": len(cor_slices),
            "Axial": len(axi_slices)
        }
    }


# ========== 4. 取得切片URL ========== #
@app.get("/get_slice_url/{doc_id}")
def get_slice_url(doc_id: str, plane: str, index: int):
    """
    回傳該 plane+index 的 PNG 路徑URL
    e.g. http://127.0.0.1:8000/files/{folderName}/Sagittal/sag_{index}.png
    """
    doc = collection.find_one({"_id": ObjectId(doc_id)})
    if not doc:
        return {"error": "找不到此文件或 doc_id 無效"}

    folderPath = doc["folderPath"]
    folderName = os.path.basename(folderPath)
    prefix = ""
    if plane.lower().startswith("sag"):
        prefix = "sag"
    elif plane.lower().startswith("cor"):
        prefix = "cor"
    elif plane.lower().startswith("axi"):
        prefix = "axi"
    else:
        return {"error": "plane參數錯誤"}

    url = f"http://127.0.0.1:8000/files/{folderName}/{plane}/{prefix}_{index}.png"
    return {"url": url}


# ========== 5. 檢視 folderPath / originalNii ========== #
@app.get("/get_folder_info/{doc_id}")
def get_folder_info(doc_id: str):
    doc = collection.find_one({"_id": ObjectId(doc_id)})
    if not doc:
        return {"error": "找不到此文件或 doc_id 無效"}

    return {
        "folderPath": doc["folderPath"],
        "originalNii": doc.get("originalNii", "unknown")
    }


# ========== 6. 運行程式 ========== #
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
