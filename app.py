import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 页面配置
st.set_page_config(page_title="CS2 Pro Team Analysis", layout="wide")

# --- 数据载入 (直接复用你之前的 df) ---
@st.cache_data
def load_data():
    # --- 数据载入函数 ---
@st.cache_data
def load_data():
    # 核心修复：在这里定义原始数据 raw_data
    raw_data = {
        'Team': [
            'Vitality', 'Vitality', 'Vitality', 'Vitality', 'Vitality',
            'NAVI', 'NAVI', 'NAVI', 'NAVI', 'NAVI',
            'Astralis', 'Astralis', 'Astralis', 'Astralis', 'Astralis',
            'The MongolZ', 'The MongolZ', 'The MongolZ', 'The MongolZ', 'The MongolZ',
            'Aurora', 'Aurora', 'Aurora', 'Aurora', 'Aurora'
        ],
        'Player': [
            'ZywOo', 'flameZ', 'Spinx', 'apEX', 'mezii',
            'iM', 'w0nderful', 'Aleksib', 'jL', 'b1t',
            'Staehr', 'jabbi', 'phzy', 'ryu', 'HooXi',
            '910', 'mzinho', 'Techno', 'bLitz', 'cobrazera',
            'deko', 'r3salt', 'Norwi', 'Lack1', 'KENSI'
        ],
        'Rating': [
            1.30, 1.15, 1.14, 1.02, 1.03,
            1.09, 1.07, 0.91, 1.10, 1.09,
            1.11, 1.06, '--', '--', 0.84,
            1.05, 1.04, 0.97, 0.95, '--',
            1.15, 1.13, 1.05, 0.98, 1.10
        ],
        'Firepower': [92, 80, 75, 35, 51, 72, 53, 4, 86, 60, 85, 68, 74, 44, 6, 72, 50, 24, 28, 65, 86, 85, 62, 25, 78],
        'Utility': [52, 54, 51, 89, 72, 35, 54, 89, 52, 51, 79, 48, 62, 32, 81, 60, 45, 46, 94, 35, 35, 56, 45, 91, 45],
        'Entry': [56, 70, 42, 85, 24, 66, 28, 86, 90, 33, 62, 69, 22, 79, 52, 6, 52, 51, 42, 41, 36, 82, 52, 42, 66],
        'AWP': [94, 1, 0, 1, 0, 0, 92, 0, 0, 2, 0, 0, 92, 0, 1, 91, 0, 0, 2, 7, 92, 0, 0, 2, 1],
        'Clutch': [82, 35, 75, 31, 60, 32, 78, 51, 36, 79, 38, 50, 77, 48, 40, 66, 54, 38, 34, 42, 82, 35, 54, 34, 45]
    }
    
    # 实例化 DataFrame
    temp_df = pd.DataFrame(raw_data)
    
    # 数据清洗：处理 '--'
    temp_df['Rating'] = pd.to_numeric(temp_df['Rating'], errors='coerce')
    team_avg = temp_df.groupby('Team')['Rating'].transform('mean')
    temp_df['Rating'] = temp_df['Rating'].fillna(team_avg)
    
    # 角色分类
    def get_role(row):
        if row['AWP'] > 80: return 'Sniper'
        if row['Utility'] > 80: return 'Tactical/IGL'
        if row['Entry'] > 70: return 'Entry Fragger'
        return 'Rifler'
    temp_df['Role'] = temp_df.apply(get_role, axis=1)
    
    return temp_df # 返回处理好的 DataFrame

# 调用函数获取 df
df = load_data()

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


