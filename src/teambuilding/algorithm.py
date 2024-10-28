import torch
import torchvision
import torch.nn
import torch.nn as nn
import torch.optim as optim
import numpy as np
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
# 트랜스포머 모델 정의
class TeamTransformer(nn.Module):
    def __init__(self, embedding_dim, n_heads, hidden_dim, n_layers, output_dim, dropout_rate):
        super(TeamTransformer, self).__init__()

        # 트랜스포머 인코더 레이어
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embedding_dim, nhead=n_heads, dim_feedforward=hidden_dim, dropout=dropout_rate
        )
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=n_layers)

        # 피드포워드 네트워크 (연속 점수 예측)
        self.fc_out = nn.Linear(embedding_dim, output_dim)

    def forward(self, embedded_team):
        # 트랜스포머 인코더를 통과
        transformer_out = self.transformer_encoder(embedded_team)  # [batch_size, seq_len, embedding_dim]

        # 전체 시퀀스의 평균을 구하여 점수 예측 (시퀀스 전체 정보 활용)
        avg_output = transformer_out.mean(dim=1)  # [batch_size, embedding_dim]

        # 점수 예측
        score = self.fc_out(avg_output)  # [batch_size, output_dim]

        return score, transformer_out
    