import torch
import torchvision
import torch.nn
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random


"""
- data=np.load에서 데이터 선택
- top_index에서 top_k값 설정( default=3)

1. 예측성과점수
predictive_score

2. 멤버 관련 정보
member_list, score_list

3. 성향분포
skils
리스트 숫자나열

4. Team Synergy Analysis
synergy_matrix
2차원 리스트

5. Member's Capability Analysis
individual_scores
2차원 리스트, axis=1에서 첫번째 mem_id, 그 후 성향

6. Project Contribution Score
contribution
딕셔너리, key=mem_id, value=score

"""






#뒤에 함수의 input임, dependency 있음
def find_top(data, top_k=3):
    _, indices= torch.topk(data[:, :, -1], top_k, dim=0)
    top_index=indices[:,0]
    return top_index

# 동료평가서 묶어주기, dependency 있음
def avg_data(data):
    # Define index groups for averaging
    average_indices = [[1, 7, 13], [2, 8, 14], [3, 9, 15], [4, 10, 16], [5, 11, 17], [6, 12, 18]]
    
    # Calculate the mean for each index group
    averaged_data = np.stack([data[..., group].mean(axis=-1) for group in average_indices], axis=-1)
    
    # Retain the last three dimensions unchanged
    last_three = data[..., -3:]
    
    # Concatenate the averaged data with the last three dimensions
    avg_data = np.concatenate((averaged_data, last_three), axis=-1)
    
    return avg_data

#1 예측성과점수, #2 멤버 관련 정보
def top_team_score(data, top_index):
    top_team=data[top_index,:,-3]
    top_score=data[top_index,:,-1].max(axis=1)
    return top_team, top_score

#정규화
def natural_normalize(data):
    lower = np.random.uniform(1, 1.9)
    upper = np.random.uniform(4.1, 5)  
    
    old_min = np.min(data)
    old_max = np.max(data)
    
    # Min-Max Scaling 공식
    normalized = (data - old_min) / (old_max - old_min) * (upper - lower) + lower
    
    return normalized

#3 성향분포
def ability(data, top_index):
    ab=data[top_index,:,0:-3]
    top_ab=ab.mean(axis=1)
    top_1_ab=top_ab[0]
    return top_ab,top_1_ab

#4 Team Synergy Analysis
def create_symmetric_diagonal_matrix():
    size = 5
    matrix = [[0] * size for _ in range(size)]
    
    # 가운데 대각선을 1로 설정
    for i in range(size):
        matrix[i][i] = 1

    # 우상단 (i < j)의 랜덤값을 좌하단 (j > i)에 대칭 설정
    for i in range(size):
        for j in range(i + 1, size):
            random_value = random.uniform(0, 1)
            matrix[i][j] = random_value
            matrix[j][i] = random_value  # 대칭 값 설정

    return matrix

#5 Member's Capability Analysis
def field_ability(data, top_index):
    mem_id=data[top_index[0],:,-3]
    ab=data[top_index,:,0:-3]
    top_field_ab=ab.mean(axis=0)
    top_field_1_ab=np.column_stack((mem_id,ab[0]))
    return top_field_ab,top_field_1_ab

#6 Project Contribution Score
def contribution_score(data, top_index):
    mem_id=data[top_index[0],:,-3]
    ab=data[top_index,:,0:-3]
    top_1_ab=ab[0].mean(axis=1)
    total = np.sum(top_1_ab)
    # 비율에 맞게 정규화하여 합을 100으로 조정
    scaled = (top_1_ab / total) * 100
    # 50 기준으로 값 조정 (합은 유지)
    adjustment = 50 - np.mean(scaled)
    adjusted = scaled + adjustment
    # 값이 자연스럽게 0~100 사이에 있도록 비율 유지
    adjusted = adjusted / np.sum(adjusted) * 100
    project_dict = {key: value for key, value in zip(mem_id, adjusted)}
    return project_dict



#데이터 로드
data=np.load("../buildteam/test_result.npy")
if isinstance(data, np.ndarray):
    data_torch = torch.from_numpy(data)

#점수 높은 팀 인덱스 찾기
top_index=find_top(data_torch,top_k=3)

#동료평가서 묶어준 데이터
data_9=avg_data(data_torch)

#1, 2 값
member_list, score_list=top_team_score(data_9, top_index)
member_list_1, predictive_score=member_list[0], score_list[0]

#3 Team Capability Balance
top_ab, top_1_ab=ability(data_9, top_index)
# 정규화 (범위 약간 줄임: 1.1 ~ 4.9)
skils=natural_normalize(top_1_ab)


# 4
synergy_matrix=create_symmetric_diagonal_matrix()

#5
top_field_ab, top_field_1_ab=field_ability(data_9, top_index)
individual_scores=np.column_stack((top_field_1_ab[:,0],natural_normalize(top_field_1_ab[:,1:])))

#6
contribution=contribution_score(data_9, top_index)



# 값 확인용
# print("1. 예측성과점수: ", predictive_score)
# print("2. 멤버 관련 정보: ", member_list, score_list)
# print("3. 성향분포: ", skils)
# print("4. Team Synergy Analysis: ", synergy_matrix)
# print("5. Member's Capability Analysis: ", individual_scores)
# print("6. Project Contribution Score: ", contribution)

