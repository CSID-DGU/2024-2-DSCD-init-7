import streamlit as st
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from NLP.extract.extract_okr import extract_okr


# 페이지 설정
st.set_page_config(layout="centered")
st.title("Upload Files")

# 제목 입력 필드
file_title = st.text_input("Title", "Input Title")

# 파일 업로드 컴포넌트 (PDF, DOCX, HWP 지원)
uploaded_file = st.file_uploader("Attached Document", type=['pdf', 'docx', 'hwp'], label_visibility="collapsed")

# 업로드된 파일 정보 표시
if uploaded_file is not None:
    # 파일 저장 경로 설정
    save_path = os.path.join("uploaded_files", uploaded_file.name)
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.success(f"{uploaded_file.name} 파일이 임시 저장되었습니다.")
else:
    st.warning("파일을 선택해 주세요.")

# 업로드 버튼 클릭 시 OKR 추출 및 결과 출력
if st.button("Upload", help="Click to upload your file"):
    if uploaded_file is not None:
        try:
            # OKR 추출 함수 호출
            final_okr_list = extract_okr(save_path)  # 파일 경로 전달
            
            # 추출된 OKR 결과 화면에 표시
            st.subheader("Extracted OKR Results")
            for i, okr in enumerate(final_okr_list):
                st.write(f"Project {i + 1}:")
                st.write(f"Objective: {okr[0]}")
                st.write(f"Key Result 1: {okr[1]}")
                st.write(f"Key Result 2: {okr[2]}")
                st.write(f"Key Result 3: {okr[3]}")
                st.write("---")
                
            st.success("OKR 추출이 완료되었습니다.")
        except Exception as e:
            st.error(f"OKR 추출 중 오류가 발생했습니다: {e}")
    else:
        st.warning("파일을 선택해 주세요.")