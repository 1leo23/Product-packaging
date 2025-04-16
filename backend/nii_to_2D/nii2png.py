import ants
import numpy as np
def resample_to_isotropic_1mm(input_path):
    """
    將影像重取樣成 1 mm isotropic，保持相同物理範圍（會改變輸出影像維度！）
    interp_type=1 為線性插值
    """
    # 讀檔
    image = ants.image_read(input_path)
    
    # 以 voxel 為單位，將影像重取樣到 128×128×128
    resampled = ants.resample_image(
        image,
        (1, 1, 1),
        use_voxels=False,
        interp_type=1
    )

    # 儲存到指定路徑
    #ants.image_write(resampled, output_path)
    return resampled

import os
import matplotlib.pyplot as plt
import os
import numpy as np
import matplotlib.pyplot as plt
import sys

def make_slice(arr: np.ndarray, output_root: str):
    """
    將 3D 陣列沿三個方向切片，並對每張切片進行上下翻轉再轉置，分別輸出成 PNG 到三個資料夾:
      output_root/axial/*.png
      output_root/coronal/*.png
      output_root/sagittal/*.png
    """
    os.makedirs(output_root, exist_ok=True)

    directions = ['sagittal', 'coronal', 'axial']
    for axis, name in enumerate(directions):
        dir_path = os.path.join(output_root, name)
        os.makedirs(dir_path, exist_ok=True)

        num_slices = arr.shape[axis]
        for i in range(num_slices):
            if axis == 0:
                slice_img = arr[i, :, :]
            elif axis == 1:
                slice_img = arr[:, i, :]
            else:
                slice_img = arr[:, :, i]

            # 轉置 -> 上下 flip -> 左右 flip  
           
            slice_img = slice_img.T
            slice_img = np.flipud(slice_img)
            slice_img = np.fliplr(slice_img)

            out_png = os.path.join(dir_path, f"{i:03d}.png")
            plt.imsave(out_png, slice_img, cmap='gray')
        print(name+'切割完畢')

if __name__ == "__main__":
    input_path = sys.argv[1]
    output_dir = sys.argv[2]

    # 讀取並重取樣
    resampled = resample_to_isotropic_1mm(input_path)
    arr = resampled.numpy()

    # 產生切片
    make_slice(arr, output_dir)






