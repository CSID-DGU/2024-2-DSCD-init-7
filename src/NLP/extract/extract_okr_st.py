import re
from sentence_transformers import SentenceTransformer, util
from transformers import T5ForConditionalGeneration, T5Tokenizer, MarianMTModel, MarianTokenizer
from docx import Document
import streamlit as st
from io import BytesIO
import pandas as pd

# SBERT 모델 로드
encode_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# 요약 모델 및 토크나이저 불러오기 (T5 모델 사용)
model_name = 't5-small'  
model = T5ForConditionalGeneration.from_pretrained(model_name)
tokenizer = T5Tokenizer.from_pretrained(model_name)

# 번역 모델 및 토크나이저 불러오기 (한국어 -> 영어)
translation_model_name = 'Helsinki-NLP/opus-mt-ko-en'
translation_model = MarianMTModel.from_pretrained(translation_model_name)
translation_tokenizer = MarianTokenizer.from_pretrained(translation_model_name)

# 텍스트 번역 함수
def translate_to_english(text):
    inputs = translation_tokenizer.encode(text, return_tensors="pt", max_length=512, truncation=True)
    translated_ids = translation_model.generate(inputs, max_length=512, num_beams=5, early_stopping=True)
    translated_text = translation_tokenizer.decode(translated_ids[0], skip_special_tokens=True)
    return translated_text

# 텍스트 요약 함수
def summarize_text(text):
    inputs = tokenizer.encode("summarize: " + text, return_tensors="pt", max_length=512, truncation=True)
    summary_ids = model.generate(
        inputs,
        max_length=20,
        min_length=10,
        length_penalty=3.0,
        num_beams=8,
        early_stopping=True
    )
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    summary = summary.strip().replace('.', '').replace('  ', ' ')
    return summary + '.'

# 전처리 함수
def preprocess_text(text):
    text_without_numbers = re.sub(r'\b\d+\s?(percent|%)?\b', '다소', text)
    return text_without_numbers

# 프로젝트 성과 추출 함수
def extract_project_performance(doc):
    project_performances = []
    in_project_section = False
    for para in doc.paragraphs:
        if '1. 주요 프로젝트 성과' in para.text:
            in_project_section = True
            continue
        if in_project_section:
            if para.text.strip() == "":
                break
            project_performances.append(para.text)
    return project_performances

# OKR 추출 함수
def extract_okr(doc, threshold=0.5, weight=1.2):
    okr_labels = {
        "Key Result 1": "정확한 수치와 숫자가 들어있는 성과",
        "Key Result 2": "정확한 수치와 숫자가 들어있는 성과",
        "Key Result 3": "정확한 수치와 숫자가 들어있는 성과"
    }
    project_performance = extract_project_performance(doc)
    obj_list = []

    for text in project_performance:
        preprocessed_text = preprocess_text(text)
        translated_text = translate_to_english(preprocessed_text)
        obj = summarize_text(translated_text)
        obj_list.append(obj)

    all_sentences = []
    for text in project_performance:
        sentences = text.split('.')
        sentences = [s.strip() for s in sentences if s.strip()]
        split_sentences = []
        for sentence in sentences:
            split_sentences.extend([seg.strip() for seg in sentence.split(',') if seg.strip()])
        all_sentences.append(split_sentences)

    kr_list = []
    number_pattern = re.compile(r'\d+')

    for project_sentences in all_sentences:
        project_okr_results = {}
        used_sentences = set()
        for label, description in okr_labels.items():
            label_embedding = encode_model.encode(description, convert_to_tensor=True)
            highest_score = -1
            best_sentence = None
            for sentence in project_sentences:
                if sentence in used_sentences:
                    continue
                sentence_embedding = encode_model.encode(sentence, convert_to_tensor=True)
                score = util.pytorch_cos_sim(label_embedding, sentence_embedding).item()
                if number_pattern.search(sentence):
                    score *= weight
                if score > highest_score and score >= threshold:
                    highest_score = score
                    best_sentence = sentence
            if best_sentence:
                translated_sentence = translate_to_english(best_sentence)
                project_okr_results[label] = translated_sentence
                used_sentences.add(best_sentence)

        kr_list.append([project_okr_results.get(label) for label in okr_labels])

    final_okr_list = []
    for obj, kr in zip(obj_list, kr_list):
        final_okr_list.append([obj] + kr)
    return final_okr_list

# Streamlit 인터페이스 설정 및 파일 업로드
st.title("OKR 문서 분석")
uploaded_file = st.file_uploader("분석할 .docx 파일을 업로드하세요", type="docx")

if uploaded_file is not None:
    doc = Document(BytesIO(uploaded_file.read()))
    final_okr_list = extract_okr(doc)

    # 결과를 테이블 형태로 출력
    st.write("OKR 분석 결과:")
    df = pd.DataFrame(final_okr_list, columns=["Objective", "Key Result 1", "Key Result 2", "Key Result 3"])
    st.table(df)
