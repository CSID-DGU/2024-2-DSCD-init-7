import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
from io import BytesIO
import base64
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from NLP.extract.extract_okr import extract_okr


# Streamlit 페이지 설정
st.set_page_config(page_title="Enhanced Dashboard", layout="wide", page_icon="📊")

# CSS 스타일 추가
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
    </style>
""", unsafe_allow_html=True)

# Helper function to create donut charts
def create_donut_chart(score, label):
    fig, ax = plt.subplots(figsize=(3, 3), subplot_kw=dict(aspect="equal"))
    colors = ["#3498db", "#ecf0f1"]
    data = [score, 100 - score]
    wedges, _ = ax.pie(data, colors=colors, startangle=90, wedgeprops=dict(width=0.3, edgecolor="w"))
    ax.text(0, 0, f"{score}%", ha='center', va='center', fontsize=18, fontweight='bold')
    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", transparent=True)
    buf.seek(0)
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode("utf-8")

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

    # model을 여기 넣기


    predict_score = 91

    members = [
        {"name": "강성지", "role": "PM(9년차)", "skills": "Agile, Scrum"},
        {"name": "구동현", "role": "UI/UX(3년차)", "skills": "Figma, Adobe"},
        {"name": "김승현", "role": "D_Eng(4년차)", "skills": "SQL, Python"},
        {"name": "전현재", "role": "F_Dev(2년차)", "skills": "React, Vue.js"},
        {"name": "유근태", "role": "B_Dev(2년차)", "skills": "Node.js"}
    ]

    #members = [1, 23, 45, 77, 89]

    # db로 접근해서 role, skills 가져오는 방법

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

    st.markdown('<div class="container"><div class="title">Dashboard</div></div>', unsafe_allow_html=True)

    # Title and Objective 섹션
    st.markdown(f"""
        <div class="container">
            <div class="title-box">Title: {st.session_state['file_title']}</div>
            <p><strong>Content:</strong> {final_okr_list[0]}</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
        <div class="container">
            <div class="title">Objective and Key Results</div>
            <ul>
                <li><strong>Objective:</strong> {final_okr_list[1]}</li>
                <li><strong>Key Result 1:</strong> {final_okr_list[2]}</li>
                <li><strong>Key Result 2:</strong> {final_okr_list[3]}</li>
                <li><strong>Key Result 3:</strong> {final_okr_list[4]}</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

    # Members Section
    st.markdown('<div class="container"><div class="title">Team Members</div></div>', unsafe_allow_html=True)
    cols = st.columns(len(members))
    for col, member in zip(cols, members):
        col.markdown(f"""
            <div class="member-box">
                <div class="member-name">{member['name']}</div>
                <div class="member-role">{member['role']}</div>
                <div class="member-skills">{member['skills']}</div>
            </div>
        """, unsafe_allow_html=True)

    # 메트릭 카드 섹션
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="metric-box"><div class="metric-title">Completion Rate</div><div class="metric-value">91%</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-box"><div class="metric-title">Accuracy</div><div class="metric-value">88%</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-box"><div class="metric-title">User Satisfaction</div><div class="metric-value">92%</div></div>', unsafe_allow_html=True)

    # 도넛 차트 섹션
    col1, col2, col3, col4 = st.columns(4)
    with col1:
    # 도넛 차트를 plotly로 렌더링
        fig = px.pie(
            names=["Performance", "Remaining"],
            values=[predict_score, 100 - predict_score],
            hole=0.5,
            title="Predictive Performance",
        )
        fig.update_traces(textinfo='none')  # 중앙 텍스트 제거
        fig.add_annotation(
            text=f"{predict_score}%",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=20, color="black"),
            xref="paper",
            yref="paper",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
    # 열 지도(Heatmap)를 plotly로 렌더링
        fig = px.imshow(
            matrix,
            color_continuous_scale="RdBu",  # 변경된 부분: Plotly에서 지원하는 colorscale 사용
            title="Feature Importance",
            labels=dict(color="Importance"),
        )
        st.plotly_chart(fig, use_container_width=True)

    # 팀 점수 비교 차트
    with col3:
        # 데이터 정렬
        sorted_scores = dict(sorted(scores.items(), key=lambda item: item[1], reverse=False))
        
        # 점수에 '%' 추가
        scores_with_percentage = [f"{value}%" for value in sorted_scores.values()]

        # 막대 그래프 생성 (가로 방향)
        fig = px.bar(
            x=list(sorted_scores.values()),
            y=list(sorted_scores.keys()),
            labels={'x': "Score", 'y': "Team"},
            title="Score Comparison",
            orientation="h"  # 막대 그래프를 가로 방향으로 설정
        )
        fig.update_traces(
            text=scores_with_percentage,
            textposition="outside",  # 텍스트를 막대 끝에 표시
        )
        st.plotly_chart(fig, use_container_width=True)

    # 팀 기술 스킬 차트
    with col4:
        fig = px.pie(values=list(skills.values()), names=list(skills.keys()), title="Team Skills")
        st.plotly_chart(fig, use_container_width=True)

    # Field Results 섹션
    st.markdown('<div class="container"><div class="title">Field Results</div></div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    for col, (key, values) in zip([col1, col2, col3, col4, col5], field_data.items()):
        # 각 키를 레이블로 사용
        labels = list(skills.keys())  # Collaboration, Responsibility 등
        fig = px.pie(
            values=values,
            names=labels[:len(values)],  # 레이블을 기술 항목 이름으로 설정
            title=key
        )
        col.plotly_chart(fig, use_container_width=True)
