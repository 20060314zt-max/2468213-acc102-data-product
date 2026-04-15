import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# ==========================================
# 页面全局配置
# ==========================================
st.set_page_config(page_title="CS2 Pro Player Analytics Pro Max", layout="wide", page_icon="🎮")
sns.set_theme(style="darkgrid", context="talk")

# 辅助函数：绘制雷达图
def plot_radar_chart(player_series, categories, title, color):
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    values = player_series[categories].values.flatten().tolist()
    values += values[:1]
    angles += angles[:1]
    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    ax.fill(angles, values, color=color, alpha=0.3)
    ax.plot(angles, values, color=color, linewidth=2)
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=10, weight='bold')
    ax.set_title(title, size=14, color=color, y=1.1)
    return fig

# ==========================================
# 数据加载与集成 Pipeline (已合并精简)
# ==========================================
@st.cache_data
def get_processed_data():
    raw_data = {
        'Team': ['Vitality']*5 + ['NAVI']*5 + ['Astralis']*5 + ['The MongolZ']*5 + ['Aurora']*5,
        'Player': ['ZywOo', 'flameZ', 'Spinx', 'apEX', 'mezii', 'iM', 'w0nderful', 'Aleksib', 'jL', 'b1t', 'Staehr', 'jabbi', 'phzy', 'ryu', 'HooXi', '910', 'mzinho', 'Techno', 'bLitz', 'cobrazera', 'deko', 'r3salt', 'Norwi', 'Lack1', 'KENSI'],
        'Rating': [1.30, 1.15, 1.14, 1.02, 1.03, 1.09, 1.07, 0.91, 1.10, 1.09, 1.11, 1.06, '--', '--', 0.84, 1.05, 1.04, 0.97, 0.95, '--', 1.15, 1.13, 1.05, 0.98, 1.10],
        'Impact': [1.42, 1.18, 1.15, 0.98, 1.00, 1.12, 1.05, 0.85, 1.15, 1.08, 1.10, 1.04, 1.05, 1.01, 0.78, 1.08, 1.01, 0.95, 0.99, 1.02, 1.20, 1.16, 1.08, 0.95, 1.12],
        'Firepower': [92, 80, 75, 35, 51, 72, 53, 4, 86, 60, 85, 68, 74, 44, 6, 72, 50, 24, 28, 65, 86, 85, 62, 25, 78],
        'Utility': [52, 54, 51, 89, 72, 35, 54, 89, 52, 51, 79, 48, 62, 32, 81, 60, 45, 46, 94, 35, 35, 56, 45, 91, 45],
        'Entry': [56, 70, 42, 85, 24, 66, 28, 86, 90, 33, 62, 69, 22, 79, 52, 6, 52, 51, 42, 41, 36, 82, 52, 42, 66],
        'Clutch': [82, 35, 75, 31, 60, 32, 78, 51, 36, 79, 38, 50, 77, 48, 40, 66, 54, 38, 34, 42, 82, 35, 54, 34, 45],
        'AWP': [94, 1, 0, 1, 0, 0, 92, 0, 0, 2, 0, 0, 92, 0, 1, 91, 0, 0, 2, 7, 92, 0, 0, 2, 1]
    }
    df = pd.DataFrame(raw_data)
    # Pipeline: 处理缺失值
    df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')
    df['Rating'] = df['Rating'].fillna(df.groupby('Team')['Rating'].transform('mean')).round(2)
    # Pipeline: 特征工程
    df['Combat_Index'] = (df['Firepower']*0.4 + df['Entry']*0.3 + df['Clutch']*0.3).round(1)
    def get_role(row):
        if row['AWP'] > 75: return 'Sniper'
        if row['Utility'] > 75: return 'Tactical/IGL'
        return 'Rifler'
    df['Role'] = df.apply(get_role, axis=1)
    return df

df_analyzed = get_processed_data()

# ==========================================
# 侧边栏：全局数据过滤 (保持不变)
# ==========================================
st.sidebar.image("https://cdn.akamai.steamstatic.com/apps/csgo/images/csgo_react/global/logo_cs_sm_global.svg", width=150)
st.sidebar.header("⚙️ Global Filters")
min_rating = st.sidebar.slider("Minimum Rating", 0.8, 1.4, 0.9, 0.01)
selected_roles = st.sidebar.multiselect("Filter by Role", options=df_analyzed['Role'].unique(), default=df_analyzed['Role'].unique())

df_filtered = df_analyzed[(df_analyzed['Rating'] >= min_rating) & (df_analyzed['Role'].isin(selected_roles))]

# 状态管理
if 'page' not in st.session_state: st.session_state.page = 'home'

# ==========================================
# 页面逻辑 - 首页
# ==========================================
if st.session_state.page == 'home':
    st.title("🏆 CS2 Top 25 Players Analytical Pipeline")
    
    # --- 新的合并版 Pipeline 展示 ---
    with st.expander("🛠️ Data Pipeline & Cleaning Summary", expanded=False):
        c1, c2 = st.columns(2)
        c1.write("**Step 1: Raw Data Cleaning**")
        c1.info("Detected '--' in Rating. Applied Team-Mean Imputation.")
        c2.write("**Step 2: Feature Engineering**")
        c2.info("Calculated 'Combat_Index' & Assigned Roles based on Stats.")
        st.dataframe(df_filtered[['Player', 'Team', 'Rating', 'Role', 'Combat_Index']].head(5), use_container_width=True)

    # --- 大幅强化：可视化分析区 (可长拉滚动) ---
    st.header("📊 Global Player Analysis")
    
    # 第一行：统计学分布 (热力图 + 箱线图)
    col_stat1, col_stat2 = st.columns(2)
    with col_stat1:
        st.subheader("Correlation Heatmap")
        fig_h, ax_h = plt.subplots(figsize=(10, 8))
        corr = df_filtered[['Rating', 'Impact', 'Firepower', 'Utility', 'Entry', 'Clutch', 'Combat_Index']].corr()
        sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", ax=ax_h)
        st.pyplot(fig_h)
    
    with col_stat2:
        st.subheader("Team Rating Distribution")
        fig_b, ax_b = plt.subplots(figsize=(10, 8))
        sns.boxplot(data=df_filtered, x='Team', y='Rating', palette='Set3', ax=ax_b)
        sns.swarmplot(data=df_filtered, x='Team', y='Rating', color=".25", ax=ax_b)
        st.pyplot(fig_b)

    st.divider()

    # 第二行：25人多维度大数据对比 (丰富化改写)
    st.header("⚔️ The Big 25-Player Showdown")
    st.markdown("下面是针对全量选手的多角度竞技指标分析，请向下滑动查看详细内容。")

    # 1. 评分与影响力排位 (横向对比)
    st.subheader("1. Elite Performance: Rating vs Impact")
    fig_comp1, ax_comp1 = plt.subplots(figsize=(12, 10))
    # 按照Rating排序显示
    df_sorted = df_filtered.sort_values('Rating', ascending=True)
    ax_comp1.barh(df_sorted['Player'], df_sorted['Rating'], color='skyblue', label='Rating', alpha=0.7)
    ax_comp1.barh(df_sorted['Player'], df_sorted['Impact']-df_sorted['Rating'], left=df_sorted['Rating'], color='orange', label='Impact Extra', alpha=0.5)
    ax_comp1.set_xlim(0.7, 1.5)
    ax_comp1.legend()
    st.pyplot(fig_comp1)

    # 2. 进攻性与残局能力对比 (散点坐标系)
    st.subheader("2. Playstyle Logic: Entry Fraggers vs Clutch Kings")
    fig_comp2, ax_comp2 = plt.subplots(figsize=(12, 7))
    for i, row in df_filtered.iterrows():
        ax_comp2.scatter(row['Entry'], row['Clutch'], s=row['Rating']*200, alpha=0.6)
        ax_comp2.text(row['Entry']+1, row['Clutch']+1, row['Player'], fontsize=10)
    ax_comp2.set_xlabel("Entry Capability")
    ax_comp2.set_ylabel("Clutch Capability")
    ax_comp2.axhline(50, color='grey', linestyle='--')
    ax_comp2.axvline(50, color='grey', linestyle='--')
    st.pyplot(fig_comp2)

    # 3. 战斗指数排名 (战斗力直方图)
    st.subheader("3. Raw Firepower: Global Combat Index Ranking")
    fig_comp3, ax_comp3 = plt.subplots(figsize=(12, 6))
    sns.barplot(data=df_filtered.sort_values('Combat_Index', ascending=False), x='Player', y='Combat_Index', hue='Role', ax=ax_comp3)
    plt.xticks(rotation=45)
    st.pyplot(fig_comp3)

    st.divider()

    # --- 战队入口点 (修改：底色改为白色) ---
    st.subheader("🛡️ Team Roster Access")
    teams = df_analyzed['Team'].unique()
    team_cols = st.columns(len(teams))
    
    for i, t in enumerate(teams):
        with team_cols[i]:
            # 修改底色为白色 (background-color: white)
            st.markdown(f"""
                <div style='text-align:center; padding:10px; border-radius:5px; border:1px solid #ddd; background-color:white; color:black; margin-bottom:10px;'>
                    <b>{t}</b>
                </div>
                """, unsafe_allow_html=True)
            if st.button(f"Details: {t}", key=f"btn_{t}", use_container_width=True):
                st.session_state.selected_team = t
                st.session_state.page = 'detail'
                st.rerun()

# ==========================================
# 页面逻辑 - 战队详情页 (保持原有逻辑)
# ==========================================
elif st.session_state.page == 'detail':
    target = st.session_state.selected_team
    if st.button("⬅ Back to Global Analysis"):
        st.session_state.page = 'home'
        st.rerun()
    
    st.header(f"🚀 {target} Roster Performance")
    team_data = df_analyzed[df_analyzed['Team'] == target]
    
    col_l, col_r = st.columns([1, 2])
    with col_l:
        st.metric("Avg Team Rating", f"{team_data['Rating'].mean():.2f}")
        st.dataframe(team_data[['Player', 'Role', 'Rating']], hide_index=True)
    
    with col_r:
        fig_team, ax_team = plt.subplots()
        team_melted = team_data.melt(id_vars='Player', value_vars=['Firepower', 'Utility', 'Entry', 'Clutch'])
        sns.barplot(data=team_melted, x='value', y='Player', hue='variable', ax=ax_team)
        st.pyplot(fig_team)
        
        # 详情页的小福利：增加该队雷达图展示
        st.divider()
        st.subheader("Player Radar Comparison")
        sel_p = st.selectbox("Select Player:", team_data['Player'].unique())
        p_stats = team_data[team_data['Player'] == sel_p].iloc[0]
        st.pyplot(plot_radar_chart(p_stats, ['Firepower', 'Utility', 'Entry', 'Clutch', 'AWP'], f"{sel_p} Stats", "green"))




