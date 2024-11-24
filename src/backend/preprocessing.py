import pandas as pd
import numpy as np

def sort_and_transform_data(df, num_columns):
    df_sorted = df.sort_values(by='Member', ascending=True)
    flattened_data = []

    for i in range(50):
        if 0 <= i < 10 or 50 <= i < 60:
            selected_columns = [12] + [col for col in range(14, 20) if col < num_columns]
        elif 10 <= i < 20 or 60 <= i < 70:
            selected_columns = [12] + [col for col in range(20, 26) if col < num_columns]
        elif 20 <= i < 30 or 70 <= i < 80:
            selected_columns = [12] + [col for col in range(26, 32) if col < num_columns]
        elif 30 <= i < 40 or 80 <= i < 90:
            selected_columns = [12] + [col for col in range(32, 38) if col < num_columns]
        elif 40 <= i < 50 or 90 <= i < 100:
            selected_columns = [12] + [col for col in range(38, 44) if col < num_columns]

        first_row_data = df_sorted.iloc[3 * i:3 * (i + 1), selected_columns[0]].T.tolist()
        other_data = df_sorted.iloc[3 * i:3 * (i + 1), selected_columns[1:]].values.flatten().tolist()
        combined_data = [i + 1, np.nan] + first_row_data + other_data
        flattened_data.append(combined_data)

    return flattened_data
