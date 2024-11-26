import numpy as np
import torch
import torchvision
import torch.nn
import torch.nn as nn
import torch.optim as optim

from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split

def create_test_loader(data_new, batch_size=512):
    """
    테스트 전용 DataLoader를 생성하는 함수.

    Args:
        data_path (str): 테스트 데이터 파일 경로 (Numpy 파일)
        batch_size (int): DataLoader의 배치 크기 (기본값 512)

    Returns:
        test_loader (DataLoader): 테스트 데이터 DataLoader
    """
    # 1. 데이터 로드
    # data = np.load(data_path, allow_pickle=True)
    data=data_new

    # 2. 데이터 입력 및 타겟 분리
    dataset_input = data[:, :, :-1]  # 입력 데이터 [N, 5, 20]
    dataset_target = data[:, :, -1:]  # 타겟 데이터 [N, 5, 1]

    # 3. Numpy 배열을 Torch 텐서로 변환
    dataset_input = torch.tensor(dataset_input, dtype=torch.float32)
    dataset_target = torch.tensor(dataset_target, dtype=torch.float32)

    # 4. TensorDataset으로 변환
    test_dataset = TensorDataset(dataset_input, dataset_target)

    # 5. DataLoader 생성
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    return test_loader
