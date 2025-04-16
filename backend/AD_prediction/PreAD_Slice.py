import os
import tempfile
import time
import shutil

import uvicorn
from fastapi import FastAPI, File, UploadFile, Query, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
from pymongo import MongoClient
from bson import ObjectId

import xgboost as xgb

# 載入預處理與特徵擷取函式
from preprocess import n4, reg, skull, min_max_normalization, resample
from extractor import FE

# ========== 1. MongoDB 連線 ==========
MONGO_URI = (
    "mongodb+srv://forever60204:aaa09843@cluster0.mjnv5.mongodb.net/"
    "?retryWrites=true&w=majority&appName=Cluster0"
)
client = MongoClient(MONGO_URI)
db = client["my_database"]
collection = db["nii_slices"]

# ========== 2. FastAPI + CORS ==========
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

# 靜態檔案掛載（請確認資料夾路徑正確）
app.mount("/files", StaticFiles(directory=r"C:\API_Brain\id"), name="files")


# ========== 3. 工具函式：翻轉/旋轉修正 + 儲存 PNG ==========
def save_slice_2d(slice_2d: np.ndarray, out_path: str, plane: str):
    """
    將 slice_2d 正規化為 [0,255] 的 uint8，然後依 plane 做翻轉/轉置，最後存成 PNG。
    """
    import imageio
    
    # 1) 正規化
    min_val = slice_2d.min()
    ptp_val = slice_2d.ptp()
    if ptp_val > 0:
        slice_norm = (slice_2d - min_val) / ptp_val
    else:
        slice_norm = slice_2d - min_val
    slice_uint8 = (slice_norm * 255).astype(np.uint8)
    
    # 2) 翻轉/旋轉（預設寫法，可依需要再調整）
    plane_lower = plane.lower()
    if plane_lower.startswith('axi'):
        # Axial：常見做法是先轉置，再垂直翻轉
        slice_display = np.flipud(slice_uint8.T)
    elif plane_lower.startswith('cor'):
        # Coronal：同樣先轉置再翻轉
        slice_display = np.flipud(slice_uint8.T)
    elif plane_lower.startswith('sag'):
        # Sagittal：也嘗試先轉置再翻轉
        slice_display = np.flipud(slice_uint8.T)
    else:
        slice_display = slice_uint8
    
    # 寫入 PNG
    imageio.imwrite(out_path, slice_display)


def extract_middle_50_slices(data_3d: np.ndarray, plane: str, base_name: str, output_dir: str):
    """
    針對指定 plane（'Sagittal', 'Coronal', 'Axial'），
    取該方向「中間 50 張」切片並輸出成 PNG 檔名： base_name_0.png, base_name_1.png, ...
    若該維度小於 50，則盡量取全部。
    """
    plane_lower = plane.lower()
    x_size, y_size, z_size = data_3d.shape

    if plane_lower.startswith('sag'):
        # x 維
        max_index = x_size
        get_slice = lambda i: data_3d[i, :, :]
    elif plane_lower.startswith('cor'):
        # y 維
        max_index = y_size
        get_slice = lambda i: data_3d[:, i, :]
    elif plane_lower.startswith('axi'):
        # z 維
        max_index = z_size
        get_slice = lambda i: data_3d[:, :, i]
    else:
        raise ValueError("plane參數錯誤: " + plane)

    # 中間 50 張
    if max_index <= 50:
        # 維度小於等於 50，全部都取
        start_idx = 0
        end_idx = max_index
    else:
        # 取中間 50
        mid_start = (max_index - 50) // 2
        start_idx = mid_start
        end_idx = mid_start + 50

    os.makedirs(output_dir, exist_ok=True)

    slice_count = 0
    for i in range(start_idx, end_idx):
        slice_2d = get_slice(i)
        png_name = f"{base_name}_{slice_count}.png"  # 0-based 檔名
        out_path = os.path.join(output_dir, png_name)
        save_slice_2d(slice_2d, out_path, plane)
        slice_count += 1
    
    return slice_count


# ========== 4. 上傳 API：重新導向成 RAS，切三方向中間 50 張 ==========
@app.post("/upload_nii_png_local")
async def upload_nii_png_local(
    file: UploadFile = File(...),
    sex: str = Form(...),    
    age: int = Form(...),    
    mmse: int = Form(...),   
):
    """
    1) 接收 NIfTI 檔，讀取後 as_closest_canonical => 近似 RAS (mmap=False)。
    2) 對 Sagittal, Coronal, Axial 各取「中間 50 張」並 0-based 命名存成 PNG。
    3) 將檔案和補充資訊存入 MongoDB。
    4) 最後刪除臨時檔案時，採用 del + time.sleep 避免 WinError 32。
    """
    original_name = file.filename
    base_name = original_name
    is_gz = False
    if base_name.endswith(".nii.gz"):
        base_name = base_name[:-7]
        is_gz = True
    elif base_name.endswith(".nii"):
        base_name = base_name[:-4]

    file_bytes = await file.read()
    suffix = ".nii.gz" if is_gz else ".nii"

    # === 1. 先將上傳檔案寫入一個臨時檔 ===
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    # 嘗試讀取 NIfTI 並 reorient
    try:
        # 讀檔時加上 mmap=False，避免持續對檔案產生占用
        nii_obj = nib.load(tmp_path, mmap=False)
        nii_ras = nib.as_closest_canonical(nii_obj)
        data_3d = nii_ras.get_fdata()
        del nii_obj  # 顯式釋放 nibabel 物件
    except Exception as e:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        return {"error": f"無法讀取 NIfTI 檔: {e}"}

    doc_id_str = str(ObjectId())
    root_dir = r"C:\API_Brain\id"
    folder_name = f"{doc_id_str}_{base_name}"
    doc_folder = os.path.join(root_dir, folder_name)

    sag_dir = os.path.join(doc_folder, "Sagittal")
    cor_dir = os.path.join(doc_folder, "Coronal")
    axi_dir = os.path.join(doc_folder, "Axial")
    os.makedirs(sag_dir, exist_ok=True)
    os.makedirs(cor_dir, exist_ok=True)
    os.makedirs(axi_dir, exist_ok=True)

    # === 2. 備份原始檔 (非臨時檔) ===
    original_nii_name = "original" + suffix
    original_nii_path = os.path.join(doc_folder, original_nii_name)
    with open(original_nii_path, "wb") as out_f:
        out_f.write(file_bytes)

    # === 3. 執行三方向的「中間 50 張」切片 ===
    sag_count = extract_middle_50_slices(data_3d, plane="Sagittal",
                                         base_name="sag", output_dir=sag_dir)
    cor_count = extract_middle_50_slices(data_3d, plane="Coronal",
                                         base_name="cor", output_dir=cor_dir)
    axi_count = extract_middle_50_slices(data_3d, plane="Axial",
                                         base_name="axi", output_dir=axi_dir)

    # 確保所有對 data_3d 的操作已完成後，再刪除臨時檔
    if os.path.exists(tmp_path):
        # 若仍擔心 Windows 時序問題，可加 0.1秒延遲或重試機制
        time.sleep(0.1)
        try:
            os.remove(tmp_path)
        except PermissionError:
            pass  # or do a retry if needed

    # === 4. 寫入 MongoDB ===
    doc = {
        "_id": ObjectId(doc_id_str),
        "folderPath": doc_folder,
        "originalNii": original_nii_name,
        "sex": sex,
        "age": age,
        "mmse": mmse,
        "slices": {
            "Sagittal": sag_count,
            "Coronal": cor_count,
            "Axial": axi_count
        }
    }
    collection.insert_one(doc)

    return {
        "document_id": doc_id_str,
        "folderPath": doc_folder,
        "originalNii": original_nii_name,
        "message": "切片完成：三方向各中間50張(若不足則全取)，備份與補充資料已存入。",
        "num_slices": {
            "Sagittal": sag_count,
            "Coronal": cor_count,
            "Axial": axi_count
        }
    }


# ========== 5. 取得切片 URL ==========
@app.get("/get_slice_url/{doc_id}")
def get_slice_url(doc_id: str, plane: str, index: int):
    """
    依傳入 plane ('Sagittal','Coronal','Axial') + index 取得 PNG 路徑，
    其中 index 對應 'xxx_index.png'。
    """
    doc = collection.find_one({"_id": ObjectId(doc_id)})
    if not doc:
        return {"error": "找不到此文件或 doc_id 無效"}

    folderPath = doc["folderPath"]
    folderName = os.path.basename(folderPath)

    plane_lower = plane.lower()
    sub_folder = ""
    prefix = ""
    if plane_lower.startswith("sag"):
        sub_folder = "Sagittal"
        prefix = "sag"
    elif plane_lower.startswith("cor"):
        sub_folder = "Coronal"
        prefix = "cor"
    elif plane_lower.startswith("axi"):
        sub_folder = "Axial"
        prefix = "axi"
    else:
        return {"error": "plane參數錯誤"}

    png_name = f"{prefix}_{index}.png"  # e.g. sag_0.png
    url = f"http://127.0.0.1:8000/files/{folderName}/{sub_folder}/{png_name}"
    return {"url": url}


# ========== 6. AD 預測 API (示範) ==========
@app.get("/predict_ad/{doc_id}")
def predict_ad(doc_id: str):
    """
    若已經在 MongoDB 中有 prediction 欄位，則直接回傳；否則執行預測。
    """
    doc = collection.find_one({"_id": ObjectId(doc_id)})
    if not doc:
        return {"error": "找不到此文件或 doc_id 無效"}

    # 先檢查資料庫裡是否已有預測結果
    if "prediction" in doc:
        return {"prediction": doc["prediction"]}

    # ========== 1. 取得原始檔路徑 ==========
    folder_path = doc["folderPath"]
    original_nii_name = doc["originalNii"]
    original_image_path = os.path.join(folder_path, original_nii_name)

    # ========== 2. 取得病人資訊，將 F/M 轉為 Female/Male ==========
    sex_val = doc.get("sex", "F")  # 預設給 "F"
    if sex_val.upper() == "F":
        gender = "Female"
    elif sex_val.upper() == "M":
        gender = "Male"
    else:
        gender = "Female"  # 如果有意料外的值就當成 Female

    age = doc.get("age", 0)
    mmse = doc.get("mmse", 0)
    params = {"Female": 0, "Male": 1}
    patient_info = np.array([params.get(gender, 0), age, mmse], dtype=np.float32)

    # ========== 3. 執行預處理與推論 ==========
    fixed_path = r"C:\API_Brain\3\AD_Risk\mni_icbm152_t1_tal_nlin_sym_09a.nii"
    deep_learning_model_path = r"C:\API_Brain\3\AD_Risk\DenseNet121_15epochs_accuracy0.83378_val0.58201.pth"
    xgboost_model_path = r"C:\API_Brain\3\AD_Risk\xgboost_model.json"

    corrected_image = n4(original_image_path)
    warped_image = reg(corrected_image, fixed_path)
    masked = skull(warped_image)
    normalized_image = min_max_normalization(masked)
    resize_image = resample(normalized_image)

    feature_vector = FE(deep_learning_model_path, resize_image)
    output = feature_vector.detach().cpu().numpy().flatten()
    final_input = np.concatenate([output, patient_info]).reshape(1, -1)

    xgboost_model = xgb.XGBClassifier()
    xgboost_model.load_model(xgboost_model_path)
    xgb_output = xgboost_model.predict(final_input)

    label_mapping = {0: "AD(阿茲海默症)", 1: "CN(正常認知)", 2: "MCI(輕度認知障礙)"}
    xgb_output_label = label_mapping.get(xgb_output[0], "未知類別")

    # ========== 4. 寫入資料庫 ==========
    collection.update_one({"_id": ObjectId(doc_id)}, {"$set": {"prediction": xgb_output_label}})

    return {"prediction": xgb_output_label}



# ========== 7. 運行程式 ==========
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
