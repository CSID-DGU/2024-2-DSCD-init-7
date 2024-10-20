import os
import sys
import csv

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from extract.extract_okr import extract_okr


# 현재 SBert.py 파일 위치 기준으로 상대 경로 설정
docx_file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', '인사평가서_okr.docx')

final_okr_list = extract_okr(docx_file_path)

# CSV 파일로 저장할 경로 설정 (make_csv 폴더 내에 저장)
csv_file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'okr_results.csv')

# CSV 파일로 저장
with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)

    # 컬럼명 작성
    writer.writerow(["Objective", "Key Result 1", "Key Result 2", "Key Result 3"])

    # 2차원 리스트 내용을 CSV에 작성
    writer.writerows(final_okr_list)