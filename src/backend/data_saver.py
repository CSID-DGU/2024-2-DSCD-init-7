import numpy as np

def save_final_data(all_data_f, output_filename):
    # 모든 data_f를 dim=0에서 연결하여 결합
    final_data_f = np.concatenate(all_data_f, axis=0)
    
    # 데이터 저장
    np.save(output_filename, final_data_f)
    print(f"Data saved to {output_filename}")
