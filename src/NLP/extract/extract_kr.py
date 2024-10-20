import re
from sentence_transformers import SentenceTransformer, util
from docx import Document
import os

# SBERT 모델 로드
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# OKR에 대한 성과 항목 정의 (Objective는 제거)
okr_labels = {
    "Key Result 1": "정확한 수치와 숫자가 들어있는 성과",
    "Key Result 2": "정확한 수치와 숫자가 들어있는 성과",
    "Key Result 3": "정확한 수치와 숫자가 들어있는 성과"
}

def extract_project_performance(doc_path):
    # .docx 파일 열기
    doc = Document(doc_path)
    
    project_performances = []
    in_project_section = False
    
    # 문서에서 주요 프로젝트 성과 추출
    for para in doc.paragraphs:
        if '1. 주요 프로젝트 성과' in para.text:
            in_project_section = True
            continue
        
        if in_project_section:
            if para.text.strip() == "":
                # 빈 줄을 만나면 프로젝트 성과 끝난 것으로 간주
                break
            project_performances.append(para.text)
    
    return project_performances


# 숫자 가중치를 적용하여 유사도를 계산하는 함수 (Objective는 없음)
def extract_okr_with_conditional_weights(doc_path, okr_labels, model, threshold=0.5, weight=1.2):

    project_performance = extract_project_performance(doc_path)

    all_sentences = []

    # 텍스트를 문장 단위로 분리
    for text in project_performance:
        sentences = text.split('.')
        sentences = [s.strip() for s in sentences if s.strip()]

        # 문장을 쉼표 단위로 세부 분할
        split_sentences = []
        for sentence in sentences:
            # 쉼표 단위로 분할 후 각 세그먼트별로 리스트에 추가
            split_sentences.extend([seg.strip() for seg in sentence.split(',') if seg.strip()])

        all_sentences.append(split_sentences)

    final_results = []  # 최종 2차원 결과 리스트

    number_pattern = re.compile(r'\d+')  # 숫자 패턴을 찾기 위한 정규 표현식

    # 각 프로젝트에 대해 처리
    for project_sentences in all_sentences:
        project_okr_results = {}  # 각 프로젝트의 OKR 결과를 저장할 딕셔너리
        used_sentences = set()  # 중복 방지를 위한 집합

        for label, description in okr_labels.items():
            # OKR 레이블에 대한 임베딩 생성
            label_embedding = model.encode(description, convert_to_tensor=True)

            highest_score = -1  # 가장 높은 유사도를 저장할 변수
            best_sentence = None

            for sentence in project_sentences:
                # 중복된 문장은 건너뜀
                if sentence in used_sentences:
                    continue

                # 문장 임베딩 및 유사도 계산
                sentence_embedding = model.encode(sentence, convert_to_tensor=True)
                score = util.pytorch_cos_sim(label_embedding, sentence_embedding).item()

                # 숫자가 포함된 문장에 가중치 적용
                if number_pattern.search(sentence):
                    score *= weight

                # 유사도 threshold 이상의 문장만 선택
                if score > highest_score and score >= threshold:
                    highest_score = score
                    best_sentence = sentence

            # 가장 유사한 문장을 저장하고 중복 방지
            if best_sentence:
                project_okr_results[label] = best_sentence
                used_sentences.add(best_sentence)  # 선택된 문장을 저장

        # 각 프로젝트별로 OKR 결과를 리스트로 변환하여 추가
        final_results.append([project_okr_results.get(label) for label in okr_labels])

    return final_results

# 현재 SBert.py 파일 위치 기준으로 상대 경로 설정
docx_file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', '하나요.docx')

# OKR 추출 실행 (Objective는 없고, 숫자 가중치 적용)
final_results = extract_okr_with_conditional_weights(docx_file_path, okr_labels, model, threshold=0.5, weight=1.5)


for kr in final_results:
    print(kr)
