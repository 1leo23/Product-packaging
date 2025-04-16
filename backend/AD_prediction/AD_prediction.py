import subprocess
def runModel(folder_path, original_image_path, MMSE_score, actual_age, sex):
    """使用 env_runmodel 環境執行 runModel.py 並取得預測的腦齡"""
    try:
        result = subprocess.run(
            # 環境參數要改
            ["conda", "run", "-n", "brainAge_runModel_env", "python", "runModel.py", folder_path, original_image_path, MMSE_score, actual_age, sex],
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        print("失智預測執行失敗：", e.stderr)
        return None

    try:
        # 預期 runModel.py 將預測結果輸出至 stdout
        AD_prediction = float(result.stdout.strip().split('\n')[-1])
    except ValueError:
        print("無法解析失智預測結果：", result.stdout)
        return None

    return AD_prediction
