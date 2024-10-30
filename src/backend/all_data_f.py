import numpy as np
import sys
import os
sys.path.append(os.path.abspath("../teambuilding"))
from cal import calculate_weighted_scores
from combinations_3d import generate_combinations_3d

def process_data(data, objectives, score):
    all_data_f = []

    for i, n_okr in enumerate(objectives):
        # Step 2: calculate_weighted_scores 함수 사용하여 weighted_sums 계산
        weighted_sums = calculate_weighted_scores(n_okr)

        # Step 3: weighted_sums에서 두 번째 값을 추출
        weighted_values = [value[1] for value in weighted_sums]

        # Step 4: data의 첫 번째 열에 weighted_values 추가
        weighted_array = np.array(weighted_values)
        
        if data.shape[0] == len(weighted_values):
            data.iloc[:, 0] = weighted_array  # pandas의 iloc 사용하여 첫 번째 열에 할당
            data['label'] = score[i]  # label 추가
        else:
            print(f"Objective {i+1}: 샘플 수가 일치하지 않습니다.")
        
        data_3d = generate_combinations_3d(data.iloc[:, :], num_parts=5)

        # data_f 계산
        data_f = np.concatenate((data_3d[:, :, 0:1], data_3d[:, :, 4:]), axis=2)
        
        # data_f를 dim=0에서 쌓기 위해 리스트에 저장
        all_data_f.append(data_f)
    
    return all_data_f
