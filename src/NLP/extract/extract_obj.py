from transformers import PegasusForConditionalGeneration, PegasusTokenizer, MarianMTModel, MarianTokenizer
from docx import Document

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

# .docx 파일 경로 설정
docx_file_path = r"C:\Users\irony\Documents\카카오톡 받은 파일\인사평가서.docx"

# 프로젝트 성과 추출
project_performances = extract_project_performance(docx_file_path)

# 각 프로젝트 성과에 대해 번역 및 요약 실행
for idx, text in enumerate(project_performances):
    translated_text = translate_to_english(text)  # 한국어를 영어로 번역
    summary = summarize_text(translated_text)     # 번역된 영어 텍스트를 요약
    
    print(f"\n프로젝트 {idx+1} 원문 (한국어):\n", text)
    print(f"\n프로젝트 {idx+1} 번역 (영어):\n", translated_text)
    print(f"\n프로젝트 {idx+1} 요약 (영어):\n", summary)
