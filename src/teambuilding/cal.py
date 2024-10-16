import pandas as pd
from sentence_transformers import SentenceTransformer
import torch
import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


def calculate_weight(n_okr):
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'member_okr.csv')

    df = pd.read_csv(csv_path)

    # SBERT 모델 로드
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

    # 문장의 임베딩 생성
    n_okr_embedding = model.encode(n_okr, convert_to_tensor=True)
    
    # 각 멤버의 유사도 계산 결과를 저장할 리스트
    weighted_sums = []

    # 유사도를 1로 간주하는 임계값 설정 (예: 0.9999 이상이면 1로 간주)
    similarity_threshold = 0.99

    # 각 멤버별로 데이터를 그룹화
    grouped_df = df.groupby('Member')

    for member, group in grouped_df:
        total_weighted_score = 0
        valid_count = 0  # 유사도가 1이 아닌 Objective 수를 셈

        # 각 멤버의 3개의 행에 대해 반복
        for index, row in group.iterrows():
            okr_num = row['OKR_NUM']
            objective = row['Objective']
            objective_score = row['Objective Score']

            # 각 Objective에 대한 임베딩 생성 및 유사도 계산
            obj_embedding = model.encode(objective, convert_to_tensor=True)
            similarity = torch.nn.functional.cosine_similarity(n_okr_embedding, obj_embedding, dim=-1).item()

            '''print('member:', member)
            print('okr_num:', okr_num)
            print('objective:', objective)
            print('similarity:', similarity)'''

            # 유사도가 임계값보다 낮은 경우에만 가중합 계산에 포함
            if similarity < similarity_threshold:
                weighted_score = similarity * objective_score
                total_weighted_score += weighted_score
                valid_count += 1

        # valid_count가 0이 아닌 경우만 나누기, 유사도가 모두 1에 가까운 경우는 0 반환
        if valid_count > 0:
            print(f' {member}의 가중합 공식: {total_weighted_score} / {valid_count}')
            weighted_sums.append((member, total_weighted_score / valid_count))
        else:
            weighted_sums.append((member, 0))  # 모든 유사도가 1에 가까운 경우

    return weighted_sums


n_okr = 'Boost the user base through targeted marketing features'
weighted_sums = calculate_weight(n_okr)
print(weighted_sums)