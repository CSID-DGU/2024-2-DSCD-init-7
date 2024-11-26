import pandas as pd
import numpy as np

def preprocess_data(member_okr):
    df_sorted = member_okr.sort_values(by='Member', ascending=True)
    flattened_data = []
    num_columns = df_sorted.shape[1]

    for i in range(50):
        selected_columns = [12] + [col for col in range(14 + i % 10 * 6, 14 + i % 10 * 6 + 6) if col < num_columns]
        first_row_data = df_sorted.iloc[3 * i:3 * (i + 1), selected_columns[0]].T.tolist()
        other_data = df_sorted.iloc[3 * i:3 * (i + 1), selected_columns[1:]].values.flatten().tolist()
        combined_data = [i + 1, np.nan] + first_row_data + other_data
        flattened_data.append(combined_data)

    column_names = [
        'member', 'N_OKR', 'pr1_score', 'pr2_score', 'pr3_score',
        'pr1_1', 'pr1_2', 'pr1_3', 'pr1_4', 'pr1_5', 'pr1_6',
        'pr2_1', 'pr2_2', 'pr2_3', 'pr2_4', 'pr2_5', 'pr2_6',
        'pr3_1', 'pr3_2', 'pr3_3', 'pr3_4', 'pr3_5', 'pr3_6'
    ]
    max_length = max(len(row) for row in flattened_data)
    adjusted_column_names = column_names[:max_length]
    return pd.DataFrame(flattened_data, columns=adjusted_column_names).iloc[:, 1:]
