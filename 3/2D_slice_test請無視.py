import os
import numpy as np
import nibabel as nib
import imageio

def reorient_and_save_slices(
    input_nii: str,
    output_dir: str,
    total_slices: int = 15
):
    """
    讀取指定的 NIfTI, reorient 成近似 RAS 後，
    分別切出 Sagittal, Coronal, Axial 的部分切片並存成 PNG。
    檔名均由 0~(total_slices-1).png 遞增。
    """

    # 1. 讀取並 reorient 成近似 RAS
    nii = nib.load(input_nii)
    ras_nii = nib.as_closest_canonical(nii)  # 調整軸向接近 RAS
    data_3d = ras_nii.get_fdata()

    # RAS 模式下: x=LR, y=PA, z=IS
    x_size, y_size, z_size = data_3d.shape

    # 2. 建立輸出資料夾，以及三個方向的子資料夾
    os.makedirs(output_dir, exist_ok=True)
    sag_dir = os.path.join(output_dir, "Sagittal")
    cor_dir = os.path.join(output_dir, "Coronal")
    axi_dir = os.path.join(output_dir, "Axial")
    os.makedirs(sag_dir, exist_ok=True)
    os.makedirs(cor_dir, exist_ok=True)
    os.makedirs(axi_dir, exist_ok=True)

    # 3. 定義一個通用函式，用於讀取切片、正規化、翻轉/旋轉、輸出 PNG
    def save_slice(slice_2d: np.ndarray, out_path: str, plane: str):
        """
        將 slice_2d 正規化到 0~255，並依 plane 決定翻轉/旋轉方式，最後存成 PNG。
        """
        # 正規化到 0~255
        min_val = slice_2d.min()
        ptp_val = slice_2d.ptp()
        if ptp_val > 0:
            slice_norm = (slice_2d - min_val) / ptp_val
        else:
            slice_norm = slice_2d - min_val
        slice_uint8 = (slice_norm * 255).astype(np.uint8)

        # 根據 plane 嘗試做一些翻轉/旋轉
        # 以下只是範例，實際需依你想要的顯示習慣微調
        plane_lower = plane.lower()
        if plane_lower == 'sag':
            # Sagittal 建議先轉置再上下翻轉
            slice_display = np.flipud(slice_uint8.T)
        elif plane_lower == 'cor':
            # Coronal 也可嘗試 rot90、flipud 等
            slice_display = np.flipud(slice_uint8.T)
        elif plane_lower == 'axi':
            # Axial 常見：轉置 + flipud
            slice_display = np.flipud(slice_uint8.T)
        else:
            slice_display = slice_uint8

        # 寫入 PNG 檔
        imageio.imwrite(out_path, slice_display)

    # 4. 寫一個小工具函式，方便抽取某軸
    #    假設要從某個範圍開始擷取 total_slices 張
    #    也可以改成從中間開始切或其他規則
    def extract_plane(data, plane_name: str, plane_dir: str, start_idx: int, max_idx: int):
        """
        :param plane_name: 'sag', 'cor', or 'axi'
        :param plane_dir: 該 plane 的輸出資料夾
        :param start_idx: 初始切片位置
        :param max_idx: 該方向可用的最大索引
        """
        end_idx = min(start_idx + total_slices, max_idx)
        for i in range(start_idx, end_idx):
            # 根據 plane 取 slice
            if plane_name == 'sag':     # x 軸
                slice_2d = data[i, :, :]
            elif plane_name == 'cor':   # y 軸
                slice_2d = data[:, i, :]
            elif plane_name == 'axi':   # z 軸
                slice_2d = data[:, :, i]
            else:
                continue
            out_name = f"{i - start_idx}.png"  # 檔名從 0,1,2...
            out_path = os.path.join(plane_dir, out_name)
            save_slice(slice_2d, out_path, plane_name)

    # 先定義要從「最中間」開始各取 15 張，如想從最前面取就設 start_idx=0
    sag_mid = x_size // 2 - total_slices // 2
    cor_mid = y_size // 2 - total_slices // 2
    axi_mid = z_size // 2 - total_slices // 2
    if sag_mid < 0: sag_mid = 0
    if cor_mid < 0: cor_mid = 0
    if axi_mid < 0: axi_mid = 0

    # 5. 逐個方向擷取
    extract_plane(data_3d, 'sag', sag_dir, sag_mid, x_size)
    extract_plane(data_3d, 'cor', cor_dir, cor_mid, y_size)
    extract_plane(data_3d, 'axi', axi_dir, axi_mid, z_size)

    print("完成：Sagittal, Coronal, Axial 切片共存入：", output_dir)


def main():
    input_nii = r"C:\API_Brain\id\67fe70f3cce4619650a715fe_003_S_4441\original.nii"
    output_dir = r"C:\API_Brain\id"

    # 你可以在這邊調整 total_slices, 例如一次要 10 張或 20 張
    reorient_and_save_slices(input_nii, output_dir, total_slices=15)


if __name__ == "__main__":
    main()
