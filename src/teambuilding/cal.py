import pandas as pd
from sentence_transformers import SentenceTransformer
import torch
import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# SBERT 모델 로드
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

def calculate_similarity(n_okr, objective):

    # 입력 문장들에 대해 임베딩 생성
    n_okr_embedding = model.encode(n_okr, convert_to_tensor=True)
    obj_embedding = model.encode(objective, convert_to_tensor=True)
    
    # 코사인 유사도 계산
    similarity = torch.nn.functional.cosine_similarity(n_okr_embedding, obj_embedding, dim=-1).item()
    
    return similarity


import pandas as pd
from sentence_transformers import SentenceTransformer
import torch
import os

# SBERT 모델을 한 번만 로드
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

def calculate_similarity(n_okr_embedding, obj_embedding):
    # 코사인 유사도 계산
    similarity = torch.nn.functional.cosine_similarity(n_okr_embedding, obj_embedding, dim=-1).item()
    return similarity


import pandas as pd
from sentence_transformers import SentenceTransformer
import torch
import os

import torch
from sentence_transformers import SentenceTransformer

# SBERT 모델을 한 번만 로드
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

def get_similarities(n_okr, objectives):
    # n_okr와 각 objective에 대해 임베딩 생성
    n_okr_embedding = model.encode(n_okr, convert_to_tensor=True)
    similarities = []

    for objective in objectives:
        obj_embedding = model.encode(objective, convert_to_tensor=True)
        similarity = torch.nn.functional.cosine_similarity(n_okr_embedding, obj_embedding, dim=-1).item()
        similarities.append(similarity)

    return similarities

def calculate_weighted_scores(n_okr):
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'member_okr.csv')

    df = pd.read_csv(csv_path)

    # 각 멤버의 유사도 계산 결과를 저장할 리스트
    weighted_sums = []

    # 각 멤버별로 데이터를 그룹화
    grouped_df = df.groupby('Member')

    for member, group in grouped_df:
        objectives = group['Objective'].tolist()
        objective_scores = group['Objective Score'].tolist()

        # 유사도 계산 (멤버별 3개의 okr에 대한 유사도)
        similarities = get_similarities(n_okr, objectives)
        
        #print(similarities)

        total_weighted_score = 0
        valid_count = 0

        # 유사도와 Objective Score를 곱해 가중합 계산
        for similarity, objective_score, objective in zip(similarities, objective_scores, objectives):
            if objective != n_okr:  # objective가 같은 경우 제외
                weighted_score = similarity * objective_score
                total_weighted_score += weighted_score
                valid_count += 1

        if valid_count > 0:
            weighted_sums.append((member, total_weighted_score / valid_count))
        else:
            weighted_sums.append((member, 0))  # 모든 유사도가 1에 가까운 경우

    return weighted_sums


n_okr = 'Boost the user base through targeted marketing features'
weighted_sums = calculate_weighted_scores(n_okr)
print(weighted_sums)
