import torch
import torchvision
import torch.nn
import torch.nn as nn
import torch.optim as optim
import numpy as np
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from datapreprocess import create_dataloaders
from algorithm import TeamTransformer

#cuda
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# 하이퍼파라미터 설정
# 1. 데이터 관련
embedding_dim = 19
seq_len = 5  
output_dim = 1 

# 2. 모델 관련
n_heads = 1
n_layers = 3 
hidden_dim = 64  
dropout_rate = 0.2
epochs = 10

# 데이터 경로
data_path = "final.npy"

# 원하는 배치 크기
batch_size = 512

# DataLoader 생성
train_loader, val_loader = create_dataloaders(data_path, batch_size)


# 모델 초기화
model = TeamTransformer(embedding_dim, n_heads, hidden_dim, n_layers, output_dim, dropout_rate).to(device)

# 손실 함수 및 옵티마이저 설정
criterion = nn.MSELoss()  # 연속적인 점수 예측이므로 MSE 사용
optimizer = optim.Adam(model.parameters(), lr=0.001)



# 손실 기록 리스트
train_losses = []
val_losses = []
transformer_out_list = []
best_val_loss = float('inf')  # 초기화

# 학습 및 검증 루프
for epoch in range(epochs):
    # 각 에포크마다 새로운 리스트로 초기화 (각 에포크별로 그래프를 그리기 위함)
    epoch_train_losses = []
    epoch_val_losses = []  # validation 배치 손실 기록

    model.train()
    total_train_loss = 0
    total_val_loss = 0  # Validation 손실 초기화

    # Training & Validation Loop
    for batch_idx, (batch_inputs_total, batch_targets) in enumerate(train_loader):
        batch_inputs= batch_inputs_total[:, :, :-1]
        batch_inputs_num= batch_inputs_total[:, :, -1]

        # Training Step
        batch_inputs, batch_targets = batch_inputs.to(device), batch_targets.to(device)
        optimizer.zero_grad()
        output, _ = model(batch_inputs)


        # 타겟에서 팀원 제외하고 점수만 받기
        batch_targets = batch_targets[:, 0]

        # Train 손실 계산 및 역전파
        train_loss = criterion(output, batch_targets)
        train_loss.backward()
        optimizer.step()
        total_train_loss += train_loss.item()

        # Validation Step
        model.eval()
        with torch.no_grad():
            # val_inputs, val_targets = next(iter(val_loader))  # Validation 데이터를 매 배치마다 하나 가져옴
            # val_inputs, val_targets = val_inputs.to(device), val_targets.to(device)
            # val_output, transformer_out = model(val_inputs)
            val_inputs_total, val_targets = next(iter(val_loader))  # Validation 데이터를 매 배치마다 하나 가져옴
            val_inputs = val_inputs_total[:, :, :-1].to(device)  # Validation 입력 데이터에서 마지막 열 제외
            val_inputs_num = val_inputs_total[:, :, -1].int()  # Validation 입력 데이터에서 마지막 열만 가져옴
            val_targets = val_targets.to(device)
            val_output, transformer_out = model(val_inputs)
            transformer_out_list.append(transformer_out.detach().cpu().numpy())
            val_targets = val_targets[:, 0]
            val_loss = criterion(val_output, val_targets)
            total_val_loss += val_loss.item()


        model.train()  # 다시 training mode로 전환

        # 배치별 손실 저장
        avg_train_loss = total_train_loss / (batch_idx + 1)
        avg_val_loss = total_val_loss / (batch_idx + 1)
        epoch_train_losses.append(avg_train_loss)
        epoch_val_losses.append(avg_val_loss)

        train_losses.append(train_loss.item())
        # 각 스텝의 Validation 손실을 val_losses 리스트에 추가
        val_losses.append(val_loss.item())

        # 실시간 train 및 validation 손실 출력
        if batch_idx % 1000 == 0:
            print(f'Epoch {epoch+1}, Batch {batch_idx+1}, Train Loss: {avg_train_loss}, Validation Loss: {avg_val_loss}')

    # 에포크마다 손실 값 출력
    print(f'Epoch {epoch+1} - Train Loss: {avg_train_loss}, Validation Loss: {avg_val_loss}')

    # 최적의 모델 저장
    if avg_val_loss < best_val_loss:
        best_val_loss = avg_val_loss
        torch.save(model.state_dict(), 'best_model_weights.pth')
        print(f"최적의 모델 파라미터가 에포크 {epoch+1}에서 저장되었습니다 (Validation Loss: {best_val_loss})")


    # 에포크가 끝날 때마다 그래프 그리기
    plt.figure(figsize=(10, 6))

    # Training Loss
    plt.plot(epoch_train_losses, label='Train Loss')

    # Validation Loss
    plt.plot(epoch_val_losses, label='Validation Loss')

    plt.xlabel('Batch')
    plt.ylabel('Loss')
    plt.title(f'Epoch {epoch+1} - Training & Validation Loss Over Batches')
    plt.legend()
    plt.grid(True)
    plt.show()  # 한 에포크가 끝날 때마다 그래프 표시

# 전체 에포크에 대한 Train/Validation Loss 그래프 그리기
plt.figure(figsize=(10, 6))
plt.plot(train_losses, label='Train Loss')
plt.plot(val_losses, label='Validation Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.title('Validation Loss Over Epochs')
plt.legend()
plt.grid(True)
plt.show()

# transformer_out_list(attention value matrix)의 마지막 배치 가져오기
transformer_out_last = transformer_out_list[-1]

if isinstance(transformer_out_last, np.ndarray):
    transformer_out_last = torch.from_numpy(transformer_out_last)


# transformer_out_last에 붙이기
result = torch.cat((transformer_out_last, val_inputs_num), dim=-1) 

# numpy로 저장
np.save("result.npy", result)