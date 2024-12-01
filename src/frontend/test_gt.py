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
import plotly.graph_objects as go

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from NLP.extract.extract_okr import extract_okr
from buildteam.visualize import *

# MySQL 서버에 연결
conn = mysql.connector.connect(
    #host='10.80.11.114', # 학교 호스트 (DGU-WIFI)
    #host='170.20.10.2', # 핫스팟 호스트 이름 (현재 핫스팟)
    host = '192.168.208.42', # 승현 핫스팟
    user='initmember',       # MySQL 사용자 이름
    password='qweqsame1231',   # MySQL 사용자 비밀번호
    database='employee'  # 연결할 데이터베이스 이름
)


# 테스트용 임시 데이터 추가
member_details = {
    1: {
        #"experience": "8년",
        "education": "컴퓨터공학 석사",
        "certifications": ["PMP", "Agile Scrum Master"],
        "previous_projects": ["AI 플랫폼 개발", "클라우드 마이그레이션"],
        "strengths": ["리더십", "의사소통", "문제해결"],
        #"languages": ["한국어", "영어"],
        "contact": "member1@example.com"
    },
    2: {
        #"experience": "5년",
        "education": "컴퓨터공학 학사",
        "certifications": ["React Developer", "AWS Developer"],
        "previous_projects": ["전자상거래 플랫폼", "모바일 앱 개발"],
        "strengths": ["UI/UX", "최신 기술 습득력"],
        #"languages": ["한국어", "영어"],
        "contact": "member2@example.com"
    },
    # ... 나머지 멤버들의 상세 정보도 비슷한 형식으로 추가
}


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
    }

     /* 사이드바 버튼 스타일 - 여러 클래스 선택자 사용 */
    .css-1d391kg .stButton > button,
    .css-1544g2n .stButton > button,
    .css-k1vhr4 .stButton > button,
    [data-testid="stSidebar"] .stButton > button {
        margin-left: 0;
        width: 100%;
        text-align: center;
        margin-bottom: 8px;
        background-color: #FF4B4B;
    }
    .stButton > button:hover {
        background-color: #FF3333;
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
    .member-box {
        cursor: pointer;
        transition: transform 0.2s;
    }
    .member-box:hover {
        transform: scale(1.02);
    }
    
    .stModal {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
        /* 사이드바 스타일 */
    .css-1d391kg {
        padding-top: 3.5rem;
    }
    
    /* 햄버거 메뉴 아이콘 스타일 */
    .st-emotion-cache-r421ms {
        z-index: 999;
    }
    
    /* 사이드바 버튼 스타일 */
    .sidebar-button {
        width: 100%;
        padding: 15px;
        margin: 5px 0;
        border: none;
        border-radius: 5px;
        background-color: #f0f2f6;
        cursor: pointer;
        text-align: left;
        transition: background-color 0.3s;
    }
    
    .sidebar-button:hover {
        background-color: #e0e2e6;
    }
    
    .sidebar-button.active {
        background-color: #ff4b4b;
        color: white;
    }           
    </style>
""", unsafe_allow_html=True)

# 멤버 정보 가져오는 함수
def get_member_info(member_id):
    # SQL 쿼리 생성
    query = f"""
    SELECT task
    FROM member_based_okr_assignments
    WHERE Member IN ({member_id})
    """

    try:
        id_list = [member_id]
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
        cursor.close()

    stack_list = ['Node.js']

    # members 리스트 생성
    if len(id_list) == len(task_list) == len(stack_list):
        members = {
            member: {"name": ('Member ' + str(int(member))), 
                  "role": task, 
                  "skills": skills}
            for idx, (member, task, skills) in enumerate(zip(id_list, task_list, stack_list))
        }

        return members.get(member_id, {"name": f"Member {member_id}", "role": "Unknown", "skills": "Unknown"})


def get_member_name(member_id):
    return get_member_info(member_id)["name"]


# 세션 상태 초기화
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'upload'

# 사이드바 생성
with st.sidebar:
    st.title("메뉴")
    
    # 파일 업로드 페이지 버튼
    if st.button("파일 업로드", 
                key="upload_btn",
                help="프로젝트 문서 업로드 페이지로 이동",
                use_container_width=True):
        st.session_state['current_page'] = 'upload'
        st.session_state['dashboard'] = False
    
    # 대시보드 페이지 버튼
    if st.button("대시보드", 
                key="dashboard_btn",
                help="팀 매칭 대시보드 페이지로 이동",
                use_container_width=True):
        if 'uploaded_file_path' in st.session_state:
            st.session_state['current_page'] = 'dashboard'
            st.session_state['dashboard'] = True
        else:
            st.warning("먼저 파일을 업로드해주세요.")
    # Team Builder 버튼 추가
    if st.button("팀 빌더", key="team_builder_btn", use_container_width=True):
        if 'uploaded_file_path' in st.session_state:
            st.session_state['current_page'] = 'team_builder'
        else:
            st.warning("먼저 파일을 업로드해주세요.")

# 메인 컨텐츠
if st.session_state['current_page'] == 'upload':
    st.title("프로젝트 팀 매칭 시스템")
    file_title = st.text_input("프로젝트 제목", value="", placeholder="프로젝트 제목을 입력하세요")
    uploaded_file = st.file_uploader("프로젝트 문서 업로드", type=['pdf', 'docx', 'hwp'])

    if st.button("분석 시작"):
        if uploaded_file is not None and file_title:
            save_path = os.path.join("uploaded_files", uploaded_file.name)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            st.session_state['uploaded_file_path'] = save_path
            st.session_state['file_title'] = file_title
            st.session_state['current_page'] = 'dashboard'
            st.session_state['dashboard'] = True
            st.success(f"{uploaded_file.name} 파일이 업로드되었습니다.")
        else:
            st.warning("제목과 파일을 모두 입력해 주세요.")

elif st.session_state['current_page'] == 'dashboard':
    if st.session_state['dashboard']:
        member_list = member_list
        score_list = score_list
        capability_list = skils 
        
        # 시너지 매트릭스 데이터
        synergy_df = pd.DataFrame(
            synergy_matrix,
            index=[get_member_name(id) for id in member_list[0]],
            columns=[get_member_name(id) for id in member_list[0]]
        )
        
        # 개인 역량 점수
        individual_scores = individual_scores
        
        # 기여도 데이터
        contribution_list = contribution

        # 데이터 준비
        final_okr_list = extract_okr(st.session_state['uploaded_file_path'])[0]
        
        # 대시보드 제목
        st.markdown('<div class="dashboard-title">Team Matching Dashboard</div>', unsafe_allow_html=True)

        # Project Details 섹션
        st.markdown(f"""
        <div class="container">
            <div class="section-title">Project Overview</div>
            <div style="font-size:32px;"><strong>Project:</strong> {st.session_state['file_title']}</div>
            <p style="font-size:25px;"><strong>Description:</strong> {final_okr_list[0]}</p>
        </div>
        """, unsafe_allow_html=True)

        # Objective and Key Results 섹션
        st.markdown(f"""
        <div class="container">
            <div class="section-title">Project Goals</div>
            <p style="font-size:30px;"><strong>Main Objective:</strong> {final_okr_list[1]}</p>
            <div style="font-size:28px;"><strong>Key Results:</strong></div>
            <ul>
                <li style="font-size:25px; margin-bottom: 10px;">{final_okr_list[2]}</li>
                <li style="font-size:25px; margin-bottom: 10px;">{final_okr_list[3]}</li>
                <li style="font-size:25px; margin-bottom: 10px;">{final_okr_list[4]}</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        # Team Composition 섹션
        st.markdown(f'''
            <div class="container">
                <div class="section-title">Best Team Composition (Team Score: {score_list[0]})</div>
            </div>
        ''', unsafe_allow_html=True)

        cols = st.columns(len(member_list[0]))
        for col, member_id in zip(cols, member_list[0]):
            member_info = get_member_info(member_id)
            
            # 멤버 박스를 expander로 만들기
            with col.expander(f"{member_info['name']} 상세 정보"):
                details = member_details.get(member_id, {})
                
                # 기본 정보
                st.subheader("기본 정보")
                st.write(f"**역할:** {member_info['role']}")
                #st.write(f"**경력:** {details.get('experience', 'N/A')}")
                st.write(f"**학력:** {details.get('education', 'N/A')}")
                st.write(f"**보유 기술:** {member_info['skills']}")
                st.write(f"**연락처:** {details.get('contact', 'N/A')}")
                
                # 자격증 및 강점
                st.subheader("자격증 및 강점")
                st.write("**자격증:**")
                for cert in details.get('certifications', []):
                    st.write(f"- {cert}")
                
                st.write("**강점:**")
                for strength in details.get('strengths', []):
                    st.write(f"- {strength}")
                
                # 프로젝트 이력
                st.subheader("프로젝트 이력")
                for project in details.get('previous_projects', []):
                    st.write(f"- {project}")
            
            # 기존 멤버 정보 표시
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
            labels = [get_member_name(member_id) for member_id in contribution_list.keys()]
            values = list(contribution_list.values())
            
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
                margin=dict(t=80, l=0, r=0, b=80),
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
        # 사이드바 수정
elif st.session_state['current_page'] == 'team_builder':
    st.markdown('<div class="dashboard-title">Team Builder</div>', unsafe_allow_html=True)
    
    # 직군별 멤버 데이터 (예시)
    roles = ["Project Manager", "Frontend Engineer", "Backend Engineer", "Data Engineer", "UI/UX Designer"]
    all_members = {
        "Project Manager": [f"PM_{i}" for i in range(1, 11)],
        "Frontend Engineer": [f"FE_{i}" for i in range(1, 11)],
        "Backend Engineer": [f"BE_{i}" for i in range(1, 11)],
        "Data Engineer": [f"DE_{i}" for i in range(1, 11)],
        "UI/UX Designer": [f"UI_{i}" for i in range(1, 11)]
    }
    
    # 현재 Best Team 표시
    st.markdown("""
    <div class="container">
        <div class="section-title">Current Best Team</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 각 역할별로 선택 가능한 멤버 표시
    cols = st.columns(len(roles))
    current_team = []
    
    for idx, (col, role) in enumerate(zip(cols, roles)):
        with col:
            st.subheader(role)
            # Best Team의 멤버를 기본값으로 설정
            default_member = get_member_name(member_list[0][idx])
            selected_member = st.selectbox(
                f"Select {role}",
                options=all_members[role],
                key=f"select_{role}",
                index=all_members[role].index(default_member) if default_member in all_members[role] else 0
            )
            current_team.append(selected_member)
    
    # 팀 분석 결과 표시
    if st.button("팀 분석하기"):
        st.markdown("""
        <div class="container">
            <div class="section-title">Team Analysis Result</div>
        </div>
        """, unsafe_allow_html=True)
        
        # 선택된 팀의 점수 계산 (예시)
        new_team_score = 80  # 실제로는 선택된 팀원들의 조합에 따른 점수 계산 필요
        new_capability_scores = [4.0, 3.5, 4.2, 3.8, 4.1, 3.9]  # 예시 데이터
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Team Matching Score
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=new_team_score,
                title={'text': "New Team Matching Score", 'font': {'size': 30}},
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
            # Team Capability Balance
            categories = ['Collaboration', 'Responsibility', 'Problem Solving', 
                         'Communication', 'Initiative', 'Feedback Receptiveness']
            
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=new_capability_scores,
                theta=categories,
                fill='toself',
                name='New Team Balance'
            ))
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
                showlegend=False,
                title=dict(text="New Team Capability Balance", font=dict(size=30))
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # 점수 비교
        st.markdown("""
        <div class="container">
            <div class="section-title">Score Comparison</div>
        </div>
        """, unsafe_allow_html=True)
        
        comparison_df = pd.DataFrame({
            'Team': ['Best Team', 'Current Selection'],
            'Score': [score_list[0], new_team_score]
        })
        
        fig = px.bar(comparison_df,
                    x='Team',
                    y='Score',
                    title="Team Score Comparison",
                    color='Team',
                    color_discrete_sequence=["#3498db", "#e74c3c"])
        
        fig.update_layout(
            title_font_size=30,
            yaxis_range=[0, 100],
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)


   