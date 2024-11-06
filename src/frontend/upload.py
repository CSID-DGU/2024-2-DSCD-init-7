import streamlit as st
import os

# 페이지 설정
st.set_page_config(layout="centered")
st.title("Upload Files")

# 제목 입력 필드
file_title = st.text_input("Title", "Input Title")


# 파일 업로드 컴포넌트를 숨긴 채로 제공
uploaded_file = st.file_uploader("Attached Document", type=['pdf', 'docx', 'hwp'], label_visibility="collapsed")

# 업로드된 파일 정보 표시
if uploaded_file is not None:
    # 파일 저장 경로 설정
    save_path = os.path.join("uploaded_files", uploaded_file.name)
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
# 업로드 버튼
if st.button("Upload", help="Click to upload your file"):
    if uploaded_file is not None:
        st.success(f"{uploaded_file.name} 파일이 업로드되었습니다.")
    else:
        st.warning("파일을 선택해 주세요.")
