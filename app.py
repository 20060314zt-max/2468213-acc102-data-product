import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# ==========================================
# 1. 页面配置与主题
# ==========================================
st.set_page_config(page_title="CS2 Analytics Pro", layout="wide", page_icon="🎮")
sns.set_theme(style="darkgrid", context="notebook")

# 辅助函数：雷达图
def plot_radar(player_series, categories, color):
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    values = player_series[categories].values.flatten().tolist()
    values += values[:1]
    angles += angles[:1]
    fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))
    ax.fill(angles, values, color=color, alpha=0.25)
    ax.plot(angles, values, color=color, linewidth=2)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=9)
    ax.set_yticklabels([])
    return fig

# ==========================================
# 2. 数据加载与集成 Pipeline
# ==========================================
@st.cache_data
def get_processed_data():
    # 原始数据
    raw = {
        'Team': ['Vitality']*5 + ['NAVI']*5 + ['Astralis']*5 + ['The MongolZ']*5 + ['Aurora']*5,
        'Player': ['ZywOo', 'flameZ', 'Spinx', 'apEX', 'mezii', 'iM', 'w0nderful', 'Aleksib', 'jL', 'b1t',
                   'Staehr', 'jabbi', 'phzy', 'ryu', 'HooXi', '910', 'mzinho', 'Techno', 'bLitz', 'cobrazera',
                   'deko', 'r3salt', 'Norwi', 'Lack1', 'KENSI'],
        'Rating': [1.30, 1.15, 1.14, 1.02, 1.03, 1.09, 1.07, 0.91, 1.10, 1.09, 1.11, 1.06, '--', '--', 0.84, 1.05, 1.04, 0.97, 0.95, '--', 1.15, 1.13, 1.05, 0.98, 1.10],
        'Firepower': [92, 80, 75, 35, 51, 72, 53, 4, 86, 60, 85, 68, 74, 44, 6, 72, 50, 24, 28, 65, 86, 85, 62, 25, 78],
        'Utility': [52, 54, 51, 89, 72, 35, 54, 89, 52, 51, 79, 48, 62, 32, 81, 60, 45, 46, 94, 35, 35, 56, 45, 91, 45],
        'Entry': [56, 70, 42, 85, 24, 66, 28, 86, 90, 33, 62, 69, 22, 79, 52, 6, 52, 51, 42, 41, 36, 82, 52, 42, 66],
        'Clutch': [82, 35, 75, 31, 60, 32, 78, 51, 36, 79, 38, 50, 77, 48, 40, 66, 54, 38, 34, 42, 82, 35, 54, 34, 45],
        'AWP': [94, 1, 0, 1, 0, 0, 92, 0, 0, 2, 0, 0, 92, 0, 1, 91, 0, 0, 2, 7, 92, 0, 0, 2, 1]
    }
    df = pd.DataFrame(raw)
    
    # 清洗逻辑: '--' 转为均值
    df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')
    df['Rating'] = df['Rating'].fillna(df.groupby('Team')['Rating'].transform('mean')).round(2)
    
    # 特征工程: 角色分配
    def assign_role(row):
        if row['AWP'] > 75: return 'Sniper'
        if row['Utility'] > 75: return 'IGL/Support'
        return 'Rifler'
    df['Role'] = df.apply(assign_role, axis=1)
    return df

df_full = get_processed_data()

# ==========================================
# 3. 侧边栏过滤
# ==========================================
st.sidebar.title("📊 Filter Engine")
selected_teams = st.sidebar.multiselect("Select Teams", options=df_full['Team'].unique(), default=df_full['Team'].unique())
rating_range = st.sidebar.slider("Rating Range", 0.8, 1.4, (0.85, 1.35))

df_view = df_full[(df_full['Team'].isin(selected_teams)) & 
                  (df_full['Rating'].between(rating_range[0], rating_range[1]))]

# ==========================================
# 4. 页面逻辑
# ==========================================
if 'page' not in st.session_state: st.session_state.page = 'home'

if st.session_state.page == 'home':
    st.title("🏆 CS2 Pro Player Dashboard")
    
    tab1, tab2, tab3 = st.tabs(["🚀 Data Pipeline", "📈 Global Analytics", "⚔️ Team Entry"])

    with tab1:
        st.subheader("Combined Data Logic")
        c1, c2 = st.columns(2)
        with c1:
            st.caption("Step 1: Automated Cleaning (Mean Imputation)")
            st.dataframe(df_view[['Player', 'Team', 'Rating']].head(10), use_container_width=True)
        with c2:
            st.caption("Step 2: Role Engineering")
            st.dataframe(df_view[['Player', 'Role', 'Firepower', 'Utility']].head(10), use_container_width=True)

    with tab2:
        col_a, col_b = st.columns([1.2, 1])
        with col_a:
            st.markdown("##### Performance Matrix (Bubble Chart)")
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.scatterplot(data=df_view, x='Firepower', y='Utility', hue='Team', size='Rating', sizes=(100, 700), alpha=0.6, ax=ax)
            st.pyplot(fig)
        with col_b:
            st.markdown("##### Rating Distribution by Role")
            fig2, ax2 = plt.subplots(figsize=(8, 7))
            sns.violinplot(data=df_view, x='Role', y='Rating', palette='pastel', ax=ax2)
            st.pyplot(fig2)

    with tab3:
        st.subheader("Select Team for Deep Dive")
        t_cols = st.columns(len(df_full['Team'].unique()))
        for idx, t_name in enumerate(df_full['Team'].unique()):
            with t_cols[idx]:
                if st.button(t_name, use_container_width=True):
                    st.session_state.selected_team = t_name
                    st.session_state.page = 'detail'
                    st.rerun()

elif st.session_state.page == 'detail':
    target = st.session_state.selected_team
    st.button("⬅ Back to Dashboard", on_click=lambda: setattr(st.session_state, 'page', 'home'))
    
    st.header(f"🛡️ {target} Tactical Report")
    t_df = df_full[df_full['Team'] == target]
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Avg Team Rating", f"{t_df['Rating'].mean():.2f}")
    m2.metric("Star Player", t_df.loc[t_df['Rating'].idxmax(), 'Player'])
    m3.metric("Roster Strength", f"{t_df['Firepower'].sum()}")

    col_x, col_y = st.columns([1.5, 1])
    with col_x:
        st.markdown("##### Skill Breakdown")
        fig_bar, ax_bar = plt.subplots()
        t_df.set_index('Player')[['Firepower', 'Utility', 'Entry', 'Clutch']].plot(kind='barh', stacked=False, ax=ax_bar, colormap='viridis')
        st.pyplot(fig_bar)
    with col_y:
        st.markdown("##### Player Focus")
        p_name = st.selectbox("Compare Player Radar:", t_df['Player'].tolist())
        p_data = t_df[t_df['Player'] == p_name].iloc[0]
        st.pyplot(plot_radar(p_data, ['Firepower', 'Utility', 'Entry', 'Clutch', 'AWP'], '#ff4b4b'))



