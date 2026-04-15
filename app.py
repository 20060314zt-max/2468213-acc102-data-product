import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# ==========================================
# 页面全局配置
# ==========================================
st.set_page_config(page_title="CS2 Pro Player Analytics", layout="wide")

# ==========================================
# 核心数据加载 (包含原始数据用于演示清洗流程)
# ==========================================
@st.cache_data
def load_raw_data():
    raw_data = {
        'Team': ['Vitality']*5 + ['NAVI']*5 + ['Astralis']*5 + ['The MongolZ']*5 + ['Aurora']*5,
        'Player': [
            'ZywOo', 'flameZ', 'Spinx', 'apEX', 'mezii',
            'iM', 'w0nderful', 'Aleksib', 'jL', 'b1t',
            'Staehr', 'jabbi', 'phzy', 'ryu', 'HooXi',
            '910', 'mzinho', 'Techno', 'bLitz', 'cobrazera',
            'deko', 'r3salt', 'Norwi', 'Lack1', 'KENSI'
        ],
        'Rating': [1.30, 1.15, 1.14, 1.02, 1.03, 1.09, 1.07, 0.91, 1.10, 1.09, 1.11, 1.06, '--', '--', 0.84, 1.05, 1.04, 0.97, 0.95, '--', 1.15, 1.13, 1.05, 0.98, 1.10],
        'Firepower': [92, 80, 75, 35, 51, 72, 53, 4, 86, 60, 85, 68, 74, 44, 6, 72, 50, 24, 28, 65, 86, 85, 62, 25, 78],
        'Utility': [52, 54, 51, 89, 72, 35, 54, 89, 52, 51, 79, 48, 62, 32, 81, 60, 45, 46, 94, 35, 35, 56, 45, 91, 45],
        'Entry': [56, 70, 42, 85, 24, 66, 28, 86, 90, 33, 62, 69, 22, 79, 52, 6, 52, 51, 42, 41, 36, 82, 52, 42, 66],
        'Clutch': [82, 35, 75, 31, 60, 32, 78, 51, 36, 79, 38, 50, 77, 48, 40, 66, 54, 38, 34, 42, 82, 35, 54, 34, 45],
        'AWP': [94, 1, 0, 1, 0, 0, 92, 0, 0, 2, 0, 0, 92, 0, 1, 91, 0, 0, 2, 7, 92, 0, 0, 2, 1]
    }
    return pd.DataFrame(raw_data)

# 初始化数据流水线
df_raw = load_raw_data()

# ------------------------------------------
# 自动数据处理 (Pipeline)
# ------------------------------------------
df_clean = df_raw.copy()
df_clean['Rating'] = pd.to_numeric(df_clean['Rating'], errors='coerce')
team_avg = df_clean.groupby('Team')['Rating'].transform('mean')
df_clean['Rating'] = df_clean['Rating'].fillna(team_avg).round(2)

df_analyzed = df_clean.copy()
df_analyzed['Combat_Index'] = (df_analyzed['Firepower']*0.4 + df_analyzed['Entry']*0.3 + df_analyzed['Clutch']*0.3).round(1)
def get_role(row):
    if row['AWP'] > 80: return 'Sniper'
    if row['Utility'] > 80: return 'Tactical/IGL'
    return 'Rifler'
df_analyzed['Role'] = df_analyzed.apply(get_role, axis=1)

# ==========================================
# 状态管理
# ==========================================
if 'page' not in st.session_state: st.session_state.page = 'home'

# ==========================================
# 页面逻辑
# ==========================================
if st.session_state.page == 'home':
    st.title("🏆 CS2 Top 25 Players Analytical Pipeline")
    
    # 顶部流程标签
    tabs = st.tabs(["🔍 Data Exploration", "🧹 Cleaning", "🧮 Analysis", "📊 Visualization"])

    with tabs[0]:
        st.subheader("Raw Data Inspection")
        st.dataframe(df_raw.head(10))
        st.warning("Detection: Found '--' placeholders in Rating column.")

    with tabs[1]:
        st.subheader("Imputation Results")
        st.write("Cleaned Data (Mean Imputation by Team):")
        st.dataframe(df_clean.iloc[[12, 13, 19]]) # 展示修复行

    with tabs[2]:
        st.subheader("Feature Engineering")
        st.write("Added 'Combat_Index' and 'Role' classification.")
        st.dataframe(df_analyzed.head(5))

    with tabs[3]:
        st.header("Global 25-Player Comparison")
        # 25人横向大横评
        all_players = df_analyzed['Player'].tolist()
        selected = st.multiselect("Select Specific Players to Compare:", all_players, default=all_players[:12])
        
        pdf = df_analyzed[df_analyzed['Player'].isin(selected)]
        if not pdf.empty:
            c1, c2 = st.columns(2)
            with c1:
                fig1, ax1 = plt.subplots(figsize=(8, 6))
                sns.barplot(data=pdf.sort_values('Rating'), x='Rating', y='Player', hue='Team', ax=ax1)
                ax1.set_xlim(0.8, 1.35)
                st.pyplot(fig1)
            with c2:
                fig2, ax2 = plt.subplots(figsize=(8, 6))
                sns.scatterplot(data=pdf, x='Firepower', y='Utility', hue='Role', size='Rating', sizes=(100, 500), ax=ax2)
                st.pyplot(fig2)

        st.divider()

        # --- 核心保留功能：五个战队入口点 ---
        st.subheader("🛡️ Team Deep Dive")
        st.markdown("Click a team to view their specific 5-player roster data.")
        teams = df_analyzed['Team'].unique()
        team_cols = st.columns(len(teams))
        
        for i, t in enumerate(teams):
            with team_cols[i]:
                st.info(f"**{t}**")
                # 检查是否有 logo，没有则显示文字
                logo_path = f"logos/{t.lower()}.png"
                if os.path.exists(logo_path):
                    st.image(logo_path, use_container_width=True)
                
                if st.button(f"View {t} Roster", key=f"btn_{t}", use_container_width=True):
                    st.session_state.selected_team = t
                    st.session_state.page = 'detail'
                    st.rerun()

elif st.session_state.page == 'detail':
    target = st.session_state.selected_team
    if st.button("⬅ Back to Global Analysis"):
        st.session_state.page = 'home'
        st.rerun()
    
    st.header(f"🚀 {target} Roster Performance")
    team_data = df_analyzed[df_analyzed['Team'] == target]
    
    # 该战队的内部数据展示
    col_l, col_r = st.columns([1, 2])
    with col_l:
        st.metric("Avg Team Rating", round(team_data['Rating'].mean(), 2))
        st.write("Active Roster:")
        st.dataframe(team_data[['Player', 'Role', 'Rating']], hide_index=True)
    
    with col_r:
        # 战队内部各成员属性对比
        fig_team, ax_team = plt.subplots()
        team_melted = team_data.melt(id_vars='Player', value_vars=['Firepower', 'Utility', 'Entry', 'Clutch'])
        sns.barplot(data=team_melted, x='value', y='Player', hue='variable', ax=ax_team)
        st.pyplot(fig_team)
    
    # 使用 st.dataframe 渲染交互式表格 (用户可以在网页上排序)
    st.dataframe(
        team_data[display_cols].style.highlight_max(subset=['Rating', 'Firepower', 'Utility'], color='lightgreen', axis=0),
