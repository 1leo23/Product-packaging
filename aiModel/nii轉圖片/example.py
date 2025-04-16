import os
import sys
import subprocess

def run_nii2png(input_path, output_dir):
    """使用指定 Conda 環境執行 nii2png.py，傳入輸入檔與輸出資料夾"""
    try:
        result = subprocess.run(
            f"conda run -n brainAge_pp_env python nii2png.py {input_path} {output_dir}",
            capture_output=True,
            text=True,
            check=True
        )
        msg = result.stdout.strip()
        print("===== 切片執行狀況 =====")
        print(msg)
        print("===== 切片執行結束 =====")
        
    except subprocess.CalledProcessError as e:
        print("切片執行失敗：", e.stderr)
        return None

    print("切片結果已儲存於:", output_dir)
    return output_dir

run_nii2png('ADNI-sc-CN_I18211_90_F_.nii.gz','slice')