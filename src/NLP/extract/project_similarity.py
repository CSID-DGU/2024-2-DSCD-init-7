import pandas as pd
from sentence_transformers import SentenceTransformer
import torch
import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 현재 SBert.py 파일 위치 기준으로 상대 경로 설정
csv_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'OKR_peer_30.csv')

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

# 유사도 결과를 src/data/ 폴더에 CSV 파일로 저장
output_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'objective_similarities.csv')
similarity_df.to_csv(output_path, index=True)

# 각 문장마다 상위 5개의 유사도를 출력하는 함수
def print_top_similarities(similarity_df, top_n=5):
    for index, row in similarity_df.iterrows():
        print(f"\n문장: {index}")
        # 자신을 제외한 상위 유사도 5개 추출
        top_similarities = row.drop(index).nlargest(top_n)
        for similar_index, similarity_value in top_similarities.items():
            print(f"  유사한 문장: {similar_index}, 유사도: {similarity_value:.4f}")


print_top_similarities(similarity_df, top_n=5)

# 전체 문장들의 유사도 값 추출 (대각선 제외)
# 대각선은 자기 자신과의 유사도(1.0)이므로 제외
all_similarities = similarity_df.values[np.triu_indices_from(similarity_df, k=1)]

# displot을 이용한 전체 유사도 분포 시각화
plt.figure(figsize=(10, 6))
sns.displot(all_similarities, kde=True, bins=30, color='blue')
plt.title('Overall Similarity Distribution Across All Objectives')
plt.xlabel('Cosine Similarity')
plt.ylabel('Density')
plt.grid(True)
plt.show()

