import pandas as pd
import os
import openai
from dotenv import load_dotenv

load_dotenv()
chatgpt_api_key = os.getenv('chatgpt_api_key')
openai.api_key = chatgpt_api_key

# 현재 SBert.py 파일 위치 기준으로 상대 경로 설정
csv_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'OKR_peer_30.csv')

# CSV 파일을 pandas DataFrame으로 불러오기
df = pd.read_csv(csv_path, encoding='cp949')
 
objectives = df['Objective'][:1].dropna().tolist()
key_result_1 = df['Key Result 1'][:1].dropna().tolist()
key_result_2 = df['Key Result 2'][:1].dropna().tolist()
key_result_3 = df['Key Result 3'][:1].dropna().tolist()

print(objectives)
print(key_result_1)
print(key_result_2)
print(key_result_3)

def generate_okr(obj, kr1, kr2, kr3):
    okr_generated = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": """당신은 프로젝트 성과를 간결하고 명확하게 한 문단으로 요약하는 전문가입니다. 
                성과는 기술적 기여, 성능 개선, 효율성 향상 등을 중심으로 작성되며, 명확하고 구체적인 결과를 포함해야 합니다. 
                한 문단으로 간결하게 작성해 주세요."""
            },
            {
                "role": "user",
                "content": f"""다음 프로젝트 성과를 한 문단으로 요약해 주세요. 
                프로젝트 목표(Objective): {obj}
                
                주요 성과(Key Results):
                1. {kr1}
                2. {kr2}
                3. {kr3}

                성과 평가를 한 문단으로 작성해 주세요. 프로젝트에는 실제 objective 내용이 들어가야돼. 기술적 기여, 성능 개선, 시스템 개선 사항 등을 포함하여 한 번에 읽히는 방식으로 작성해 주세요. 한국어로 작성해 주세요.
                
                아래는 예시 내용이야. 아래와 비슷한 양식으로 작성해줘. 저 :이랑 띄어쓰기 다 고려해줘.

                메인 공지 서비스 리뉴얼: 
                본 프로젝트에서 MongoDB의 CPU 사용률을 안정화하고, API 응답 시간을 3배 이상 개선하였으며, 기상악화 정보 수집 로직을 내재화하는 성과를 거두었습니다. 또한, 공지 메시지 관리의 효율성을 높이기 위한 자체 어드민 시스템을 구축함으로써 운영의 편의성을 크게 증대시켰습니다. 이를 통해 시스템 성능과 안정성이 획기적으로 향상되었습니다.
                
                """
            }
        ]
    )

    return okr_generated.choices[-1].message.content


# 각 항목을 ChatGPT API를 통해 생성 요청
for index, (obj, kr1, kr2, kr3) in enumerate(zip(objectives, key_result_1, key_result_2, key_result_3)):
    print(f"프로젝트 {index + 1}의 평가 생성 중...")
    evaluation = generate_okr(obj, kr1, kr2, kr3)
    print(f"프로젝트 {index + 1}의 평가:\n{evaluation}\n")