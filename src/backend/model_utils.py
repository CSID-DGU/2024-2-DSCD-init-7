import numpy as np
import torch
from buildteam.algorithm import TeamTransformer

def generate_combinations_3d(data, num_parts=5):
    """데이터를 3D 조합 형태로 변환합니다."""
    data_values = data.values
    part_size = len(data_values) // num_parts
    parts = [data_values[i * part_size:(i + 1) * part_size] for i in range(num_parts)]
    return np.array(list(itertools.product(*parts)))

def load_model():
    """TeamTransformer 모델을 로드합니다."""
    model = TeamTransformer(embedding_dim=19, n_heads=1, hidden_dim=64, n_layers=3, output_dim=1, dropout_rate=0.2)
    model.load_state_dict(torch.load('best_model_weights.pth', map_location=torch.device('cpu')))
    model.eval()
    return model

def predict_with_model(model, input_data):
    """모델을 사용하여 예측합니다."""
    input_tensor = torch.tensor(input_data, dtype=torch.float32)
    with torch.no_grad():
        predictions, _ = model(input_tensor)
    return predictions.numpy()
