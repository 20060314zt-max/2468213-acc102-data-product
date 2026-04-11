import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 页面配置
st.set_page_config(page_title="CS2 Pro Team Analysis", layout="wide")

# --- 数据载入 (直接复用你之前的 df) ---
@st.cache_data
def load_data():
    # 这里放你之前整理好的完整 df 代码
    # 为了演示简略，假设 df 已经存在
    return df 

df = load_data()

# --- 导航逻辑 ---
if 'view' not in st.session_state:
    st.session_state.view = 'main'

# ==========================================
# LEVEL 1: 主展示与对比页面
# ==========================================
if st.session_state.view == 'main':
    st.title("🎮 CS2 Global Top 5 Teams Analysis")
    
    # 1. 检索窗口 (多选)
    selected_teams = st.multiselect(
        "Select Teams to Compare:", 
        options=df['Team'].unique(),
        default=df['Team'].unique()
    )
    
    # 过滤数据
    compare_df = df[df['Team'].isin(selected_teams)]
    
    # 2. 可视化图表
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Team Rating Comparison")
        fig, ax = plt.subplots()
        sns.barplot(x='Team', y='Rating', data=compare_df, estimator='mean', ax=ax, palette='magma')
        st.pyplot(fig)
        
    with col2:
        st.subheader("Firepower vs Utility")
        fig2, ax2 = plt.subplots()
        sns.scatterplot(data=compare_df, x='Firepower', y='Utility', hue='Team', size='Rating', ax=ax2)
        st.pyplot(fig2)

    st.divider()

    # 3. 战队入口 (队标矩阵)
    st.subheader("Explore Team Rosters")
    cols = st.columns(5)
    teams = list(df['Team'].unique())
    
    for i, team in enumerate(teams):
        with cols[i]:
            # 显示队标 (需确保你仓库有相应图片)
            # st.image(f"logos/{team.lower()}.png", use_column_width=True) 
            if st.button(f"View {team} Details"):
                st.session_state.selected_team = team
                st.session_state.view = 'details'
                st.rerun()

# ==========================================
# LEVEL 2: 战队详情页面
# ==========================================
elif st.session_state.view == 'details':
    target_team = st.session_state.selected_team
    if st.button("← Back to Dashboard"):
        st.session_state.view = 'main'
        st.rerun()
        
    st.title(f"🛡️ Team {target_team} Roster")
    
    team_data = df[df['Team'] == target_team]
    
    # 使用卡片形式展示队员
    for _, player in team_data.iterrows():
        with st.expander(f"Player: {player['Player']}"):
            c1, c2, c3 = st.columns(3)
            c1.metric("Rating", player['Rating'])
            c2.metric("Firepower", player['Firepower'])
            c3.metric("Role", player['Role'])
            st.progress(player['Rating']/1.5, text="Rating Performance")


