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

predict_score = 91

members = [
    {"name": "강성지", "role": "PM(9년차)", "skills": "Agile, Scrum"},
    {"name": "구동현", "role": "UI/UX(3년차)", "skills": "Figma, Adobe"},
    {"name": "김승현", "role": "D_Eng(4년차)", "skills": "SQL, Python"},
    {"name": "전현재", "role": "F_Dev(2년차)", "skills": "React, Vue.js"},
    {"name": "유근태", "role": "B_Dev(2년차)", "skills": "Node.js"}
]

skills = {'Collaboration': 22, 'Responsibility': 15, 'Problem Solving': 11, 'Communication': 17, 'Initiative': 20}

scores = {"Team 1": 70, "Team 2": 85, "Team 3": 95, "Team 4": 60, "Team 5": 78}

field_data = {
        'PM': [30, 20, 15, 25, 10],
        'Designer': [20, 30, 20, 15, 15],
        'Frontend Dev': [25, 25, 20, 20, 10],
        'Backend Dev': [40, 15, 30, 10, 5],
        'Data Engineer': [30, 10, 15, 35, 10]
    }

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
        donut_chart_base64 = create_donut_chart(predict_score, "Performance")
        st.markdown(
            f"""
            <div class="container" style="text-align: center;">
                <h4>Predictive Performance</h4>
                <img src="data:image/png;base64,{donut_chart_base64}" style="max-width: 100%; margin: 0 auto;">
            </div>
            """, unsafe_allow_html=True
        )

    # 열 지도 예시 (Heatmap)
    with col2:
        data = np.random.rand(10, 10)
        fig, ax = plt.subplots(figsize=(4, 4))
        cax = ax.matshow(data, cmap='coolwarm')
        plt.colorbar(cax)
        plt.title("Feature Importance", pad=20)
        buf = BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        base64_img = base64.b64encode(buf.getvalue()).decode("utf-8")
        st.markdown(
            f"""
            <div class="container" style="text-align: center;">
                <h4>Feature Importance</h4>
                <img src="data:image/png;base64,{base64_img}" style="max-width: 100%; margin: 0 auto;">
            </div>
            """, unsafe_allow_html=True
        )

    # 팀 점수 비교 차트
    with col3:
        fig = px.bar(x=list(scores.keys()), y=list(scores.values()), labels={'x': "Team", 'y': "Score"}, title="Score Comparison")
        st.plotly_chart(fig, use_container_width=True)

    # 팀 기술 스킬 차트
    with col4:
        fig = px.pie(values=list(skills.values()), names=list(skills.keys()), title="Team Skills")
        st.plotly_chart(fig, use_container_width=True)

    # Field Results 섹션
    st.markdown('<div class="container"><div class="title">Field Results</div></div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    for col, (key, values) in zip([col1, col2, col3, col4, col5], field_data.items()):
        fig = px.pie(values=values, names=[f"Category {i}" for i in range(len(values))], title=key)
        col.plotly_chart(fig, use_container_width=True)
