import torch
import torchvision
import torch.nn
import torch.nn as nn
import torch.optim as optim
import numpy as np
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from datapreprocess import data, dataset_input, dataset_target, train_input, val_input, train_target, val_target, train_dataset, val_dataset, train_loader, val_loader
from algorithm import TeamTransformer

## colab 사용 시
# from google.colab import drive
# drive.mount('/content/drive')
# import os

# # 바꿀 디렉토리 설정 (예: "/path/to/your/directory")
# new_directory = "/content/drive/MyDrive/dscd"

# # 작업 디렉토리 변경
# os.chdir(new_directory)

# # 변경된 작업 디렉토리 확인
# print("Changed working directory to:", os.getcwd())

# # cuda 사용가능 여부 확인
# torch.cuda.is_available()

#cuda
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# 하이퍼파라미터 설정
# 1. 데이터 관련
embedding_dim = 19  # 각 팀원의 임베딩 크기
seq_len = 5  # 팀원 조합 크기
output_dim = 1  # 예측할 점수 (연속적인 값)

# 2. 모델 관련
n_heads = 1  # 멀티헤드 어텐션의 헤드 수 (embedding_dim의 약수로 설정)
n_layers = 3  # 트랜스포머 인코더 레이어 수 (모델의 깊이를 적절하게 설정)
hidden_dim = 64  # 피드포워드 네트워크의 히든 레이어 크기 (embedding_dim보다 크게 설정하여 모델 용량 증가)
dropout_rate = 0.2  # 드롭아웃 비율 (오버피팅 방지를 위해 설정)
epochs = 5

# 모델 초기화
model = TeamTransformer(embedding_dim, n_heads, hidden_dim, n_layers, output_dim, dropout_rate).to(device)

# 손실 함수 및 옵티마이저 설정
criterion = nn.MSELoss()  # 연속적인 점수 예측이므로 MSE 사용
optimizer = optim.Adam(model.parameters(), lr=0.001)



# 손실 기록 리스트
train_losses = []
val_losses = []
# transformer_out 값을 저장할 리스트
transformer_outputs = []  # 각 배치의 transformer_out을 저장할 리스트
# 학습 및 검증 루프
for epoch in range(epochs):
    # 각 에포크마다 새로운 리스트로 초기화 (각 에포크별로 그래프를 그리기 위함)
    epoch_train_losses = []  # 에포크별 훈련 배치 손실 리스트
    epoch_val_losses = []    # 에포크별 검증 배치 손실 리스트

    model.train()
    total_train_loss = 0  # 훈련 손실 초기화
    total_val_loss = 0    # 검증 손실 초기화

    # Training Loop (훈련 루프)
    for batch_idx, (batch_inputs, batch_targets) in enumerate(train_loader):
        batch_inputs, batch_targets = batch_inputs.to(device), batch_targets.to(device)
        optimizer.zero_grad()  # 이전 기울기 초기화

      # 모델에 배치 입력 후 출력 계산
        output, transformer_out = model(batch_inputs)  # transformer_out 추가

        # transformer_out 저장 (필요에 따라 배치 단위로 저장)
        transformer_outputs.append(transformer_out.detach().cpu().numpy())  # transformer_out 저장

        # 손실 계산
        train_loss = criterion(output, batch_targets[:, 0])

        # 역전파 수행
        train_loss.backward()
        optimizer.step()

        # 배치별 손실 저장
        total_train_loss += train_loss.item()
        avg_train_loss = total_train_loss / (batch_idx + 1)  # 평균 손실 계산
        epoch_train_losses.append(train_loss.item())  # **배치별 손실 저장**

        # 검증 데이터에서 손실 계산
        model.eval()  # 평가 모드로 전환
        with torch.no_grad():
            val_inputs, val_targets = next(iter(val_loader))
            val_inputs, val_targets = val_inputs.to(device), val_targets.to(device)
            val_output, _ = model(val_inputs)
            val_loss = criterion(val_output, val_targets[:, 0])

        total_val_loss += val_loss.item()
        avg_val_loss = total_val_loss / (batch_idx + 1)  # 검증 배치 손실의 평균
        epoch_val_losses.append(val_loss.item())  # **검증 배치별 손실 저장**

        model.train()  # 다시 학습 모드로 전환

        # 실시간 손실 출력
        if batch_idx % 1000 == 0:
            print(f'Epoch {epoch+1}, Batch {batch_idx+1}, Train Loss: {avg_train_loss}, Validation Loss: {avg_val_loss}')

    # 에포크마다 손실 값 출력
    print(f'Epoch {epoch+1} - Train Loss: {avg_train_loss}, Validation Loss: {avg_val_loss}')

    # 에포크가 끝날 때 손실 그래프 그리기
    plt.figure(figsize=(10, 6))
    plt.plot(epoch_train_losses, label='Train Loss (Batch-wise)')
    plt.plot(epoch_val_losses, label='Validation Loss (Batch-wise)')
    plt.xlabel('Batch')
    plt.ylabel('Loss')
    plt.title(f'Epoch {epoch+1} - Training & Validation Loss Over Batches')
    plt.legend()
    plt.grid(True)
    plt.show()