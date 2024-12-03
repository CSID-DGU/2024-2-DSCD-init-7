import pandas as pd
import numpy as np
import torch
from src.backend.okr_module import fetch_data_from_query, process_member_okr_data, calculate_weighted_scores, generate_combinations_3d
from src.buildteam.algorithm import TeamTransformer
from src.buildteam.dataloader import create_test_loader

def model(conn, n_okr_input):
    # 데이터베이스 커서 생성
    cursor = conn.cursor()

    # 데이터 로드
    member_assign_query = "SELECT * FROM member_assign_50to100"
    okr_query = "SELECT * FROM okr_30to60"
    join_query = '''
    SELECT *
    FROM member_assign_50to100
    JOIN okr_30to60 
    ON okr_30to60.OKR_NUM IN (member_assign_50to100.project1, member_assign_50to100.project2, member_assign_50to100.project3);
    '''

    member_assign_50to100 = fetch_data_from_query(cursor, member_assign_query)
    okr_df = fetch_data_from_query(cursor, okr_query)
    member_okr = fetch_data_from_query(cursor, join_query)

    # 데이터 처리
    data = process_member_okr_data(member_okr)

    # 사용자 입력값
    posted_input = 61.0
    label_input = np.nan

    # 가중치 계산
    weighted_sums = calculate_weighted_scores(member_okr, n_okr_input)[:50]
    weighted_values = [value[1] for value in weighted_sums]
    weighted_array = np.array(weighted_values)

    if data.shape[0] == len(weighted_values):
        data.iloc[:, 0] = weighted_array
        data["member"] = data.index.astype(int)
        data["posted"] = posted_input
        data["label"] = label_input
    else:
        raise ValueError(f"샘플 수가 일치하지 않습니다. data 행 수: {data.shape[0]}, weighted_values 길이: {len(weighted_values)}")

    # 데이터 조합 생성
    data_3d = generate_combinations_3d(data.iloc[:, :], num_parts=5)
    final_data_f = np.concatenate((data_3d[:, :, 0:1], data_3d[:, :, 4:]), axis=2)

    # 모델 파라미터 설정
    embedding_dim = 19
    seq_len = 5
    output_dim = 1
    n_heads = 1
    n_layers = 3
    hidden_dim = 64
    dropout_rate = 0.2

    # 모델 초기화
    model = TeamTransformer(
        embedding_dim=embedding_dim,
        n_heads=n_heads,
        hidden_dim=hidden_dim,
        n_layers=n_layers,
        output_dim=output_dim,
        dropout_rate=dropout_rate,
    )

    # 저장된 가중치 로드
    state_dict = torch.load('best_model_weights.pth', map_location=torch.device('cpu'))
    model.load_state_dict(state_dict)

    # 테스트 데이터를 위한 DataLoader 생성
    test_loader = create_test_loader(final_data_f, batch_size=512)
    transformer_out_list = []
    predictions_list = []

    # 평가 모드로 전환
    model.eval()
    for batch_inputs_total, _ in test_loader:
        with torch.no_grad():
            val_inputs_total, _ = next(iter(test_loader))
            val_inputs = batch_inputs_total[:, :, :-2]
            val_inputs_num = batch_inputs_total[:, :, -2:].int()
            predictions, transformer_out = model(val_inputs)
            transformer_out_list.append(transformer_out.detach().cpu().numpy())
            predictions_list.append(predictions)

    # 결과 조합
    transformer_out_last = torch.from_numpy(transformer_out_list[-1])
    expand_predict = np.repeat(predictions_list[-1], repeats=5, axis=1).reshape(-1, 5, 1)
    output = torch.cat((transformer_out_last, val_inputs_num), dim=-1)
    forward_result = torch.cat((output, expand_predict), dim=-1)

    return forward_result
