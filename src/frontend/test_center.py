import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import base64
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from NLP.extract.extract_okr import extract_okr

# Streamlit 페이지 설정
st.set_page_config(page_title="Team Matching Dashboard", layout="wide", page_icon="📊")

# CSS 스타일링
st.markdown("""
    <style>
    body {
        font-family: Arial, sans-serif;
        background-color: #f4f4f9;
        font-size: 22px;
    }
            .stButton > button {
        background-color: #FF4B4B;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 8px 16px;
        font-size: 16px;
        margin-left: 18px;
    }
    .stButton > button:hover {
        background-color: #FF3333;
    }
    .container {
        background-color: white;
        border-radius: 15px;
        padding: 35px;
        margin-bottom: 35px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    .dashboard-title {
        font-size: 85px;
        font-weight: bold;
        color: #2c3e50;
        text-align: center;
        margin-top: 35px;
        margin-bottom: 55px;
    }
    .section-title {
        font-size: 48px;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 25px;
    }
    .member-box {
        text-align: center;
        padding: 25px;
        border-radius: 12px;
        background: #ffffff;
        border: 1px solid #e3e8ed;
        margin: 18px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    .member-name {
        font-size: 32px;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 10px;
    }
    .member-role {
        font-size: 26px;
        color: #34495e;
        margin-bottom: 10px;
    }
    .member-skills {
        font-size: 22px;
        color: #7f8c8d;
    }
    .chart-container {
        padding: 25px;
        background: white;
        border-radius: 15px;
        margin-bottom: 25px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    </style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if 'dashboard' not in st.session_state:
    st.session_state['dashboard'] = False
if 'show_candidates' not in st.session_state:
    st.session_state['show_candidates'] = False

# 파일 업로드 섹션
if not st.session_state['dashboard']:
    st.title("프로젝트 팀 매칭 시스템")
    file_title = st.text_input("프로젝트 제목", "프로젝트 제목을 입력하세요")
    uploaded_file = st.file_uploader("프로젝트 문서 업로드", type=['pdf', 'docx', 'hwp'])

    if st.button("분석 시작"):
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
    # 데이터 준비
    final_okr_list = extract_okr(st.session_state['uploaded_file_path'])[0]
    predict_score = 91

    members = [
        {"name": "강성지", "role": "PM(9년차)", "skills": "Agile, Scrum"},
        {"name": "구동현", "role": "UI/UX(3년차)", "skills": "Figma, Adobe"},
        {"name": "김승현", "role": "D_Eng(4년차)", "skills": "SQL, Python"},
        {"name": "전현재", "role": "F_Dev(2년차)", "skills": "React, Vue.js"},
        {"name": "유근태", "role": "B_Dev(2년차)", "skills": "Node.js"}
    ]

    skills = {
        'Collaboration': 22,
        'Responsibility': 15,
        'Problem Solving': 11,
        'Communication': 17,
        'Initiative': 20
    }

    color_mapping = {
        "Collaboration": "#2B66C2",
        "Initiative": "#57AD9D",
        "Communication": "#F3AFAD",
        "Responsibility": "#EB4339",
        "Problem Solving": "#93C7FA"
    }

    # 대시보드 제목
    st.markdown('<div class="dashboard-title">Team Matching Dashboard</div>', unsafe_allow_html=True)

    # Project Details 섹션
    st.markdown("""
    <div class="container">
        <div class="section-title">Project Overview</div>
        <div style="font-size:32px;"><strong>Project:</strong> {}</div>
        <p style="font-size:28px;"><strong>Description:</strong> {}</p>
    </div>
    """.format(st.session_state['file_title'], final_okr_list[0]), unsafe_allow_html=True)

    # Objective and Key Results 섹션
    st.markdown("""
    <div class="container">
        <div class="section-title">Project Goals</div>
        <p style="font-size:30px;"><strong>Main Objective:</strong> {}</p>
        <div style="font-size:28px;"><strong>Key Results:</strong></div>
        <ul style="font-size:26px;">
            <li>{}</li>
            <li>{}</li>
            <li>{}</li>
        </ul>
    </div>
    """.format(final_okr_list[1], final_okr_list[2], final_okr_list[3], final_okr_list[4]), unsafe_allow_html=True)

    # Team Composition 섹션
    # Team Composition 섹션
    st.markdown('<div class="container"><div class="section-title">Team Composition</div></div>', unsafe_allow_html=True)
    cols = st.columns(len(members))
    for col, member in zip(cols, members):
        col.markdown(f"""
            <div class="member-box">
                <div class="member-name">{member['name']}</div>
                <div class="member-role">{member['role']}</div>
                <div class="member-skills">{member['skills']}</div>
            </div>
        """, unsafe_allow_html=True)

    # Show Other Candidate Teams 버튼
    st.button("Show Other Candidate Teams", key="show_candidates_btn", 
             on_click=lambda: setattr(st.session_state, 'show_candidates', not st.session_state.get('show_candidates', False)))

    # Candidate Teams Comparison 섹션
    if st.session_state.get('show_candidates', False):
        st.markdown("""
        <div class="container">
            <div class="section-title">Candidate Teams Comparison</div>
        </div>
        """, unsafe_allow_html=True)

        # 후보 팀 데이터
        candidate_teams = [
            {
                "team_name": "Team 2",
                "members": [
                    {"name": "이지원", "role": "PM(8년차)", "skills": "PMP, Kanban"},
                    {"name": "정수진", "role": "UI/UX(4년차)", "skills": "Sketch, Adobe XD"},
                    {"name": "박데이", "role": "D_Eng(5년차)", "skills": "Python, R"},
                    {"name": "김프론", "role": "F_Dev(3년차)", "skills": "Angular, React"},
                    {"name": "김백엔", "role": "B_Dev(3년차)", "skills": "Spring, Java"}
                ],
                "team_score": 88
            },
            {
                "team_name": "Team 3",
                "members": [
                    {"name": "박준호", "role": "PM(7년차)", "skills": "Agile, PMP"},
                    {"name": "한미래", "role": "UI/UX(3년차)", "skills": "Adobe, Protopie"},
                    {"name": "이현우", "role": "D_Eng(3년차)", "skills": "SQL, Tableau"},
                    {"name": "이재민", "role": "F_Dev(4년차)", "skills": "Vue.js, TypeScript"},
                    {"name": "이서버", "role": "B_Dev(4년차)", "skills": "Django, Python"}
                ],
                "team_score": 85
            }
        ]

        # 각 후보 팀 표시
        for team in candidate_teams:
            st.markdown(f"### {team['team_name']} (Team Score: {team['team_score']})")
            cols = st.columns(len(team['members']))
            for col, member in zip(cols, team['members']):
                col.markdown(f"""
                    <div class="member-box">
                        <div class="member-name">{member['name']}</div>
                        <div class="member-role">{member['role']}</div>
                        <div class="member-skills">{member['skills']}</div>
                    </div>
                """, unsafe_allow_html=True)
            st.markdown("---")



    # Team Analysis 섹션
    st.markdown('<div class="container"><div class="section-title">Team Analysis</div></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        # Team Matching Score
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=predict_score,
            title={'text': "Team Matching Score", 'font': {'size': 30}},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "#3498db"},
                'steps': [
                    {'range': [0, 60], 'color': "#ff9999"},
                    {'range': [60, 80], 'color': "#ffcc99"},
                    {'range': [80, 100], 'color': "#99ff99"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Team Synergy Matrix
        synergy_matrix = pd.DataFrame(
            np.random.uniform(0.7, 1.0, size=(5, 5)),
            index=[member['name'] for member in members],
            columns=[member['name'] for member in members]
        )
        fig = px.imshow(
            synergy_matrix,
            color_continuous_scale="RdYlBu",
            title="Team Synergy Analysis",
            labels=dict(color="Synergy Score")
        )
        fig.update_layout(title_font_size=30)
        st.plotly_chart(fig, use_container_width=True)

    # Team Capabilities 섹션
    col1, col2 = st.columns(2)
    with col1:
        # Team Balance Radar Chart
        categories = list(skills.keys())
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=[skills[cat] for cat in categories],
            theta=categories,
            fill='toself',
            name='Team Balance'
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 25])),
            showlegend=False,
            title=dict(text="Team Capability Balance", font=dict(size=30))
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Role Distribution
        fig = px.pie(
            values=list(skills.values()),
            names=list(skills.keys()),
            title="Team Skill Distribution",
            color=list(skills.keys()),
            color_discrete_map=color_mapping
        )
        fig.update_layout(title_font_size=30)
        st.plotly_chart(fig, use_container_width=True)

    # Individual Analysis 섹션
    st.markdown('<div class="container"><div class="section-title">Individual Analysis</div></div>', unsafe_allow_html=True)
    
    selected_member = st.selectbox(
        "팀원 선택",
        [member["name"] for member in members]
    )

    col1, col2 = st.columns(2)
    with col1:
        # Individual Radar Chart
        individual_scores = {
            'Technical': np.random.randint(70, 100),
            'Collaboration': np.random.randint(70, 100),
            'Communication': np.random.randint(70, 100),
            'Leadership': np.random.randint(70, 100),
            'Problem Solving': np.random.randint(70, 100)
        }
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=list(individual_scores.values()),
            theta=list(individual_scores.keys()),
            fill='toself'
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=False,
            title=dict(text=f"{selected_member}'s Capability Analysis", font=dict(size=30))
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Project Contribution Score
        contribution_score = np.random.randint(85, 100)
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=contribution_score,
            title={'text': "Project Contribution Score", 'font': {'size': 30}},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "#3498db"},
                'steps': [
                    {'range': [0, 60], 'color': "#ff9999"},
                    {'range': [60, 80], 'color': "#ffcc99"},
                    {'range': [80, 100], 'color': "#99ff99"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        st.plotly_chart(fig, use_container_width=True)