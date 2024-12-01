import torch
import torchvision
import torch.nn
import torch.nn as nn
import torch.optim as optim
import numpy as np

def member_change(npy,target_ids):
    data=np.load(npy)
    
    # Define index groups for averaging
    average_indices = [[1, 7, 13], [2, 8, 14], [3, 9, 15], [4, 10, 16], [5, 11, 17], [6, 12, 18]]
    
    # Calculate the mean for each index group
    averaged_data = np.stack([data[..., group].mean(axis=-1) for group in average_indices], axis=-1)
    
    # Retain the last three dimensions unchanged
    last_three = data[..., -3:]
    
    # Concatenate the averaged data with the last three dimensions
    avg_data = np.concatenate((averaged_data, last_three), axis=-1)

    result = []
    for i, team in enumerate(avg_data[..., -3]):
        if all(target_id in team for target_id in target_ids):
            result.append(avg_data[i])  # 팀 전체 데이터를 저장

    predict_score=result[0][:,-1]
    ab=result[0][:,:-3]
    ab_mean=ab.mean(axis=0)

    return predict_score, ab_mean



# target_ids = [7,13,25,36,42]
# print(member_change("real_result.npy",target_ids]))