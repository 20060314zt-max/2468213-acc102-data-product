import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ==========================================
# 页面全局配置 (必须写在最前面)
# ==========================================
st.set_page_config(page_title="CS2 Pro Team Hub", layout="wide", initial_sidebar_state="collapsed")

# ==========================================
# 数据加载与处理模块 (已修复缩进与变量作用域)
# ==========================================
@st.cache_data
def load_data():
    # 严格保持 4 个空格的缩进
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
        'Trading': [86, 50, 68, 44, 56, 51, 83, 44, 46, 71, 50, 51, 51, 72, 36, 38, 26, 40, 27, 53, 60, 48, 26, 27, 55],
        'Opening': [80, 85, 32, 55, 15, 79, 50, 10, 85, 32, 83, 47, 73, 30, 25, 65, 17, 23, 69, 65, 66, 85, 17, 68, 69],
        'Clutch': [82, 35, 75, 31, 60, 32, 78, 51, 36, 79, 38, 50, 77, 48, 40, 66, 54, 38, 34, 42, 82, 35, 54, 34, 45],
        'AWP': [94, 1, 0, 1, 0, 0, 92, 0, 0, 2, 0, 0, 92, 0, 1, 91, 0, 0, 2, 7, 92, 0, 0, 2, 1]
    }
    
    # 转换为 DataFrame
    temp_df = pd.DataFrame(raw_data)
    
    # 数据清洗：处理缺失值 '--'
    temp_df['Rating'] = pd.to_numeric(temp_df['Rating'], errors='coerce')
    team_avg = temp_df.groupby('Team')['Rating'].transform('mean')
    temp_df['Rating'] = temp_df['Rating'].fillna(team_avg)
    
    # 特征工程：计算全能指数并划分角色
    temp_df['Combat_Index'] = (temp_df['Firepower'] * 0.4 + temp_df['Entry'] * 0.3 + temp_df['Clutch'] * 0.3).round(1)
    
    def get_role(row):
        if row['AWP'] > 80: return 'Sniper'
        if row['Utility'] > 80: return 'Tactical/IGL'
        if row['Entry'] > 70: return 'Entry Fragger'
        if row['Clutch'] > 70: return 'Clutch Master'
        return 'Rifler'
    
    temp_df['Role'] = temp_df.apply(get_role, axis=1)
    
    return temp_df

# 调用数据 (只会在第一次运行时加载，之后会缓存)
df = load_data()

# ==========================================
# 状态管理 (用于控制在两层页面间跳转)
# ==========================================
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'selected_team' not in st.session_state:
    st.session_state.selected_team = None

# ==========================================
# 页面第一层 (Level 1)：主控制台与图表对比
# ==========================================
if st.session_state.page == 'home':
    st.title("🏆 CS2 Global Top 5 Teams Analytics")
    st.markdown("Select teams below to dynamically compare their performance, or click a team logo to view specific player rosters.")
    st.divider()

    # --- 1. 检索窗口 (支持多选) ---
    all_teams = df['Team'].unique()
    selected_teams = st.multiselect(
        "🔍 Select Teams to Compare:",
        options=all_teams,
        default=all_teams # 默认全选
    )
    
    # 根据检索窗口过滤数据
    if not selected_teams:
        st.warning("Please select at least one team.")
        st.stop()
        
    compare_df = df[df['Team'].isin(selected_teams)]

    # --- 2. 可视化图表 (统一使用英文标签防止乱码) ---
    col1, col2 = st.columns(2)
    sns.set_theme(style="whitegrid")
    
    with col1:
        st.subheader("Team Average Rating")
        fig1, ax1 = plt.subplots(figsize=(8, 5))
        sns.barplot(data=compare_df, x='Team', y='Rating', estimator='mean', hue='Team', palette='viridis', ax=ax1, legend=False)
        ax1.set_ylim(0.8, 1.3)
        st.pyplot(fig1)

    with col2:
        st.subheader("Firepower vs Utility")
        fig2, ax2 = plt.subplots(figsize=(8, 5))
        sns.scatterplot(data=compare_df, x='Firepower', y='Utility', hue='Team', size='Rating', sizes=(100, 400), alpha=0.7, ax=ax2)
        ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        st.pyplot(fig2)

    st.divider()

    # --- 3. 战队入口区 (队标展示与按钮) ---
    st.subheader("🛡️ Explore Team Rosters")
    team_cols = st.columns(len(all_teams))
    
    for i, team in enumerate(all_teams):
        with team_cols[i]:
            # 处理队标图片 (如果 GitHub 仓库有 logos 文件夹且里面有图片则显示，否则显示战队名占位)
            logo_path = f"logos/{team.lower().replace(' ', '')}.png"
            if os.path.exists(logo_path):
                st.image(logo_path, use_container_width=True)
            else:
                st.markdown(f"**[{team} Logo]**")
                
            # 跳转按钮
            if st.button(f"Enter {team}", key=f"btn_{team}", use_container_width=True):
                st.session_state.selected_team = team
                st.session_state.page = 'detail'
                st.rerun() # 触发页面重载，进入 Level 2

# ==========================================
# 页面第二层 (Level 2)：单个战队详细数据
# ==========================================
elif st.session_state.page == 'detail':
    target_team = st.session_state.selected_team
    
    # 返回按钮
    if st.button("⬅️ Back to Dashboard"):
        st.session_state.page = 'home'
        st.rerun()
        
    st.title(f"🚀 {target_team} Active Roster")
    st.divider()
    
    # 过滤出当前点击的战队数据
    team_data = df[df['Team'] == target_team].reset_index(drop=True)
    
    # 使用 Metric 卡片展示数据概览
    st.subheader("Team Overview")
    avg_rating = team_data['Rating'].mean()
    avg_firepower = team_data['Firepower'].mean()
    st.metric(label="Team Average Rating", value=f"{avg_rating:.2f}")
    
    # 详细队员数据表格
    st.subheader("Player Data")
    
    # 优化展示的列顺序
    display_cols = ['Player', 'Role', 'Rating', 'Combat_Index', 'Firepower', 'Utility', 'Entry', 'Clutch', 'AWP']
    
    # 使用 st.dataframe 渲染交互式表格 (用户可以在网页上排序)
    st.dataframe(
        team_data[display_cols].style.highlight_max(subset=['Rating', 'Firepower', 'Utility'], color='lightgreen', axis=0),
        use_container_width=True,
        hide_index=True
    )
