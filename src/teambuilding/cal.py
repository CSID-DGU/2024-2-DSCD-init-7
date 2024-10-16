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

    # 각 멤버별로 데이터를 그룹화
    grouped_df = df.groupby('Member')

    for member, group in grouped_df:
        total_weighted_score = 0

        # 각 멤버의 3개의 행에 대해 반복
        for index, row in group.iterrows():
            okr_num = row['OKR_NUM']
            objective = row['Objective']
            objective_score = row['Objective Score']

            # 각 Objective에 대한 임베딩 생성 및 유사도 계산
            obj_embedding = model.encode(objective, convert_to_tensor=True)
            similarity = torch.nn.functional.cosine_similarity(n_okr_embedding, obj_embedding, dim=-1).item()

            print('okr_num:', okr_num)
            print('objective:', objective)
            print('similarity:', similarity)      

            # 유사도와 Objective Score를 곱하여 가중합 계산
            weighted_score = similarity * objective_score
            total_weighted_score += weighted_score

        # 각 멤버에 대한 가중합을 리스트에 추가
        weighted_sums.append((member, total_weighted_score / 3))

    # 계산된 가중합을 데이터프레임으로 변환
    #weighted_df = pd.DataFrame(weighted_sums, columns=['Member', 'Weighted Sum'])

    # 가중합 결과 출력
    #print(weighted_df)

    return weighted_sums


n_okr = 'Boost the user base through targeted marketing features'
weighted_sums = calculate_weight(n_okr)
print(weighted_sums)