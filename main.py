import mysql.connector
import pandas as pd
from backend.data_processing import preprocess_member_okr
from backend.similarity_utils import calculate_weighted_scores
from backend.model_utils import generate_combinations_3d, load_model, predict_with_model
from sentence_transformers import SentenceTransformer

def main():
    # Step 1: 데이터베이스 연결 및 데이터 로드
    conn = mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        password='hj010701',
        database='employee'
    )
    cursor = conn.cursor()

    # 데이터 가져오기
    cursor.execute("SELECT * FROM member_assign_50to100")
    member_assign = pd.DataFrame(cursor.fetchall(), columns=[col[0] for col in cursor.description])

    cursor.execute("SELECT * FROM okr_30to60")
    okr_data = pd.DataFrame(cursor.fetchall(), columns=[col[0] for col in cursor.description])

    cursor.execute('''
        SELECT *
        FROM member_assign_50to100
        JOIN okr_30to60
        ON okr_30to60.OKR_NUM IN (
            member_assign_50to100.project1, 
            member_assign_50to100.project2, 
            member_assign_50to100.project3
        );
    ''')
    member_okr = pd.DataFrame(cursor.fetchall(), columns=[col[0] for col in cursor.description])

    # Step 2: 데이터 전처리
    processed_data = preprocess_member_okr(member_okr)

    # Step 3: 유사도 및 가중 점수 계산
    n_okr = "Your custom OKR here"
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
    weighted_scores = calculate_weighted_scores(member_okr, model, n_okr)

    # Step 4: 조합 생성 및 모델 예측
    data_3d = generate_combinations_3d(processed_data, num_parts=5)
    team_model = load_model()
    predictions = predict_with_model(team_model, data_3d)

    # Step 5: 결과 병합
    data_3d[:, :, -1] = predictions
    print(data_3d)

if __name__ == "__main__":
    main()
