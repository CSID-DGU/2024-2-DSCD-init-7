import torch
import torchvision
import torch.nn
import torch.nn as nn
import torch.optim as optim
import numpy as np
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
# 1. 데이터 로드 (np.load를 사용하여 불러오기)
data = np.load("/content/drive/MyDrive/dscd/sample2.npy")

# 예시: 타겟 데이터를 분리할 필요가 있을 경우 아래 코드처럼 나누기
# data가 (3000000, 5, 20) 크기이므로, 20개의 피처 중 일부를 타겟으로 사용할 수 있음
# 예를 들어 마지막 특성(인덱스 19)을 타겟으로 설정
dataset_input = data[:, :, :-1]  # [3000000, 5, 19], 입력 데이터
dataset_target = data[:, :, -1:]  # [3000000, 5, 1], 타겟 데이터

# Numpy 배열을 Torch 텐서로 변환
dataset_input = torch.tensor(dataset_input, dtype=torch.float32)
dataset_target = torch.tensor(dataset_target, dtype=torch.float32)

# 2. 훈련/검증 데이터셋 분리 (80% train, 20% validation)
train_input, val_input, train_target, val_target = train_test_split(
    dataset_input, dataset_target, test_size=0.2, random_state=42
)

# 3. 훈련 데이터셋 및 검증 데이터셋을 TensorDataset으로 변환
train_dataset = TensorDataset(train_input, train_target)
val_dataset = TensorDataset(val_input, val_target)

# 4. DataLoader로 미니배치 생성 (배치 크기 설정)
batch_size = 128
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

# 5. 각 데이터셋 크기 확인
print(f"Train dataset size: {len(train_dataset)}")
print(f"Validation dataset size: {len(val_dataset)}")

# # 크기 확인
# input_tensor, target_tensor = train_dataset[0]
# print(f"Input shape: {input_tensor.shape}")   # Input shape: torch.Size([5, 19])
# print(f"Target shape: {target_tensor.shape}") # Target shape: torch.Size([1])

# # 전체 데이터셋 크기 확인
# print(f"Dataset size: {len(train_dataset)}")