import pandas as pd
import os
import numpy as np

# 현재 SBert.py 파일 위치 기준으로 상대 경로 설정
csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'member_okr.csv')

# CSV 파일을 pandas DataFrame으로 불러오기
df = pd.read_csv(csv_path)

print(df[0:150])

# member 컬럼 기준으로 내림차순 정렬
df_sorted = df.sort_values(by='Member', ascending=True)

# 모든 결과를 저장할 리스트
flattened_data = []

print(df_sorted)
# i에 따른 열 범위 설정 및 데이터 가져오기
for i in range(50):
    # i가 0~9일 때 13, 15~20번째 열을 선택
    if 0 <= i < 10:
        selected_columns = [12] + list(range(14, 20))
    # i가 10~19일 때 13, 21~26번째 열을 선택
    elif 10 <= i < 20:
        selected_columns = [12] + list(range(20, 26))
    elif 20 <= i < 30:
        selected_columns = [12] + list(range(26, 32))
    elif 30 <= i < 40:
        selected_columns = [12] + list(range(32, 38))
    elif 40 <= i < 50:
        selected_columns = [12] + list(range(38, 44))

    # 선택된 첫 번째 열은 행으로 병합 (행 우선)
    first_row_data = df_sorted.iloc[3 * i : 3 * (i + 1), selected_columns[0]].T.tolist()

    # 나머지 열은 열로 병합 (열 우선)
    other_data = df_sorted.iloc[3 * i : 3 * (i + 1), selected_columns[1:]].values.flatten().tolist()

    # 첫 번째 요소로는 인덱스+1 값을 추가, 두 번째 요소로는 null(np.nan) 값을 추가
    combined_data = [i + 1, np.nan] + first_row_data + other_data

    # 2차원 리스트에 추가
    flattened_data.append(combined_data)


# 예시로 컬럼명 생성
column_names = [
    'member', 'N_OKR', 'pr1_score', 'pr2_score', 'pr3_score', 
    'pr1_1', 'pr1_2', 'pr1_3', 'pr1_4','pr1_5', 'pr1_6', 
    'pr2_1', 'pr2_2', 'pr2_3', 'pr2_4', 'pr2_5', 'pr2_6', 
    'pr3_1', 'pr3_2', 'pr3_3', 'pr3_4', 'pr3_5', 'pr3_6'
]

# 데이터프레임 생성
df = pd.DataFrame(flattened_data, columns=column_names)

# 데이터프레임 출력
print(df)


df.to_csv('input.csv', index = False)