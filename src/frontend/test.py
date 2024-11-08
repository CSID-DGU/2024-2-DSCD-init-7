import streamlit as st
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from NLP.extract.extract_okr import extract_okr

# Example data for score and team members
score = 91.17

members = [
    {"name": "강성지", "role": "PM(9년차)", "skills": "Agile, Scrum"},
    {"name": "구동현", "role": "UI/UX(3년차)", "skills": "Figma, Adobe"},
    {"name": "김승현", "role": "D_Eng(4년차)", "skills": "SQL, Python"},
    {"name": "전현재", "role": "F_Dev(2년차)", "skills": "React, Vue.js"},
    {"name": "유근태", "role": "B_Dev(2년차)", "skills": "Node.js"}
]

team_color_data = {'Collaboration': 22, 'Responsibility': 15, 'Problem Solving': 11, 'Communication': 17, 'Initiative': 20}

score_comparison_data = {'Team 1': 75, 'Team 2': 60, 'Team 3': 95, 'Team 4': 91, 'Team 5': 88}

field_results_data = {
        'PM': [30, 20, 15, 25, 10],
        'Designer': [20, 30, 20, 15, 15],
        'Frontend Dev': [25, 25, 20, 20, 10],
        'Backend Dev': [40, 15, 30, 10, 5],
        'Data Engineer': [30, 10, 15, 35, 10]
    }

# Helper function to create and return a base64-encoded PNG
def create_image_placeholder(fig):
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", transparent=True)
    buf.seek(0)
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode("utf-8")

# Create circular performance chart
def create_circular_performance_chart(score):
    fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(aspect="equal"))
    colors = ["red", "lightgray"]
    data = [score, 100 - score]
    wedges, texts = ax.pie(data, colors=colors, startangle=90, wedgeprops=dict(width=0.3, edgecolor="w"))
    ax.text(0, 0, f"{score}%", ha='center', va='center', fontsize=18, fontweight='bold')
    return create_image_placeholder(fig)

# Create score comparison chart from dictionary input
def create_score_comparison_image(data_dict):
    fig, ax = plt.subplots()
    teams = list(data_dict.keys())
    scores = list(data_dict.values())
    ax.barh(teams, scores, color=['#f39c12', '#3498db', '#e74c3c', '#2ecc71', '#9b59b6'])
    ax.set_xlabel("Score")
    return create_image_placeholder(fig)

# Create team color pie chart from dictionary input
def create_team_color_image(data_dict):
    fig, ax = plt.subplots(figsize=(3, 3), subplot_kw=dict(aspect="equal"))
    labels = list(data_dict.keys())
    values = list(data_dict.values())
    colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6']
    wedges, texts = ax.pie(values, labels=labels, colors=colors, startangle=90, wedgeprops=dict(width=0.3, edgecolor="w"))
    ax.text(0, 0, "ability", ha='center', va='center', fontsize=9, fontweight='bold')
    return create_image_placeholder(fig)

# Create field results pie charts from dictionary input
def create_field_results_image(data_dict):
    fig, axes = plt.subplots(1, len(data_dict), figsize=(15, 3))
    colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6']
    for ax, (role, values) in zip(axes, data_dict.items()):
        ax.pie(values, colors=colors, startangle=90)
        ax.set_title(role)
    return create_image_placeholder(fig)

# Load feature importance image from file
def load_feature_importance_image():
    with open("./image/feature_importance.png", "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")
    
# Streamlit Page Configuration
st.set_page_config(layout="wide")

# CSS styling
st.markdown(
    """
    <style>
    .box {
        border: 2px solid #e6e6e6;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 12px rgba(0, 0, 0, 0.1);
        background-color: white;
        margin-bottom: 20px;
        height: 350px;
        width: 100%;
    }
    .title-box {
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .section-title {
        font-size: 24px;
        font-weight: bold;
        margin-top: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# State management for dashboard transition
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

else:
    st.title("Dashboard")
    final_okr_list = extract_okr(st.session_state['uploaded_file_path'])[0]

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(
            f"""
            <div class="box">
                <div class="title-box">Title: {st.session_state['file_title']}</div>
                <p><strong>Content:</strong> {final_okr_list[0]}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f"""
            <div class="box">
                <div class="title-box">Objective and Key Results</div>
                <p><strong>Objective:</strong> {final_okr_list[1]}</p>
                <p><strong>Key Result 1:</strong> {final_okr_list[2]}</p>
                <p><strong>Key Result 2:</strong> {final_okr_list[3]}</p>
                <p><strong>Key Result 3:</strong> {final_okr_list[4]}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown('<div class="section-title">Team Members</div>', unsafe_allow_html=True)
    member_cols = st.columns(5)
    for col, member in zip(member_cols, members):
        col.markdown(
            f"""
            <div class="box" style="text-align: center;">
                <p><strong>{member['name']}</strong></p>
                <p>{member['role']}</p>
                <p>{member['skills']}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown('<div class="section-title">Project Insights</div>', unsafe_allow_html=True)
    insights_col1, insights_col2 = st.columns([1, 1])

    with insights_col1:
        performance_chart_base64 = create_circular_performance_chart(score)
        st.markdown(
            f"""
            <div class="box" style="text-align: center;">
                <h4>Predictive Performance</h4>
                <img src="data:image/png;base64,{performance_chart_base64}" width="200">
            </div>
            """,
            unsafe_allow_html=True
        )

    with insights_col2:
        feature_importance_image_base64 = load_feature_importance_image()
        st.markdown(
            f"""
            <div class="box" style="text-align: center;">
                <h4>Feature Importance</h4>
                <img src="data:image/png;base64,{feature_importance_image_base64}" width="400">
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown('<div class="section-title">Additional Insights</div>', unsafe_allow_html=True)
    additional_col1, additional_col2 = st.columns([1, 1])

    score_comparison_image_base64 = create_score_comparison_image(score_comparison_data)
    with additional_col1:
        st.markdown(
            f"""
            <div class="box" style="text-align: center;">
                <h4>Score Comparison by Team</h4>
                <img src="data:image/png;base64,{score_comparison_image_base64}" width="400">
            </div>
            """,
            unsafe_allow_html=True
        )

    team_color_image_base64 = create_team_color_image(team_color_data)
    with additional_col2:
        st.markdown(
            f"""
            <div class="box" style="text-align: center;">
                <h4>Team Color</h4>
                <img src="data:image/png;base64,{team_color_image_base64}" width="400">
            </div>
            """,
            unsafe_allow_html=True
        )

    field_results_image_base64 = create_field_results_image(field_results_data)
    st.markdown(
        f"""
        <div class="box" style="text-align: center; height: 350px;">
            <h4>Field Results</h4>
            <img src="data:image/png;base64,{field_results_image_base64}" width="1000">
        </div>
        """,
        unsafe_allow_html=True
    )
