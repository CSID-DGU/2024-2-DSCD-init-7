import streamlit as st
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from NLP.extract.extract_okr import extract_okr

# 페이지 설정
st.set_page_config(layout="centered")

# 상태 관리: 대시보드 전환 여부 확인
if 'dashboard' not in st.session_state:
    st.session_state['dashboard'] = False

if not st.session_state['dashboard']:
    # 파일 업로드 페이지
    st.title("Upload Files")
    file_title = st.text_input("Title", "Input Title")
    uploaded_file = st.file_uploader("Attached Document", type=['pdf', 'docx', 'hwp'], label_visibility="collapsed")

    if st.button("Upload", help="Click to upload your file"):
        if uploaded_file is not None and file_title:
            # 파일 저장 경로 설정
            save_path = os.path.join("uploaded_files", uploaded_file.name)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            st.session_state['uploaded_file_path'] = save_path
            st.session_state['file_title'] = file_title
            st.session_state['dashboard'] = True  # 대시보드 화면으로 전환
            
            st.success(f"{uploaded_file.name} 파일이 업로드되었습니다.")
        else:
            st.warning("제목과 파일을 모두 입력해 주세요.")

else:
    # 대시보드 페이지
    st.title("Dashboard")

    # 상단 프로젝트 설명 및 목표 섹션
    with st.container():
        col1, col2 = st.columns([3, 1])
        final_okr_list = extract_okr(st.session_state['uploaded_file_path'])

        with col1:
            st.write(f"## {st.session_state['file_title']}")
            st.write(final_okr_list[0][0])

        with col2:
            st.write("### Objective and Key Results")
            st.write(f"Objective: {final_okr_list[0][1]}")
            st.write(f"Key Result 1: {final_okr_list[0][2]}")
            st.write(f"Key Result 2: {final_okr_list[0][3]}")
            st.write(f"Key Result 3: {final_okr_list[0][4]}")

    st.write("---")

    # 팀 멤버 섹션
    st.write("### Team Members")
    member_cols = st.columns(5)
    members = [
        {"name": "강성지", "role": "PM(9년차)", "skills": "Agile, Scrum"},
        {"name": "구동현", "role": "UI/UX(3년차)", "skills": "Figma, Adobe"},
        {"name": "김승현", "role": "D_Eng(4년차)", "skills": "SQL, Python"},
        {"name": "전현재", "role": "F_Dev(2년차)", "skills": "React, Vue.js"},
        {"name": "유근태", "role": "B_Dev(2년차)", "skills": "Node.js"}
    ]
    for col, member in zip(member_cols, members):
        #col.image(member['image'], width=60)
        col.write(f"**{member['name']}**")
        col.write(f"{member['role']}")
        col.write(f"{member['skills']}")

    st.write("---")

    # 중간 성능 그래프 섹션
    st.write("### Project Insights")
    insights_col1, insights_col2 = st.columns([1, 1])

    with insights_col1:
        st.write("#### Predictive Performance")
        st.image("./image/predictive_performance.png", width=300)
    
    with insights_col2:
        st.write("#### Feature Importance")
        st.image("./image/feature_importance.png", width=300)

    # 하단 그래프 섹션: Score Comparison, Field Results, Team Color
    lower_col1, lower_col2 = st.columns([1, 1])

    with lower_col1:
        st.write("#### Score Comparison by Team")
        st.image("./image/score_comparison.png", width=300)

    with lower_col2:
        st.write("#### Field Results")
        st.image("./image/field_result.png", width=300)
        

    st.write("#### Team Color")
    st.image("./image/team_color.png", width=600)

    st.write("---")

