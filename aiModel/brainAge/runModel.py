import torch
import torch.nn as nn
import torch
import numpy as np
import os
import torch.nn.functional as F
import nibabel as nib

# 定義 sfcn 的基本塊
class BasicBlock(nn.Module): # Conv -> BN -> MaxPooling -> ReLU
    expansion = 1  # 通道擴展倍數

    def __init__(self, in_planes, out_planes, stride=1):
        super(BasicBlock, self).__init__()
        self.conv1 = nn.Conv3d(in_planes, out_planes, kernel_size=3, stride=stride,  padding=1)
        self.bn1 = nn.BatchNorm3d(out_planes)
        self.maxpool1 = nn.MaxPool3d(kernel_size=2, stride=2)

    def forward(self, x):
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.maxpool1(out)
        out = torch.relu(out)
        return out
# Define the full network architecture
class SFCN(nn.Module):
    def __init__(self, num_classes=1):
        super(SFCN, self).__init__()
        
        # Initial channel size
        self.in_planes = 1
        # Block 1 (Input channel: 1 -> Output channel: 32)
        self.layer1 = self._make_layer(BasicBlock, 32, num_blocks=1, stride=1)

        # Block 2 (Input channel: 32 -> Output channel: 64)
        self.layer2 = self._make_layer(BasicBlock, 64, num_blocks=1, stride=1) 

        # Block 3 (Input channel: 64 -> Output channel: 128)
        self.layer3 = self._make_layer(BasicBlock, 128, num_blocks=1, stride=1)

        # Block 4 (Input channel: 128 -> Output channel: 256)
        self.layer4 = self._make_layer(BasicBlock, 256, num_blocks=1, stride=1)

        # Block 5 (Input channel: 256 -> Output channel: 256)
        self.layer5 = self._make_layer(BasicBlock, 256, num_blocks=1, stride=1)

        # Stage 2 (Conv1*1 -> BN -> Relu)
        self.conv1 = nn.Conv3d(256, 64, kernel_size=1, stride=1, padding=0)
        self.bn1 = nn.BatchNorm3d(64)
        
        # Stage 3 (AvgPool -> Dropout -> Conv1*1)
        self.dropout = nn.Dropout(p=0.2)
        self.conv2 = nn.Conv3d(64, 50, kernel_size=1, stride=1, padding=0)
        self.softmax = nn.Softmax(dim=1)
    def _make_layer(self, block, out_planes, num_blocks, stride):
        layers = []
        layers.append(block(self.in_planes, out_planes, stride))
        self.in_planes = out_planes * block.expansion
        for _ in range(1, num_blocks):
            layers.append(block(self.in_planes, out_planes))
        return nn.Sequential(*layers)

    def forward(self, x):
        # Stage 1
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        x = self.layer5(x)
        # Stage 2
        x = self.conv1(x)
        x = self.bn1(x)
        x = torch.relu(x)
        # Stage 3
        x = F.adaptive_avg_pool3d(x, output_size=1)
        x = self.dropout(x)
        x = self.conv2(x)
        x = x.view(x.shape[0], 50)
        x = self.softmax(x)
        # 權重平均
        weights = torch.arange(1, 51, dtype=x.dtype, device=x.device).view(1, -1)
        x = torch.sum(x * weights, dim=1, keepdim=True)
        x = x * 2
        return x
    
def runModel(path):
    cnns=[None, None, None, None, None]
    pt_ls = os.listdir(r'models')
    for i in range(5):
        cnns[i] = SFCN(num_classes=1)
        pt_path = os.path.join(r'models',pt_ls[i])
        cnns[i].load_state_dict(torch.load(pt_path))
        cnns[i].eval()
    image = np.zeros((1,128,192,128),dtype=np.uint8)
    # 製作 numpy image
    data = nib.load(path)
    image = data.get_fdata()
    # 製作 torch image
    image_tensor = torch.from_numpy(image).to(torch.uint8)  # 儲存為 uint8
    # 製作 輸入檔
    inputs = image_tensor.to(torch.float32) / 255.0
    inputs = inputs.unsqueeze(0)
    inputs = inputs.unsqueeze(0)
    print(inputs.shape)
    # 組合評估
    ensemble_output = 0.0
    for model_i in range(5):
        outputs = cnns[model_i](inputs)
        ensemble_output += outputs.item()*0.2
    brainAge = ensemble_output
    print(f"腦齡：{brainAge}")
    return brainAge
runModel(r'D:\brainAgePrediction\Trajectory\aiModel\brainAge\ppResult\ADNI-sc-CN_I18211_90_F_.nii.gz')