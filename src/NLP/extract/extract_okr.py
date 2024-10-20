import re
from sentence_transformers import SentenceTransformer, util
from transformers import PegasusForConditionalGeneration, PegasusTokenizer, MarianMTModel, MarianTokenizer
from docx import Document
import os

# SBERT 모델 로드
encode_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# 요약 모델 및 토크나이저 불러오기 (PEGASUS 2B + SLiC 대신 Hugging Face의 공개된 PEGASUS 사용)
model_name = 'google/pegasus-xsum'  # PEGASUS 모델 로드 (XSUM 데이터셋 기반으로 훈련됨)
model = PegasusForConditionalGeneration.from_pretrained(model_name)
tokenizer = PegasusTokenizer.from_pretrained(model_name)

# 번역 모델 및 토크나이저 불러오기 (한국어 -> 영어)
translation_model_name = 'Helsinki-NLP/opus-mt-ko-en'
translation_model = MarianMTModel.from_pretrained(translation_model_name)
translation_tokenizer = MarianTokenizer.from_pretrained(translation_model_name)


def translate_to_english(text):
    # 입력 텍스트를 토큰화
    inputs = translation_tokenizer.encode(text, return_tensors="pt", max_length=512, truncation=True)
    
    # 번역 생성
    translated_ids = translation_model.generate(inputs, max_length=512, num_beams=5, early_stopping=True)
    
    # 번역된 텍스트 디코딩
    translated_text = translation_tokenizer.decode(translated_ids[0], skip_special_tokens=True)
    
    return translated_text

def summarize_text(text):
    # 입력 텍스트를 토큰화 (영어로 번역된 텍스트를 요약)
    inputs = tokenizer.encode(text, return_tensors="pt", max_length=512, truncation=True)
    
    # 요약 생성 (PEGASUS 모델)
    summary_ids = model.generate(
        inputs, 
        max_length=40,  # PEGASUS는 더 긴 요약을 잘 처리할 수 있음
        min_length=20,  # 최소 요약 길이
        length_penalty=2.0,  # 요약이 더 짧게 나오도록 패널티를 강화
        num_beams=8,    # 빔 서치 값을 증가시켜 더 다양한 요약 생성
        early_stopping=True
    )
    
    # 요약된 텍스트 디코딩
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    
    return summary

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

# 숫자 가중치를 적용하여 유사도를 계산하는 함수
def extract_okr(doc_path, threshold=0.5, weight=1.2):

    # OKR에 대한 성과 항목 정의 (Objective는 제거)
    okr_labels = {
        "Key Result 1": "정확한 수치와 숫자가 들어있는 성과",
        "Key Result 2": "정확한 수치와 숫자가 들어있는 성과",
        "Key Result 3": "정확한 수치와 숫자가 들어있는 성과"
    }

    project_performance = extract_project_performance(doc_path)

    obj_list = []

    for text in project_performance:
        translated_text = translate_to_english(text)  # 한국어를 영어로 번역
        obj = summarize_text(translated_text)     # 번역된 영어 텍스트를 요약
        obj_list.append(obj)

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

    kr_list = []  # 최종 2차원 결과 리스트

    number_pattern = re.compile(r'\d+')  # 숫자 패턴을 찾기 위한 정규 표현식

    # 각 프로젝트에 대해 처리
    for project_sentences in all_sentences:
        project_okr_results = {}  # 각 프로젝트의 OKR 결과를 저장할 딕셔너리
        used_sentences = set()  # 중복 방지를 위한 집합

        for label, description in okr_labels.items():
            # OKR 레이블에 대한 임베딩 생성
            label_embedding = encode_model.encode(description, convert_to_tensor=True)

            highest_score = -1  # 가장 높은 유사도를 저장할 변수
            best_sentence = None

            for sentence in project_sentences:
                # 중복된 문장은 건너뜀
                if sentence in used_sentences:
                    continue

                # 문장 임베딩 및 유사도 계산
                sentence_embedding = encode_model.encode(sentence, convert_to_tensor=True)
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
                translated_sentence = translate_to_english(best_sentence)  # 문장을 번역
                project_okr_results[label] = translated_sentence
                used_sentences.add(best_sentence)  # 선택된 문장을 저장

        # 각 프로젝트별로 OKR 결과를 리스트로 변환하여 추가
        kr_list.append([project_okr_results.get(label) for label in okr_labels])

    # obj와 KR1, KR2, KR3을 하나의 리스트로 결합하여 final_list에 추가
    final_okr_list = []

    for obj, kr in zip(obj_list, kr_list):
        final_okr_list.append([obj] + kr)  # obj와 kr1, kr2, kr3을 하나의 리스트로 결합

    return final_okr_list


# 현재 SBert.py 파일 위치 기준으로 상대 경로 설정
docx_file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', '인사평가서_okr.docx')

final_okr_list = extract_okr(docx_file_path)

print(final_okr_list)