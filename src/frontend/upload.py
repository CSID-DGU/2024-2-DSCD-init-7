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

# DB 연동을 시뮬레이션하는 함수들
def get_member_info(member_id):
    # 실제로는 DB에서 가져와야 하는 정보
    member_db = {
        1: {"name": "강성지", "role": "PM(9년차)", "skills": "Agile, Scrum"},
        2: {"name": "구동현", "role": "UI/UX(3년차)", "skills": "Figma, Adobe"},
        3: {"name": "김승현", "role": "D_Eng(4년차)", "skills": "SQL, Python"},
        4: {"name": "전현재", "role": "F_Dev(2년차)", "skills": "React, Vue.js"},
        5: {"name": "유근태", "role": "B_Dev(2년차)", "skills": "Node.js"}
    }
    return member_db.get(member_id, {"name": f"Member {member_id}", "role": "Unknown", "skills": "Unknown"})

def get_member_name(member_id):
    return get_member_info(member_id)["name"]

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
    # 샘플 데이터 (실제로는 API나 다른 소스에서 받아와야 함)
    member_list = [[1, 2, 3, 4, 5], [11, 12, 13, 14, 15], [21, 22, 23, 24, 25]]
    score_list = [91, 88, 85]
    capability_list = [4.2, 3.5, 4.1, 3.8, 4.5, 4.4]  # 6가지 역량 점수
    
    # 시너지 매트릭스 데이터
    synergy_df = pd.DataFrame(
        np.array([
            [1.0, 0.8, 0.9, 0.7, 0.85],
            [0.8, 1.0, 0.75, 0.8, 0.9],
            [0.9, 0.75, 1.0, 0.85, 0.8],
            [0.7, 0.8, 0.85, 1.0, 0.75],
            [0.85, 0.9, 0.8, 0.75, 1.0]
        ]),
        index=[get_member_name(id) for id in member_list[0]],
        columns=[get_member_name(id) for id in member_list[0]]
    )
    
    # 개인 역량 점수
    individual_scores = [
        [1, 4.2, 3.8, 4.1, 3.9, 4.5, 4.3],
        [2, 3.9, 4.1, 3.8, 4.2, 4.0, 4.1],
        [3, 4.0, 3.9, 4.2, 3.8, 4.1, 4.0],
        [4, 3.8, 4.0, 3.9, 4.1, 3.9, 4.2],
        [5, 4.1, 3.8, 4.0, 3.9, 4.2, 3.8]
    ]
    
    # 기여도 데이터
    contribution_list = [(1, 25), (2, 20), (3, 20), (4, 18), (5, 17)]

    # 데이터 준비
    final_okr_list = extract_okr(st.session_state['uploaded_file_path'])[0]

    # 대시보드 제목
    st.markdown('<div class="dashboard-title">Team Matching Dashboard</div>', unsafe_allow_html=True)

    # Project Details 섹션
    st.markdown(f"""
    <div class="container">
        <div class="section-title">Project Overview</div>
        <div style="font-size:32px;"><strong>Project:</strong> {st.session_state['file_title']}</div>
        <p style="font-size:28px;"><strong>Description:</strong> {final_okr_list[0]}</p>
    </div>
    """, unsafe_allow_html=True)
    # Objective and Key Results 섹션
    st.markdown(f"""
    <div class="container">
        <div class="section-title">Project Goals</div>
        <p style="font-size:30px;"><strong>Main Objective:</strong> {final_okr_list[1]}</p>
        <div style="font-size:28px;"><strong>Key Results:</strong></div>
        <ul style="font-size:26px;">
            <li>{final_okr_list[2]}</li>
            <li>{final_okr_list[3]}</li>
            <li>{final_okr_list[4]}</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # Team Composition 섹션
    st.markdown('<div class="container"><div class="section-title">Team Composition</div></div>', unsafe_allow_html=True)
    cols = st.columns(len(member_list[0]))
    for col, member_id in zip(cols, member_list[0]):
        member_info = get_member_info(member_id)
        col.markdown(f"""
            <div class="member-box">
                <div class="member-name">{member_info['name']}</div>
                <div class="member-role">{member_info['role']}</div>
                <div class="member-skills">{member_info['skills']}</div>
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

        # 각 후보 팀 표시
        for team_idx, team_members in enumerate(member_list[1:], 2):
            st.markdown(f"### Team {team_idx} (Team Score: {score_list[team_idx-1]})")
            cols = st.columns(len(team_members))
            for col, member_id in zip(cols, team_members):
                member_info = get_member_info(member_id)
                col.markdown(f"""
                    <div class="member-box">
                        <div class="member-name">{member_info['name']}</div>
                        <div class="member-role">{member_info['role']}</div>
                        <div class="member-skills">{member_info['skills']}</div>
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
            value=score_list[0],  # 1등 팀의 점수
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
        # Team Score Comparison
        team_scores = pd.DataFrame({
            'Team': ['Team 1', 'Team 2', 'Team 3'],
            'Score': score_list
        })
        
        fig = px.bar(team_scores, 
                    x='Team', 
                    y='Score',
                    title="Team Score Comparison",
                    color='Team',
                    color_discrete_sequence=["#3498db", "#2ecc71", "#e74c3c"])
        
        fig.update_layout(
            title_font_size=30,
            yaxis_range=[min(score_list)-5, max(score_list)+5],
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

    # Team Capabilities 섹션
    col1, col2 = st.columns(2)
    with col1:
        # Team Balance Radar Chart
        categories = ['Collaboration', 'Responsibility', 'Problem Solving', 
                     'Communication', 'Initiative', 'Feedback Receptiveness']
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=capability_list,
            theta=categories,
            fill='toself',
            name='Team Balance'
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
            showlegend=False,
            title=dict(text="Team Capability Balance", font=dict(size=30))
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Team Synergy Matrix
        fig = px.imshow(
            synergy_df,
            color_continuous_scale="RdYlBu",
            title="Team Synergy Analysis",
            labels=dict(color="Synergy Score")
        )
        fig.update_layout(title_font_size=30)
        st.plotly_chart(fig, use_container_width=True)
    # Individual Analysis 섹션
    st.markdown('<div class="container"><div class="section-title">Individual Analysis</div></div>', unsafe_allow_html=True)
    
    # 멤버 선택 박스
    selected_member_idx = st.selectbox(
        "팀원 선택",
        range(len(member_list[0])),
        format_func=lambda x: get_member_name(member_list[0][x])
    )

    col1, col2 = st.columns(2)
    with col1:
        # Individual Radar Chart
        categories = ['Collaboration', 'Responsibility', 'Problem Solving', 
                     'Communication', 'Initiative', 'Feedback Receptiveness']
        
        # 선택된 멤버의 점수 찾기
        selected_member_scores = None
        for scores in individual_scores:
            if scores[0] == member_list[0][selected_member_idx]:
                selected_member_scores = scores[1:]  # 첫 번째 요소(ID)를 제외한 스킬 점수들
                break
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=selected_member_scores,
            theta=categories,
            fill='toself'
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
            showlegend=False,
            title=dict(text=f"{get_member_name(member_list[0][selected_member_idx])}'s Capability Analysis", 
                      font=dict(size=30))
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Team Contribution Distribution
        labels = [get_member_name(member_id) for member_id, _ in contribution_list]
        values = [score for _, score in contribution_list]
        
        # 선택된 멤버의 explode 값 설정
        selected_member_name = get_member_name(member_list[0][selected_member_idx])
        explode = [0.2 if label == selected_member_name else 0 for label in labels]
        
        fig = go.Figure()
        fig.add_trace(go.Pie(
            labels=labels,
            values=values,
            hole=0.3,
            pull=explode,
            textinfo='label+percent',
            textposition='outside',
            textfont=dict(size=14),
            marker=dict(
                colors=['#FF9999', '#66B2FF', '#99FF99', '#FFCC99', '#FF99CC'],
                line=dict(color='#FFFFFF', width=2)
            )
        ))
        
        fig.update_layout(
            title=dict(
                text="Team Contribution Distribution",
                font=dict(size=30),
                y=0.95
            ),
            showlegend=False,
            margin=dict(t=80, l=0, r=0, b=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)
