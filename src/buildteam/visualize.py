import torch
import torchvision
import torch.nn
import torch.nn as nn
import torch.optim as optim
import numpy as np


#뒤에 함수의 input임, dependency 있음
def find_top(data, top_k=5):
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

#1 변수별 중요도
def top_feature(data, top_index):
    top_feature=data[top_index,:,:-3].mean(axis=0)
    return top_feature

#2 예측성과
def top_team_score(data, top_index):
    top_team=data[top_index,:,-3]
    top_score=data[top_index,:,-1].max(axis=1)
    return top_team, top_score

#3 성향분포
def ability(data, top_index):
    ab=data[top_index,:,0:-3]
    top_ab=ab.mean(axis=1)
    top_1_ab=ab[0].mean(axis=1)
    return top_ab,top_1_ab

#4 직군별 성향분포
def field_ability(data, top_index):
    ab=data[top_index,:,0:-3]
    top_field_ab=ab.mean(axis=0)
    top_field_1_ab=ab[0]
    return top_field_ab,top_field_1_ab



#데이터 로드
data=np.load("test_result.npy")
if isinstance(data, np.ndarray):
    data_torch = torch.from_numpy(data)

#점수 높은 팀 인덱스 찾기
top_index=find_top(data_torch,top_index=5)

#동료평가서 묶어준 데이터
data_9=avg_data(data_torch)

#1 변수별 중요도(일반 data 사용)
top_feature_k=top_feature(data_torch, top_index)
top_feature_1=top_feature(data_torch, top_index)[0]

#2 예측성과 (data_9)
top_team, top_score=top_team_score(data_9, top_index)
top_team_1, top_score_1=top_team[0], top_score[0]

#3 성향분포 (data_9)
top_ab, top_1_ab=ability(data_9, top_index)

#4 직군별 성향분포 (data_9)
top_field_ab, top_field_1_ab=field_ability(data_9, top_index)


###
"""
1. 변수별 중요도 1등팀: top_feature_1
2. 예측성과 1등팀과 점수: top_team_1, top_score_1
3. 성향분포 1등팀: top_ab_1
4. 직군별 성향분포 1등팀: top_field_ab_1

각 1,2,3,4 top-k 전부 고려 (상호작용 항에 추가)
top_feature_k
top_team
top_score
top_ab
top_field_ab

"""
