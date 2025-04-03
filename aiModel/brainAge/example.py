import os
import sys
import subprocess

def preprocessing(input_path):
    """使用 env_processing 環境執行 processing.py 並取得前處理結果的檔案路徑"""
    try:
        result = subprocess.run(
            f"conda run -n brainAge_pp_env python preprocessing.py {input_path}",
            capture_output=True,
            text=True,
            check=True
        )
        msg = result.stdout.strip()
        print("=====前處理執行狀況=====")
        print(msg)
        print("=====前處理執行結束=====:")
        
    except subprocess.CalledProcessError as e:
        print("前處理執行失敗：", e.stderr)
        return None

    # 預期 processing.py 將前處理後的檔案路徑輸出到 stdout
    processed_path = result.stdout.strip().split('\n')[-1]
    print("前處理結果檔案路徑:", processed_path)
    return processed_path

def runModel(processed_path):
    """使用 env_runmodel 環境執行 runModel.py 並取得預測的腦齡"""
    try:
        result = subprocess.run(
            ["conda", "run", "-n", "brainAge_runModel_env", "python", "runModel.py", processed_path],
            capture_output=True,
            text=True,
            check=True
        )
        msg = result.stdout.strip()
        print("=====腦齡預測執行狀況=====")
        print(msg)
        print("=====腦齡預測執行結束=====:")
    except subprocess.CalledProcessError as e:
        print("腦齡預測執行失敗：", e.stderr)
        return None

    try:
        # 預期 runModel.py 將預測結果輸出至 stdout
        brain_age = float(result.stdout.strip().split('\n')[-1])
    except ValueError:
        print("無法解析腦齡預測結果：", result.stdout)
        return None

    return brain_age

def main():
    # 檢查並驗證輸入檔案路徑
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

if __name__ == "__main__":
    main()
