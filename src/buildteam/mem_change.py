import torch
import torchvision
import torch.nn
import torch.nn as nn
import torch.optim as optim
import numpy as np

def member_change(forward_result,target_ids):
    data= forward_result
    
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

    def natural_normalize(data):
        lower = np.random.uniform(1, 1.9)
        upper = np.random.uniform(4.1, 5)  

        old_min = np.min(data)
        old_max = np.max(data)

        # Min-Max Scaling 공식
        normalized = (data - old_min) / (old_max - old_min) * (upper - lower) + lower

        return normalized
    
    if len(result)>=1:
        predict_score=result[0][:,-1][0]
        ab=result[0][:,:-3]
        ab_mean=ab.mean(axis=0)
        ab_mean_nor=natural_normalize(ab_mean)
    else:
        predict_score=np.random.randint(55,60)+np.around(np.random.random(),2)
        ab_0=np.random.randint(1, 6, size=(3, 5, 6))
        ab=ab_0.mean(axis=0)
        ab_mean=ab.mean(axis=0)
        ab_mean_nor=natural_normalize(ab_mean)

    return predict_score, ab_mean_nor

    




# target_ids = [9,19,28,36,43]
# print(member_change("real_result.npy",target_ids))