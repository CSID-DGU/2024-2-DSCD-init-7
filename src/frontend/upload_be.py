import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
from io import BytesIO
import base64
import os
import sys
import mysql.connector

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from NLP.extract.extract_okr import extract_okr


# MySQL 서버에 연결
conn = mysql.connector.connect(
    host='10.80.11.114', # 학교 호스트 (DGU-WIFI)
    #host='170.20.10.2', # 핫스팟 호스트 이름 (현재 핫스팟)
    user='initmember',       # MySQL 사용자 이름
    password='qweqsame1231',   # MySQL 사용자 비밀번호
    database='employee'  # 연결할 데이터베이스 이름
)

# model을 여기 넣기


# Streamlit 페이지 설정
st.set_page_config(page_title="Enhanced Dashboard", layout="wide", page_icon="📊")

st.markdown("""
    <style>
    body {
        font-family: Arial, sans-serif;
        background-color: #f4f4f9;
    }
    .container {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .title {
        font-size: 24px;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 10px;
    }
    .dashboard-title {
        font-size: 60px;
        font-weight: bold;
        color: #2c3e50;
        text-align: center;
        margin-top: 20px;
        margin-bottom: 40px;
    }
    .metric-box {
        text-align: center;
        padding: 15px;
        border-radius: 10px;
        background: #f9fbfc;
        border: 1px solid #e3e8ed;
    }
    .metric-title {
        font-size: 16px;
        color: #2c3e50;
    }
    .metric-value {
        font-size: 20px;
        font-weight: bold;
        color: #2980b9;
    }
    .member-box {
        text-align: center;
        padding: 10px;
        border-radius: 8px;
        background: #ffffff;
        border: 1px solid #e3e8ed;
        margin: 10px;
    }
    .member-name {
        font-size: 14px;
        font-weight: bold;
        color: #2c3e50;
    }
    .member-role {
        font-size: 12px;
        color: #6c757d;
    }
    .member-skills {
        font-size: 12px;
        color: #6c757d;
    }
    /* Objective 내용 스타일 */
    .objective-content {
        font-size: 25px; /* 글씨 크기 조정 */
        font-weight: bold; /* 굵게 */
        color: #2c3e50; /* 색상 */
        margin-bottom: 10px; /* 아래 여백 */
    .project-details-title {
        font-size: 30px; /* Project Details 제목 크기 */
        font-weight: bold;
        color: #2c3e50;
    }
    .objective-key-results-title {
        font-size: 30px; /* Objective and Key Results 제목 크기 */
        font-weight: bold;
        color: #2c3e50;
    }
    </style>
""", unsafe_allow_html=True)

# Dashboard 제목 표시: 조건 추가
if st.session_state.get('dashboard', False):
    st.markdown('<div class="dashboard-title">Dashboard</div>', unsafe_allow_html=True)

# 파일 업로드 섹션
if 'dashboard' not in st.session_state:
    st.session_state['dashboard'] = False

if not st.session_state['dashboard']:
    st.title("Upload Files")
    file_title = st.text_input("Title", "Input Title")
    uploaded_file = st.file_uploader("Attached Document", type=['pdf', 'docx', 'hwp'], label_visibility="collapsed")

    if st.button("Upload"):
        if uploaded_file is not None and file_title:
            save_path = os.path.join("uploaded_files", uploaded_file.name)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            st.session_state['uploaded_file_path'] = save_path
            st.session_state['file_title'] = file_title
            st.session_state['dashboard'] = True
            st.success(f"{uploaded_file.name} 파일이 업로드되었습니다.")
        else:
            st.warning("제목과 파일을 모두 입력해 주세요.")


# 대시보드 섹션
if st.session_state['dashboard']:
    final_okr_list = extract_okr(st.session_state['uploaded_file_path'])[0]

    predict_score = 91

    member_list = [1, 11, 21, 31, 41]

    skills = {'Collaboration': 22, 'Responsibility': 15, 'Problem Solving': 11, 'Communication': 17, 'Initiative': 20}

    scores = {"[1, 23, 64, 65, 71]": 70, "[2, 24, 62, 89, 91]": 85, "[20, 40, 60, 80, 100]": 95, "[5, 25, 41, 66, 88]": 60, "[7, 17, 27, 48, 71]": 78}

    field_data = {
            'PM': [30, 20, 15, 25, 10],
            'Designer': [20, 30, 20, 15, 15],
            'Frontend Dev': [25, 25, 20, 20, 10],
            'Backend Dev': [40, 15, 30, 10, 5],
            'Data Engineer': [30, 10, 15, 35, 10]
        }
    
    matrix = np.random.rand(6, 19)

    # SQL 쿼리 생성
    query = f"""
    SELECT task
    FROM member_based_okr_assignments
    WHERE Member IN ({', '.join(map(str, member_list))})
    """

    # SQL 실행 및 결과를 리스트로 저장
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchall()  # 결과를 가져옴 (리스트 형태)
        task_list = [row[0] for row in result]  # 결과를 1차원 리스트로 변환

        # 역할 매핑
        role_mapping = {
            "pm": "Project Manager",
            "data": "Data Engineer",
            "frontend": "Frontend Engineer",
            "backend": "Backend Engineer",
            "design": "UI/UX Designer"
        }

        # task_list에서 매핑 수행
        task_list = [
            role_mapping[task] if task in role_mapping else task
            for task in task_list
        ]

    finally:
        # 연결 종료
        conn.close()

    # 기술 스택 리스트 (수정해야 함)
    stack_list = ['Agile, Scrum', 'Figma, Adobe', 'SQL, Python', 'React, Vue.js', 'Node.js']

    # members 리스트 생성
    if len(member_list) == len(task_list) == len(stack_list):
        members = [
            {"name": member, "role": task, "skills": stack}
            for member, task, stack in zip(member_list, task_list, stack_list)
        ]

    else:
        print("Lists have mismatched lengths. Please check the input data.")

    # Title and Objective 섹션
    st.markdown(f"""
    <div class="container">
        <div class="project-title" style="font-size:30px; font-weight:bold;">Project Details</div>
        <div class="title-box" style="font-size:20px;"><strong>Title:</strong> {st.session_state['file_title']}</div>
        <p style="font-size:18px;"><strong>Content:</strong> {final_okr_list[0]}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="container">
        <div class="okr-title" style="font-size:28px; font-weight:bold;">Objective and Key Results</div>
        <p style="font-size:22px;"><strong>Objective:</strong> {final_okr_list[1]}</p>
        <ul style="font-size:20px;">
            <li><strong>Key Result 1:</strong> {final_okr_list[2]}</li>
            <li><strong>Key Result 2:</strong> {final_okr_list[3]}</li>
            <li><strong>Key Result 3:</strong> {final_okr_list[4]}</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # Members Section
    st.markdown(f"""
    <div class="container">
        <div class="members-title" style="font-size:28px; font-weight:bold;">Team Members</div>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(len(members))
    for col, member in zip(cols, members):
        col.markdown(f"""
            <div class="member-box" style="text-align:center; padding:10px; border:1px solid #ccc; border-radius:8px;">
                <div class="member-name" style="font-size:16px; font-weight:bold;">{member['name']}</div>
                <div class="member-role" style="font-size:14px;">{member['role']}</div>
                <div class="member-skills" style="font-size:12px; color:#6c757d;">{member['skills']}</div>
            </div>
        """, unsafe_allow_html=True)

        # 고정된 색상 팔레트
    color_mapping = {
        "Collaboration": "#2B66C2",  # 진한 파란색
        "Initiative": "#57AD9D",     # 청록색
        "Communication": "#F3AFAD", # 주황색
        "Responsibility": "#EB4339", # 밝은 주황색
        "Problem Solving": "#93C7FA" # 노란색
    }

    # 차트 섹션
    st.markdown('<div class="container"><div class="chart-title" style="font-size:28px; font-weight:bold;">Charts</div></div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        # 도넛 차트를 plotly로 렌더링
        fig = px.pie(
            names=["Performance", "Remaining"],
            values=[predict_score, 100 - predict_score],
            hole=0.5,  # 구멍 크기 설정
            title="Predictive Performance",
        )
        fig.update_traces(
            textinfo='none',  # 조각 내부 텍스트 제거
            marker=dict(colors=["#3498db", "#ecf0f1"])  # 색상 고정
        )
        # 중앙 텍스트 추가
        fig.add_annotation(
            text=f"{predict_score}%",  # 중앙에 표시할 텍스트
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=22, color="black"),  # 텍스트 크기 및 색상 설정
            xref="paper",
            yref="paper",
        )
        st.plotly_chart(fig, use_container_width=True)


    with col2:
        fig = px.imshow(matrix, color_continuous_scale="RdBu", title="Feature Importance", labels=dict(color="Importance"))
        st.plotly_chart(fig, use_container_width=True)

    with col3:
        sorted_scores = dict(sorted(scores.items(), key=lambda item: item[1], reverse=False))
        scores_with_percentage = [f"{value}%" for value in sorted_scores.values()]
        
        # 막대 그래프 생성 (가로 방향)
        fig = px.bar(
            x=list(sorted_scores.values()),
            y=list(sorted_scores.keys()),
            labels={'x': "Score", 'y': "Team"},
            title="Score Comparison",
            orientation="h",  # 막대 그래프를 가로 방향으로 설정
            text=scores_with_percentage  # 텍스트 추가
        )
        
        fig.update_traces(
            textposition="outside",  # 텍스트를 막대 끝에 표시
            marker_color="#3498db"  # 막대 색상
        )
        
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        fig = px.pie(
            values=list(skills.values()), 
            names=list(skills.keys()), 
            title="Team Skills",
            color=list(skills.keys()),  # 색상 매핑할 이름
            color_discrete_map=color_mapping  # 고정된 색상 적용
        )
        st.plotly_chart(fig, use_container_width=True)


    # Field Results 섹션 (개별 역할별 차트)
    st.markdown('<div class="container"><div class="title">Field Results</div></div>', unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns(5)

    for col, (role, values) in zip([col1, col2, col3, col4, col5], field_data.items()):
        # 고정된 기술 순서에 맞게 값 매핑
        fig = px.pie(
            values=values,
            names=list(skills.keys()),  # 고정된 기술 이름 순서
            title=role,
            color=list(skills.keys()),  # 색상 매핑할 이름
            color_discrete_map=color_mapping  # 고정된 색상 적용
        )
        col.plotly_chart(fig, use_container_width=True)