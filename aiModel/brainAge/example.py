import os
import sys

# 假設前處理程式碼在 preprocessing.py 中
from preprocessing import preprocessing

# 假設模型程式碼在 model.py 中
from runModel import runModel

def main():
    # 獲取並驗證輸入路徑
    path = r"D:\brainAgePrediction\Trajectory\aiModel\brainAge\samples\ADNI-sc-CN_I18211_90_F_.nii.gz"
    input_path = os.path.abspath(path)
    if not os.path.exists(input_path):
        print(f"錯誤: 檔案 {input_path} 不存在")
        sys.exit(1)
    if not input_path.endswith('.nii.gz'):
        print("錯誤: 輸入檔案必須是 .nii.gz 格式")
        sys.exit(1)

    print(f"開始處理檔案: {input_path}")
    
    # 第一步：執行前處理
    print("執行前處理...")
    preprocessed_path = preprocessing(input_path)
    print(preprocessed_path)
    if preprocessed_path is None or not os.path.exists(preprocessed_path):
        print("前處理失敗，程式終止")
        sys.exit(1)
    print(f"前處理完成，結果保存至: {preprocessed_path}")

    # 第二步：執行腦齡預測
    print("執行腦齡預測...")
    brain_age = runModel(preprocessed_path)
    if brain_age is None:
        print("腦齡預測失敗，程式終止")
        sys.exit(1)
    
    # 輸出結果
    print(f"預測腦齡: {brain_age:.2f} 歲")
    return brain_age

main()