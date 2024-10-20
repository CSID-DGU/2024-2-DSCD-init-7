import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from extract.extract_kr import extract_okr


# 현재 SBert.py 파일 위치 기준으로 상대 경로 설정
docx_file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', '인사평가서_okr.docx')

final_okr_list = extract_okr(docx_file_path)
