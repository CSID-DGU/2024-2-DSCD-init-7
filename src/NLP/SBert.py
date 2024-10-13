import pandas as pd
from sentence_transformers import SentenceTransformer
import torch
import os

# 현재 SBert.py 파일 위치 기준으로 상대 경로 설정
csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'OKR_and_Peer_Evaluation.csv')

# CSV 파일을 pandas DataFrame으로 불러오기
df = pd.read_csv(csv_path, encoding='cp949')
 

# 'Objective' 컬럼 추출
objectives = df['Objective'].dropna().tolist()

# print(objectives)

# SBERT 모델 로드
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# 문장의 임베딩 생성
embeddings = model.encode(objectives, convert_to_tensor=True)


# 코사인 유사도 계산
cosine_similarities = torch.nn.functional.cosine_similarity(embeddings.unsqueeze(1), embeddings.unsqueeze(0), dim=-1)

# DataFrame 형태로 유사도 결과 변환
similarity_df = pd.DataFrame(cosine_similarities.cpu().numpy(), index=objectives, columns=objectives)

# 유사도 결과를 CSV 파일로 저장
similarity_df.to_csv('objective_similarities.csv', index=True)

