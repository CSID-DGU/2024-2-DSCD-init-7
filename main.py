from backend.preprocessing import sort_and_transform_data
from backend.model import load_model_weights, make_predictions
import mysql.connector
import pandas as pd
import numpy as np

def main():
    # MySQL 연결 및 데이터 로드
    conn = mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        password='hj010701',
        database='employee'
    )

    cursor = conn.cursor()

    # member_assign_50to100 데이터 가져오기
    cursor.execute("SELECT * FROM member_assign_50to100")
    result = cursor.fetchall()
    column_names = [i[0] for i in cursor.description]
    member_df = pd.DataFrame(result, columns=column_names)

    # okr_30to60 데이터 가져오기
    cursor.execute("SELECT * FROM okr_30to60")
    result = cursor.fetchall()
    column_names = [i[0] for i in cursor.description]
    okr_df = pd.DataFrame(result, columns=column_names)

    # 데이터 정렬 및 변환
    sorted_data = sort_and_transform_data(member_df, member_df.shape[1])

    # 모델 로드
    model = load_model_weights(
        model_path='models/best_model_weights.pth',
        embedding_dim=19,
        seq_len=5,
        output_dim=1,
        n_heads=1,
        n_layers=3,
        hidden_dim=64,
        dropout_rate=0.2,
    )

    # 데이터 준비
    final_data_f = np.array(sorted_data)

    # 예측 수행
    predictions, transformer_outputs = make_predictions(model, final_data_f, batch_size=512)

    # 결과 출력 (필요에 따라 후처리)
    print("Predictions:", predictions)

# 스크립트 실행 여부 확인
if __name__ == "__main__":
    main()

