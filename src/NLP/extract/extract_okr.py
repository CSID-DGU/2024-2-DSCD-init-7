from sentence_transformers import SentenceTransformer, util

# SBERT 모델 로드
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# OKR에 대한 목표 및 성과 항목 정의
okr_labels = {
    "Objective": "프로젝트의 목표",
    "Key Result 1": "정확한 수치와 숫자가 들어있는 성과",
    "Key Result 2": "정확한 수치와 숫자가 들어있는 성과",
    "Key Result 3": "정확한 수치와 숫자가 들어있는 성과"
}

# 예시 텍스트 (여기에 분석할 텍스트를 입력)
text = """
타겟 마케팅 기능 강화 프로젝트:
본 프로젝트를 통해 가입 전환율이 10% 향상되었고, 추천 프로그램 참여율은 20% 증가하는 성과를 보였습니다.
또한, 마케팅 과정에서의 사용자 획득 비용을 15% 절감함으로써 효율성을 크게 높였습니다.
이를 위한 서비스 개선과 시스템 구축을 전반적으로 진행하였으며, 이러한 결과는 우리의 기술적 기여에 의해 가능해진 것입니다.
이러한 성과는 사용자 증가 및 마케팅 비용 절감을 통한 기업의 성장에 크게 기여하였습니다.
"""

# 텍스트를 문장 단위로 분리
sentences = text.split('\n')
sentences = [s.strip() for s in sentences if s.strip()]

# 문장을 쉼표 단위로 세부 분할
split_sentences = []
for sentence in sentences:
    # 쉼표 단위로 분할 후 각 세그먼트별로 리스트에 추가
    split_sentences.extend([seg.strip() for seg in sentence.split(',') if seg.strip()])

print("쉼표로 나눈 세그먼트들:", split_sentences)

# OKR 추출 함수
def extract_okr(sentences, okr_labels, model, threshold=0.5):
    okr_results = {}  # 최종 결과를 저장하는 딕셔너리
    used_sentences = set()  # 이미 선택된 문장을 저장하는 집합

    for label, description in okr_labels.items():
        # 각 항목에 대해 임베딩 생성
        label_embedding = model.encode(description, convert_to_tensor=True)

        highest_score = -1  # 가장 높은 유사도 저장하는 변수
        best_sentence = None

        for sentence in sentences:
            # 중복된 문장은 건너뜀
            if sentence in used_sentences:
                continue

            # 문장 임베딩 및 유사도 계산
            sentence_embedding = model.encode(sentence, convert_to_tensor=True)
            score = util.pytorch_cos_sim(label_embedding, sentence_embedding).item()
            print(f"유사도 점수 for '{label}' and '{sentence}': {score}")

            # 일정 유사도 threshold 이상의 문장만 선택
            if score > highest_score and score >= threshold:
                highest_score = score
                best_sentence = sentence

        # 가장 유사한 문장을 저장하고 중복 방지
        if best_sentence:
            okr_results[label] = best_sentence
            used_sentences.add(best_sentence)  # 선택된 문장을 저장

    return okr_results

# OKR 추출 실행
okr_extracted = extract_okr(split_sentences, okr_labels, model, threshold=0.5)

print(okr_extracted)

# 결과 출력
for label, sentence in okr_extracted.items():
    print(f"{label}: {sentence}")
