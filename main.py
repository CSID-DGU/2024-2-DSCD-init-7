import mysql.connector
import pandas as pd
import numpy as np
import itertools
import torch
from src.backend.preprocess import preprocess_data
from src.backend.similarity import calculate_weighted_scores
from src.backend.model_inference import load_model, predict_with_model
from src.buildteam.algorithm import TeamTransformer

# MySQL 연결 정보
conn_params = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'hj010701',
    'database': 'employee'}

# MySQL 데이터 가져오기
conn = mysql.connector.connect(**conn_params)
cursor = conn.cursor()

cursor.execute("SELECT * FROM member_assign_50to100")
member_data = pd.DataFrame(cursor.fetchall(), columns=[i[0] for i in cursor.description])

cursor.execute("SELECT * FROM okr_30to60")
okr_data = pd.DataFrame(cursor.fetchall(), columns=[i[0] for i in cursor.description])

cursor.execute('''
SELECT *
FROM member_assign_50to100
JOIN okr_30to60 
ON okr_30to60.OKR_NUM IN (member_assign_50to100.project1, member_assign_50to100.project2, member_assign_50to100.project3);
''')
member_okr_data = pd.DataFrame(cursor.fetchall(), columns=[i[0] for i in cursor.description])

cursor.close()
conn.close()

# 데이터 정렬 및 처리
processed_data = preprocess_data(member_okr_data)

# 사용자 입력값
n_okr_input = "internal team communications Tool Improvement Projects have been aimed at improving the efficiency and accuracy of communication."
posted_input = 61.0
label_input = np.nan

# Weighted score 계산
weighted_sums = calculate_weighted_scores(n_okr_input, member_okr_data)[:50]
weighted_values = [value[1] for value in weighted_sums]
weighted_array = np.array(weighted_values)

if processed_data.shape[0] == len(weighted_values):
    processed_data.iloc[:, 0] = weighted_array
    processed_data["member"] = processed_data.index.astype(int)
    processed_data["posted"] = posted_input
    processed_data["label"] = label_input

def generate_combinations_3d(data, num_parts=5):
    data_values = data.values
    part_size = len(data_values) // num_parts
    parts = [data_values[i * part_size:(i + 1) * part_size] for i in range(num_parts)]
    combinations = list(itertools.product(*parts))
    return np.array(combinations)

data_3d = generate_combinations_3d(processed_data, num_parts=5)
final_data_f = np.concatenate((data_3d[:, :, 0:1], data_3d[:, :, 4:]), axis=2)

# 모델 파라미터
params = {
    'embedding_dim': 19,
    'n_heads': 1,
    'hidden_dim': 64,
    'n_layers': 3,
    'output_dim': 1,
    'dropout_rate': 0.2
}

# 모델 로드 및 추론
model = load_model('models/best_model_weights.pth', params)
predictions_list, transformer_out_list = predict_with_model(model, final_data_f)

transformer_out_last = transformer_out_list[-1]
expand_predict = np.repeat(predictions_list[-1], repeats=5, axis=1).reshape(-1, 5, 1)
output = torch.cat((transformer_out_last, final_data_f[:, :, -2:]), dim=-1)
result = torch.cat((output, expand_predict), dim=-1)

print(result)

