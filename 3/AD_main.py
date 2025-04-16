from preprocess import n4,reg,skull,min_max_normalization,resample
from extractor import FE
import os
import numpy as np
import xgboost as xgb
import time
# 記錄開始時間=====================================================================
start_time = time.time()
#=================================================================================
original_image_path = r"C:\API_Brain\3\AD_Risk\50 years\AD 55 years\003_S_6264.nii"
fixed_path = r"C:\API_Brain\3\AD_Risk\mni_icbm152_t1_tal_nlin_sym_09a.nii"
deep_learning_model_path = r"C:\API_Brain\3\AD_Risk\DenseNet121_15epochs_accuracy0.83378_val0.58201.pth"
xgboost_model_path = r"C:\API_Brain\3\AD_Risk\xgboost_model.json"
#1.original_image_path為原始影像的路徑
#2.fixed_path為腦膜版的路徑
#3.deep_learning_model_path為深度學習模型
#4.xgboost_model_path為.json檔，xgboost機器學習的模型
#=================================================================================
print('請輸入以下資訊')
print('=='*50)
gender = input('請輸入性別(Female/Male):')
age = input("請輸入你的年齡: ")
mmse = input("請輸入你認知測驗分數: ")
#=================================================================================
params = {'F':0,'M':1}#Female:0/Male:1
patient_info = np.array([params[gender],age,mmse], dtype=np.float32)
#啟動前處理=================================================================================
corrected_image = n4(original_image_path)
warped_image = reg(corrected_image,fixed_path )
masked = skull(warped_image)
normalized_image = min_max_normalization(masked)
resize_image = resample(normalized_image)
#將resize_image輸入model=================================================================================
feature_vector = FE(deep_learning_model_path,resize_image)
#將特徵向量與gender、age、mmse合併並且輸入xgboost=================================================================================
xgboost_model = xgb.XGBClassifier()
xgboost_model.load_model(xgboost_model_path)
output = feature_vector.detach().cpu().numpy().flatten()
final_input = np.concatenate([output, patient_info]).reshape(1,-1)
xgb_output = xgboost_model.predict(final_input)
#結果顯示===========================================================================
print('=='*70)
label_mapping = {0: "AD(阿茲海默症)", 1: "CN(正常認知)", 2: "MCI(輕度認知障礙)"}
xgb_output_label = label_mapping.get(xgb_output[0], "未知類別")  
print(f"預測結果：{xgb_output_label}")
print('此系統僅供參考，並不能當作診斷證明')
end_time = time.time()
elapsed_time = end_time - start_time
print(f"程式執行時間：{elapsed_time:.2f} 秒")
