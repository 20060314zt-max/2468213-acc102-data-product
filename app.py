import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import io

# ==========================================
# 页面全局配置 (修改为更宽的布局和自定义主题色彩)
# ==========================================
st.set_page_config(page_title="CS2 Pro Player Analytics Pro Max", layout="wide", page_icon="🎮")
sns.set_theme(style="darkgrid", context="talk") # 设置更专业的 seaborn 主题

# ==========================================
# 核心辅助函数：绘制雷达图 (电竞经典六边形)
# ==========================================
def plot_radar_chart(player_series, categories, title, color):
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    values = player_series[categories].values.flatten().tolist()
    values += values[:1] # 闭合图形
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    ax.fill(angles, values, color=color, alpha=0.3)
    ax.plot(angles, values, color=color, linewidth=2)
    ax.set_yticklabels([]) # 隐藏极坐标同心圆的数字
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=10, weight='bold')
    ax.set_title(title, size=14, color=color, y=1.1)
    return fig

# ==========================================
# 核心数据加载 (扩充了 Impact 和 KAST 等进阶数据)
# ==========================================
@st.cache_data
def load_raw_data():
    raw_data = {
        'Team': ['Vitality']*5 + ['NAVI']*5 + ['Astralis']*5 + ['The MongolZ']*5 + ['Aurora']*5,
        'Player': [
            'ZywOo', 'flameZ', 'Spinx', 'apEX', 'mezii', 'iM', 'w0nderful', 'Aleksib', 'jL', 'b1t',
            'Staehr', 'jabbi', 'phzy', 'ryu', 'HooXi', '910', 'mzinho', 'Techno', 'bLitz', 'cobrazera',
            'deko', 'r3salt', 'Norwi', 'Lack1', 'KENSI'
        ],
        'Rating': [1.30, 1.15, 1.14, 1.02, 1.03, 1.09, 1.07, 0.91, 1.10, 1.09, 1.11, 1.06, '--', '--', 0.84, 1.05, 1.04, 0.97, 0.95, '--', 1.15, 1.13, 1.05, 0.98, 1.10],
        'Impact': [1.42, 1.18, 1.15, 0.98, 1.00, 1.12, 1.05, 0.85, 1.15, 1.08, 1.10, 1.04, '--', '--', 0.78, 1.08, 1.01, 0.95, 0.99, '--', 1.20, 1.16, 1.08, 0.95, 1.12],
        'KAST_%': [76, 73, 74, 69, 71, 72, 74, 70, 71, 72, 73, 72, '--', '--', 68, 71, 70, 69, 72, '--', 75, 73, 71, 69, 72],
        'Firepower': [92, 80, 75, 35, 51, 72, 53, 4, 86, 60, 85, 68, 74, 44, 6, 72, 50, 24, 28, 65, 86, 85, 62, 25, 78],
        'Utility': [52, 54, 51, 89, 72, 35, 54, 89, 52, 51, 79, 48, 62, 32, 81, 60, 45, 46, 94, 35, 35, 56, 45, 91, 45],
        'Entry': [56, 70, 42, 85, 24, 66, 28, 86, 90, 33, 62, 69, 22, 79, 52, 6, 52, 51, 42, 41, 36, 82, 52, 42, 66],
        'Clutch': [82, 35, 75, 31, 60, 32, 78, 51, 36, 79, 38, 50, 77, 48, 40, 66, 54, 38, 34, 42, 82, 35, 54, 34, 45],
        'AWP': [94, 1, 0, 1, 0, 0, 92, 0, 0, 2, 0, 0, 92, 0, 1, 91, 0, 0, 2, 7, 92, 0, 0, 2, 1]
    }
    return pd.DataFrame(raw_data)

df_raw = load_raw_data()

# ------------------------------------------
# 数据清洗与特征工程流水线
# ------------------------------------------
df_clean = df_raw.copy()
# 批量处理包含 '--' 的列
for col in ['Rating', 'Impact', 'KAST_%']:
    df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
    team_avg = df_clean.groupby('Team')[col].transform('mean')
    df_clean[col] = df_clean[col].fillna(team_avg).round(2)

df_analyzed = df_clean.copy()
# 计算综合战斗指数 (新增标准化处理)
df_analyzed['Combat_Index'] = (df_analyzed['Firepower']*0.35 + df_analyzed['Entry']*0.25 + df_analyzed['Clutch']*0.2 + df_analyzed['Utility']*0.2).round(1)

def get_role(row):
    if row['AWP'] > 75: return 'Sniper'
    if row['Utility'] > 75 and row['Firepower'] < 50: return 'Tactical IGL'
    if row['Entry'] > 75: return 'Entry Fragger'
    return 'Rifler / Support'
df_analyzed['Role'] = df_analyzed.apply(get_role, axis=1)

# ==========================================
# 侧边栏：全局数据过滤 (Interactive Sidebar)
# ==========================================
st.sidebar.image("https://cdn.akamai.steamstatic.com/apps/csgo/images/csgo_react/global/logo_cs_sm_global.svg", width=150)
st.sidebar.header("⚙️ Global Filters")
st.sidebar.markdown("Use these controls to filter the entire dataset below.")

min_rating = st.sidebar.slider("Minimum Rating", min_value=0.8, max_value=1.4, value=0.9, step=0.01)
selected_roles = st.sidebar.multiselect("Filter by Role", options=df_analyzed['Role'].unique(), default=df_analyzed['Role'].unique())

# 应用过滤
df_filtered = df_analyzed[(df_analyzed['Rating'] >= min_rating) & (df_analyzed['Role'].isin(selected_roles))]

# ==========================================
# 状态管理
# ==========================================
if 'page' not in st.session_state: st.session_state.page = 'home'

# ==========================================
# 页面逻辑 - 首页
# ==========================================
if st.session_state.page == 'home':
    st.title("🏆 CS2 Pro Player Analytical Pipeline")
    st.markdown("A highly interactive dashboard for exploring team rosters and player statistics.")
    
    # 核心四大功能标签页
    tabs = st.tabs(["🔍 Raw Data", "🧹 Cleaning & Pipeline", "📊 Viz: Distributions", "⚔️ Viz: Player Battles"])

    # --- TAB 1: 原始数据 ---
    with tabs[0]:
        st.subheader("Raw Data Inspection")
        st.dataframe(df_raw, use_container_width=True, height=250)
        st.error(f"⚠️ Anomaly Detected: Found {df_raw['Rating'].astype(str).str.contains('--').sum()} missing values marked as '--'.")

    # --- TAB 2: 清洗与导出 ---
    with tabs[1]:
        st.subheader("Automated Imputation & Engineering")
        col1, col2 = st.columns(2)
        with col1:
            st.success("Imputation Rules: Missing values replaced by Team Averages.")
            st.dataframe(df_filtered[['Player', 'Team', 'Rating', 'Impact', 'KAST_%', 'Role']].head(8), use_container_width=True)
        with col2:
            st.info("Feature Engineered: 'Role' derived from AWP, Utility, and Entry stats.")
            # 添加 CSV 下载功能
            csv = df_filtered.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Cleaned Dataset (CSV)", csv, "cs2_cleaned_data.csv", "text/csv", use_container_width=True)

    # --- TAB 3: 数据分布可视化 (宏观) ---
    with tabs[2]:
        st.header("Macro Statistical Distributions")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Team Rating Spread (Boxplot)")
            fig, ax = plt.subplots(figsize=(8, 5))
            sns.boxplot(data=df_filtered, x='Team', y='Rating', palette='Set3', ax=ax)
            sns.swarmplot(data=df_filtered, x='Team', y='Rating', color=".25", size=6, ax=ax) # 添加散点显示具体分布
            plt.xticks(rotation=45)
            st.pyplot(fig)
            
        with c2:
            st.markdown("#### Stat Correlation (Heatmap)")
            # 只提取数值列画热力图
            numeric_cols = df_filtered[['Rating', 'Impact', 'KAST_%', 'Firepower', 'Utility', 'Entry', 'Clutch', 'Combat_Index']]
            fig, ax = plt.subplots(figsize=(8, 5))
            corr = numeric_cols.corr()
            sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", linewidths=.5, ax=ax)
            st.pyplot(fig)

    # --- TAB 4: 选手对比可视化 (微观) ---
    with tabs[3]:
        st.header("Micro Player Analytics & Battles")
        
        # 气泡图
        st.markdown("#### Utility vs Firepower vs Rating (Bubble Chart)")
        fig, ax = plt.subplots(figsize=(10, 4))
        scatter = sns.scatterplot(data=df_filtered, x='Firepower', y='Utility', hue='Role', 
                                  size='Rating', sizes=(50, 600), alpha=0.7, palette='husl', ax=ax)
        # 为高评分选手添加文字标签
        for i in range(df_filtered.shape[0]):
            if df_filtered.iloc[i]['Rating'] > 1.12:
                ax.text(df_filtered.iloc[i]['Firepower']+1, df_filtered.iloc[i]['Utility'], 
                        df_filtered.iloc[i]['Player'], fontsize=9, weight='bold')
        st.pyplot(fig)
        
        st.divider()

    # --- 战队入口点 (保留核心功能并美化) ---
    st.subheader("🛡️ Team Deep Dive")
    st.markdown("Select a team to view detailed 5-player roster data and individual capability radars.")
    teams = df_analyzed['Team'].unique()
    team_cols = st.columns(len(teams))
    
    for i, t in enumerate(teams):
        with team_cols[i]:
            # 模拟高大上的战队卡片
            st.markdown(f"<div style='text-align:center; padding:10px; border-radius:5px; background-color:#1e1e2e; margin-bottom:10px;'><b>{t}</b></div>", unsafe_allow_html=True)
            if st.button(f"Analyze", key=f"btn_{t}", use_container_width=True):
                st.session_state.selected_team = t
                st.session_state.page = 'detail'
                st.rerun()

# ==========================================
# 页面逻辑 - 战队详情页
# ==========================================
elif st.session_state.page == 'detail':
    target = st.session_state.selected_team
    
    # 顶部导航
    col_nav1, col_nav2 = st.columns([1, 8])
    with col_nav1:
        if st.button("⬅ Back"):
            st.session_state.page = 'home'
            st.rerun()
    with col_nav2:
        st.title(f"🚀 {target} Franchise Report")
    
    team_data = df_analyzed[df_analyzed['Team'] == target]
    global_avg_rating = df_analyzed['Rating'].mean()
    global_avg_impact = df_analyzed['Impact'].mean()
    
    # 动态 KPI 指标卡片 (带对比功能)
    st.subheader("Team Global Metrics")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Avg Rating", f"{team_data['Rating'].mean():.2f}", f"{(team_data['Rating'].mean() - global_avg_rating):.2f} vs Global")
    kpi2.metric("Avg Impact", f"{team_data['Impact'].mean():.2f}", f"{(team_data['Impact'].mean() - global_avg_impact):.2f} vs Global")
    kpi3.metric("Highest Rating", team_data['Rating'].max(), f"Player: {team_data.loc[team_data['Rating'].idxmax(), 'Player']}")
    kpi4.metric("Team Combat Index", f"{team_data['Combat_Index'].sum():.1f}")
    
    st.divider()
    
    # 详情页双栏复杂排版
    col_l, col_r = st.columns([1.5, 1])
    
    with col_l:
        st.markdown("#### Roster Attribute Composition")
        # 堆叠条形图
        fig_team, ax_team = plt.subplots(figsize=(8, 5))
        team_melted = team_data.melt(id_vars='Player', value_vars=['Firepower', 'Utility', 'Entry', 'Clutch'])
        sns.barplot(data=team_melted, x='value', y='Player', hue='variable', palette='magma', ax=ax_team)
        ax_team.set_xlabel("Stat Value")
        st.pyplot(fig_team)
        
        st.markdown("#### Roster Data Table")
        st.dataframe(team_data.drop(columns=['Team']).style.background_gradient(cmap='viridis', subset=['Rating', 'Combat_Index']), use_container_width=True, hide_index=True)

    with col_r:
        st.markdown("#### Role Distribution")
        # 战队角色饼图
        role_counts = team_data['Role'].value_counts()
        fig_pie, ax_pie = plt.subplots(figsize=(5, 5))
        ax_pie.pie(role_counts, labels=role_counts.index, autopct='%1.1f%%', startangle=90, colors=sns.color_palette('pastel'))
        ax_pie.axis('equal')
        st.pyplot(fig_pie)
        
        # 互动雷达图：选中该队某位选手查看详细雷达图
        st.markdown("#### Player Spotlight Radar")
        selected_player = st.selectbox("Select Player for Detailed Radar:", team_data['Player'].tolist())
        player_stats = team_data[team_data['Player'] == selected_player].iloc[0]
        
        # 绘制雷达图
        radar_categories = ['Firepower', 'Utility', 'Entry', 'Clutch', 'AWP']
        fig_radar = plot_radar_chart(player_stats, radar_categories, f"{selected_player}'s Pentagon", '#00ffcc')
        st.pyplot(fig_radar)

