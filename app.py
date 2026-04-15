import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import io

# ==========================================
# 页面全局配置
# ==========================================
st.set_page_config(page_title="CS2 Pro Player Analytics Pro Max", layout="wide", page_icon="🎮")
sns.set_theme(style="darkgrid", context="talk")

# ==========================================
# 雷达图函数
# ==========================================
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
# 数据加载
# ==========================================
@st.cache_data
def load_raw_data():
    raw_data = {
        'Team': ['Vitality']*5 + ['NAVI']*5 + ['Astralis']*5 + ['The MongolZ']*5 + ['Aurora']*5,
        'Player': [
            'ZywOo','flameZ','Spinx','apEX','mezii','iM','w0nderful','Aleksib','jL','b1t',
            'Staehr','jabbi','phzy','ryu','HooXi','910','mzinho','Techno','bLitz','cobrazera',
            'deko','r3salt','Norwi','Lack1','KENSI'
        ],
        'Rating': [1.30,1.15,1.14,1.02,1.03,1.09,1.07,0.91,1.10,1.09,1.11,1.06,'--','--',0.84,1.05,1.04,0.97,0.95,'--',1.15,1.13,1.05,0.98,1.10],
        'Impact': [1.42,1.18,1.15,0.98,1.00,1.12,1.05,0.85,1.15,1.08,1.10,1.04,'--','--',0.78,1.08,1.01,0.95,0.99,'--',1.20,1.16,1.08,0.95,1.12],
        'KAST_%': [76,73,74,69,71,72,74,70,71,72,73,72,'--','--',68,71,70,69,72,'--',75,73,71,69,72],
        'Firepower': [92,80,75,35,51,72,53,4,86,60,85,68,74,44,6,72,50,24,28,65,86,85,62,25,78],
        'Utility': [52,54,51,89,72,35,54,89,52,51,79,48,62,32,81,60,45,46,94,35,35,56,45,91,45],
        'Entry': [56,70,42,85,24,66,28,86,90,33,62,69,22,79,52,6,52,51,42,41,36,82,52,42,66],
        'Clutch': [82,35,75,31,60,32,78,51,36,79,38,50,77,48,40,66,54,38,34,42,82,35,54,34,45],
        'AWP': [94,1,0,1,0,0,92,0,0,2,0,0,92,0,1,91,0,0,2,7,92,0,0,2,1]
    }
    return pd.DataFrame(raw_data)

df_raw = load_raw_data()

# ==========================================
# 数据清洗
# ==========================================
df_clean = df_raw.copy()
for col in ['Rating','Impact','KAST_%']:
    df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
    df_clean[col] = df_clean[col].fillna(df_clean.groupby('Team')[col].transform('mean')).round(2)

df_analyzed = df_clean.copy()
df_analyzed['Combat_Index'] = (
    df_analyzed['Firepower']*0.35 +
    df_analyzed['Entry']*0.25 +
    df_analyzed['Clutch']*0.2 +
    df_analyzed['Utility']*0.2
).round(1)

def get_role(row):
    if row['AWP'] > 75: return 'Sniper'
    if row['Utility'] > 75 and row['Firepower'] < 50: return 'Tactical IGL'
    if row['Entry'] > 75: return 'Entry Fragger'
    return 'Rifler / Support'

df_analyzed['Role'] = df_analyzed.apply(get_role, axis=1)

# ==========================================
# 侧边栏（保持不变）
# ==========================================
st.sidebar.image("https://cdn.akamai.steamstatic.com/apps/csgo/images/csgo_react/global/logo_cs_sm_global.svg", width=150)
st.sidebar.header("⚙️ Global Filters")
st.sidebar.markdown("Use these controls to filter the entire dataset below.")

min_rating = st.sidebar.slider("Minimum Rating", min_value=0.8, max_value=1.4, value=0.9, step=0.01)
selected_roles = st.sidebar.multiselect("Filter by Role", options=df_analyzed['Role'].unique(), default=df_analyzed['Role'].unique())

df_filtered = df_analyzed[(df_analyzed['Rating'] >= min_rating) & (df_analyzed['Role'].isin(selected_roles))]

# ==========================================
# 状态管理
# ==========================================
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# ==========================================
# 首页开始
# ==========================================
if st.session_state.page == 'home':
    st.title("🏆 CS2 Pro Player Analytical Pipeline")
    st.markdown("A highly interactive dashboard for exploring team rosters and player statistics.")

    tabs = st.tabs(["🔍 数据概览 & 清洗", "📊 分布分析", "📈 25人多维对比", "⚔️ Viz: Player Battles"])
        with tabs[0]:
     st.subheader("Raw Data Inspection")
     st.dataframe(df_raw, use_container_width=True, height=260)
     st.error(f"⚠️ Anomaly Detected: Found {df_raw['Rating'].astype(str).str.contains('--').sum()} missing values marked as '--'.")

        st.divider()

        st.subheader("Cleaning Pipeline")
        col1, col2 = st.columns(2)

        with col1:
            st.success("Imputation Rule: missing values replaced by team averages.")
            st.dataframe(df_filtered[['Player','Team','Rating','Impact','KAST_%','Role']].head(10))

        with col2:
            st.info("Feature Engineering: Combat_Index built from multiple stats.")
            st.dataframe(df_filtered.head(10))

    with tabs[1]:
        col1, col2 = st.columns(2)

        with col1:
            fig, ax = plt.subplots()
            sns.boxplot(data=df_filtered, x='Team', y='Rating', ax=ax)
            st.pyplot(fig)

        with col2:
            fig, ax = plt.subplots()
            sns.heatmap(df_filtered.select_dtypes(include=np.number).corr(), annot=True, ax=ax)
            st.pyplot(fig)

    with tabs[2]:
        fig, ax = plt.subplots(figsize=(12,10))
        sns.barplot(data=df_filtered.sort_values('Combat_Index'), x='Combat_Index', y='Player', hue='Team', ax=ax)
        st.pyplot(fig)

        fig, ax = plt.subplots(figsize=(12,10))
        sns.heatmap(df_filtered.set_index('Player')[['Rating','Impact','Firepower','Utility','Entry','Clutch']], cmap="coolwarm", ax=ax)
        st.pyplot(fig)

    with tabs[3]:
        st.dataframe(df_filtered)

    st.subheader("🛡️ Team Deep Dive")
    teams = df_analyzed['Team'].unique()
    team_cols = st.columns(len(teams))

    for i, t in enumerate(teams):
        with team_cols[i]:
            st.markdown(
                f"<div style='text-align:center; padding:10px; border-radius:5px; background-color:#ffffff; color:#111111;'>{t}</div>",
                unsafe_allow_html=True
            )
            if st.button(f"Analyze", key=f"btn_{t}", use_container_width=True):
                st.session_state.selected_team = t
                st.session_state.page = 'detail'
                st.rerun()

elif st.session_state.page == 'detail':
    target = st.session_state.selected_team

    if st.button("⬅ Back"):
        st.session_state.page = 'home'
        st.rerun()

    st.title(target)

    team_data = df_analyzed[df_analyzed['Team'] == target]

    st.dataframe(team_data)

    selected_player = st.selectbox("Select Player", team_data['Player'])
    player_stats = team_data[team_data['Player'] == selected_player].iloc[0]

    fig = plot_radar_chart(player_stats, ['Firepower','Utility','Entry','Clutch','AWP'], selected_player, '#00ffcc')
    st.pyplot(fig)

