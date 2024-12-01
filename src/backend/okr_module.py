import mysql.connector
import pandas as pd
import numpy as np
import itertools
from sentence_transformers import SentenceTransformer
import torch

# MySQL 서버 연결
def connect_to_database(host, user, password, database):
    return mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )

# 데이터 가져오기
def fetch_data_from_query(cursor, query):
    cursor.execute(query)
    result = cursor.fetchall()
    column_names = [i[0] for i in cursor.description]
    return pd.DataFrame(result, columns=column_names)

# 데이터 변환 및 정렬
def process_member_okr_data(member_okr):
    df_sorted = member_okr.sort_values(by='Member', ascending=True)
    flattened_data = []
    num_columns = df_sorted.shape[1]

    for i in range(50):
        if 0 <= i < 10 or 50 <= i < 60:
            selected_columns = [12] + [col for col in range(14, 20) if col < num_columns]
        elif 10 <= i < 20 or 60 <= i < 70:
            selected_columns = [12] + [col for col in range(20, 26) if col < num_columns]
        elif 20 <= i < 30 or 70 <= i < 80:
            selected_columns = [12] + [col for col in range(26, 32) if col < num_columns]
        elif 30 <= i < 40 or 80 <= i < 90:
            selected_columns = [12] + [col for col in range(32, 38) if col < num_columns]
        elif 40 <= i < 50 or 90 <= i < 100:
            selected_columns = [12] + [col for col in range(38, 44) if col < num_columns]

        first_row_data = df_sorted.iloc[3 * i:3 * (i + 1), selected_columns[0]].T.tolist()
        other_data = df_sorted.iloc[3 * i:3 * (i + 1), selected_columns[1:]].values.flatten().tolist()
        combined_data = [i + 1, np.nan] + first_row_data + other_data
        flattened_data.append(combined_data)

    column_names = [
        'member', 'N_OKR', 'pr1_score', 'pr2_score', 'pr3_score', 
        'pr1_1', 'pr1_2', 'pr1_3', 'pr1_4', 'pr1_5', 'pr1_6', 
        'pr2_1', 'pr2_2', 'pr2_3', 'pr2_4', 'pr2_5', 'pr2_6', 
        'pr3_1', 'pr3_2', 'pr3_3', 'pr3_4', 'pr3_5', 'pr3_6'
    ]
    max_length = max(len(row) for row in flattened_data)
    adjusted_column_names = column_names[:max_length]
    return pd.DataFrame(flattened_data, columns=adjusted_column_names).iloc[:, 1:]

# 가중치 계산
def calculate_weighted_scores(member_okr, n_okr):
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
    n_okr_embedding = model.encode(n_okr, convert_to_tensor=True)
    weighted_sums = []
    grouped_df = member_okr.groupby('Member')
    for member, group in grouped_df:
        objectives = group['Objective'].tolist()
        objective_scores = group['Objective Score'].tolist()
        similarities = []
        for objective in objectives:
            obj_embedding = model.encode(objective, convert_to_tensor=True)
            similarity = torch.nn.functional.cosine_similarity(n_okr_embedding, obj_embedding, dim=-1).item()
            similarities.append(similarity)

        total_weighted_score = sum(sim * score for sim, score in zip(similarities, objective_scores))
        valid_count = len(similarities)
        weighted_sums.append((member, total_weighted_score / valid_count if valid_count > 0 else 0))
    return weighted_sums

# 데이터 조합 생성
def generate_combinations_3d(data, num_parts=5):
    data_values = data.values
    part_size = len(data_values) // num_parts
    parts = [data_values[i * part_size:(i + 1) * part_size] for i in range(num_parts)]
    combinations = list(itertools.product(*parts))
    return np.array(combinations)
