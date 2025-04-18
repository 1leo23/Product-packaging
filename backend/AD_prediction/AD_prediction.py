import subprocess
import os
def runModel(original_image_path, MMSE_score, actual_age, sex):
<<<<<<< HEAD
=======
    base_dir = os.path.dirname(os.path.abspath(__file__))  # 指向 backend/BrainAge/
    script_path = os.path.join(base_dir, "runModel.py")
>>>>>>> 4e266181c9b3a874f2f2c9e935a1c4890fc1c3a9
    """使用 env_runmodel 環境執行 runModel.py 並取得預測的腦齡"""
    base_dir = os.path.dirname(os.path.abspath(__file__))  # 指向 backend/BrainAge/
    script_path = os.path.join(base_dir, "AD_prediction.py")
    try:
        result = subprocess.run(
            # 環境參數要改
<<<<<<< HEAD
            ["conda", "run", "-n", "brainAge_runModel_env", "python", script_path, original_image_path, str(MMSE_score), str(actual_age), sex],
=======
            [
                "conda", "run", "-n", "ADprediction_env", "python", script_path,
                str(original_image_path),
                str(MMSE_score),
                str(actual_age),
                str(sex)
            ],
>>>>>>> 4e266181c9b3a874f2f2c9e935a1c4890fc1c3a9
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        print("失智預測執行失敗：", e.stderr)
        return None

    try:
        # 預期 runModel.py 將預測結果輸出至 stdout
        AD_prediction = result.stdout.strip().split('\n')[-1]
    except ValueError:
        print("無法解析失智預測結果：", result.stdout)
        return None

    return AD_prediction
