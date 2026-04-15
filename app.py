import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# ==========================================
# 1. 页面配置与主题设置
# ==========================================
st.set_page_config(page_title="CS2 Pro Analytics Pro Max", layout="wide", page_icon="🎮")
sns.set_theme(style="darkgrid", context="talk")

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
# 2. 数据处理流水线
# ==========================================
@st.cache_data
def get_final_data():
    raw_data = {
        'Team': ['Vitality']*5 + ['NAVI']*5 + ['Astralis']*5 + ['The MongolZ']*5 + ['Aurora']*5,
        'Player': ['ZywOo', 'flameZ', 'Spinx', 'apEX', 'mezii', 'iM', 'w0nderful', 'Aleksib', 'jL', 'b1t', 'Staehr', 'jabbi', 'phzy', 'ryu', 'HooXi', '910', 'mzinho', 'Techno', 'bLitz', 'cobrazera', 'deko', 'r3salt', 'Norwi', 'Lack1', 'KENSI'],
        'Rating': [1.30, 1.15, 1.14, 1.02, 1.03, 1.09, 1.07, 0.91, 1.10, 1.09, 1.11, 1.06, '--', '--', 0.84, 1.05, 1.04, 0.97, 0.95, '--', 1.15, 1.13, 1.05, 0.98, 1.10],
        'Impact': [1.42, 1.18, 1.15, 0.98, 1.00, 1.12, 1.05, 0.85, 1.15, 1.08, 1.10, 1.04, 1.02, 0.98, 0.78, 1.08, 1.01, 0.95, 0.99, 1.00, 1.20, 1.16, 1.08, 0.95, 1.12],
        'Firepower': [92, 80, 75, 35, 51, 72, 53, 4, 86, 60, 85, 68, 74, 44, 6, 72, 50, 24, 28, 65, 86, 85, 62, 25, 78],
        'Utility': [52, 54, 51, 89, 72, 35, 54, 89, 52, 51, 79, 48, 62, 32, 81, 60, 45, 46, 94, 35, 35, 56, 45, 91, 45],
        'Entry': [56, 70, 42, 85, 24, 66, 28, 86, 90, 33, 62, 69, 22, 79, 52, 6, 52, 51, 42, 41, 36, 82, 52, 42, 66],
        'Clutch': [82, 35, 75, 31, 60, 32, 78, 51, 36, 79, 38, 50, 77, 48, 40, 66, 54, 38, 34, 42, 82, 35, 54, 34, 45],
        'AWP': [94, 1, 0, 1, 0, 0, 92, 0, 0, 2, 0, 0, 92, 0, 1, 91, 0, 0, 2, 7, 92, 0, 0, 2, 1]
    }
    df = pd.DataFrame(raw_data)
    for col in ['Rating', 'Impact']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        df[col] = df[col].fillna(df.groupby('Team')[col].transform('mean')).round(2)
    df['Combat_Index'] = (df['Firepower']*0.4 + df['Entry']*0.3 + df['Clutch']*0.3).round(1)
    
    def set_detailed_role(r):
        if r['AWP'] > 75: return 'Sniper'
        if r['Entry'] > 70: return 'Entry Fragger'
        if r['Utility'] > 80: return 'IGL / Support'
        if r['Clutch'] > 70: return 'Clutch Minister'
        return 'Rifler'
    df['Role'] = df.apply(set_detailed_role, axis=1)
    return df

df_full = get_final_data()

# ==========================================
# 3. 侧边栏
# ==========================================
st.sidebar.image("https://cdn.akamai.steamstatic.com/apps/csgo/images/csgo_react/global/logo_cs_sm_global.svg", width=150)
st.sidebar.header("⚙️ Global Filters")
min_rating = st.sidebar.slider("Minimum Rating", 0.8, 1.4, 0.9, 0.01)
available_roles = df_full['Role'].unique().tolist()
selected_roles = st.sidebar.multiselect("Filter by Detailed Role", options=available_roles, default=available_roles)

df_filtered = df_full[(df_full['Rating'] >= min_rating) & (df_full['Role'].isin(selected_roles))]

# ==========================================
# 4. 页面导航逻辑
# ==========================================
if 'page' not in st.session_state: st.session_state.page = 'home'

if st.session_state.page == 'home':
    st.title("🏆 CS2 Pro Analytics: Global Dashboard")
    
    tabs = st.tabs(["🚀 Pipeline Summary", "⚔️ Multi-Player Battleground", "🛡️ Team Entry"])

    # --- TAB 1: 流程简述 ---
    with tabs[0]:
        st.subheader("Automated Data Pipeline")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.success("✅ Cleaned: Imputed missing Rating using Team Average.")
            st.info(f"✅ Categorized: Defined {len(available_roles)} unique player roles.")
        with col_p2:
            st.dataframe(df_filtered[['Player', 'Team', 'Rating', 'Role']].head(10), use_container_width=True)

    # --- TAB 2: 深度选手横评 (重新布局) ---
    with tabs[1]:
        st.header("📊 Global Performance Overview")
        
        # 1. 宏观分布 - 移至顶层，一行一图
        st.subheader("Global Team Rating Spread")
        fig_box, ax_box = plt.subplots(figsize=(12, 5))
        sns.boxplot(data=df_filtered, x='Team', y='Rating', palette='Set3', ax=ax_box)
        sns.swarmplot(data=df_filtered, x='Team', y='Rating', color=".25", size=5, ax=ax_box)
        st.pyplot(fig_box)

        st.subheader("Global Metric Correlation")
        fig_heat, ax_heat = plt.subplots(figsize=(12, 5))
        sns.heatmap(df_filtered[['Rating', 'Impact', 'Firepower', 'Utility', 'Entry', 'Clutch']].corr(), 
                    annot=True, cmap="mako", ax=ax_heat, fmt=".2f")
        st.pyplot(fig_heat)

        st.divider()

        # 2. 互动对比 - 每一图占一行
        st.header("⚔️ Multi-Player Battleground")
        all_players = df_filtered['Player'].tolist()
        comp_players = st.multiselect("Select Players to Compare:", options=all_players, default=all_players[:5])
        
        if len(comp_players) > 0:
            comp_df = df_filtered[df_filtered['Player'].isin(comp_players)].sort_values('Rating', ascending=False)
            
            # --- 图表 1: 属性堆叠柱状图 ---
            st.subheader("1. Tactical Attribute Stack")
            melted = comp_df.melt(id_vars='Player', value_vars=['Firepower', 'Utility', 'Entry', 'Clutch'])
            fig_bar, ax_bar = plt.subplots(figsize=(12, 6))
            sns.barplot(data=melted, x='value', y='Player', hue='variable', palette='viridis', ax=ax_bar)
            st.pyplot(fig_bar)
            
            st.divider()

            # --- 图表 2: Rating vs Impact 趋势线 ---
            st.subheader("2. Rating vs Impact Trend")
            fig_line, ax_line = plt.subplots(figsize=(12, 5))
            sns.lineplot(data=comp_df, x='Player', y='Rating', marker='o', label='Rating', color='royalblue', ax=ax_line)
            sns.lineplot(data=comp_df, x='Player', y='Impact', marker='s', label='Impact', color='crimson', ax=ax_line)
            plt.xticks(rotation=45)
            st.pyplot(fig_line)
            
            st.divider()

            # --- 图表 3: 象限分布图 ---
            st.subheader("3. Carry vs Team-Player (Quadrant)")
            fig_scat, ax_scat = plt.subplots(figsize=(12, 6))
            sns.scatterplot(data=comp_df, x='Firepower', y='Utility', hue='Player', s=400, palette='deep', ax=ax_scat)
            ax_scat.axhline(50, color='gray', linestyle='--')
            ax_scat.axvline(50, color='gray', linestyle='--')
            st.pyplot(fig_scat)
            
            st.divider()

            # --- 图表 4: 性能热力矩阵 ---
            st.subheader("4. Combat Index Heatmap")
            heat_data = comp_df.set_index('Player')[['Firepower', 'Utility', 'Entry', 'Clutch', 'Rating']]
            fig_h2, ax_h2 = plt.subplots(figsize=(12, 6))
            sns.heatmap(heat_data, annot=True, cmap="RdYlGn", ax=ax_h2, cbar=False)
            st.pyplot(fig_h2)
        else:
            st.warning("Please select players to activate the battleground.")

    # --- TAB 3: 战队入口 (底色白色) ---
    with tabs[2]:
        st.header("🛡️ Team Deep Dive")
        teams = df_full['Team'].unique()
        team_cols = st.columns(len(teams))
        for i, t in enumerate(teams):
            with team_cols[i]:
                st.markdown(f"""
                    <div style='text-align:center; padding:15px; border-radius:10px; 
                    background-color:white; color:#1e1e2e; border: 1px solid #ddd;
                    box-shadow: 2px 2px 5px rgba(0,0,0,0.05); margin-bottom:10px;'>
                        <h4 style='margin:0;'>{t}</h4>
                        <p style='font-size:0.8em; color:#666;'>Pro Roster</p >
                    </div>
                """, unsafe_allow_html=True)
                if st.button(f"Enter {t}", key=f"btn_{t}", use_container_width=True):
                    st.session_state.selected_team = t
                    st.session_state.page = 'detail'
                    st.rerun()

# ==========================================
# 5. 战队详情页
# ==========================================
elif st.session_state.page == 'detail':
    target = st.session_state.selected_team
    st.button("⬅ Back to Global", on_click=lambda: setattr(st.session_state, 'page', 'home'))
    
    st.title(f"🚀 {target} Roster Intelligence")
    t_data = df_full[df_full['Team'] == target]
    
    col_metrics = st.columns(3)
    col_metrics[0].metric("Avg Rating", f"{t_data['Rating'].mean():.2f}")
    col_metrics[1].metric("Top Gun", t_data.loc[t_data['Rating'].idxmax(), 'Player'])
    col_metrics[2].metric("Team Firepower", int(t_data['Firepower'].sum()))

    c_l, c_r = st.columns([1.5, 1])
    with c_l:
        st.markdown("#### Performance Matrix")
        t_melt = t_data.melt(id_vars='Player', value_vars=['Firepower', 'Utility', 'Entry', 'Clutch'])
        fig_t, ax_t = plt.subplots(figsize=(8, 5))
        sns.barplot(data=t_melt, x='value', y='Player', hue='variable', palette='magma', ax=ax_t)
        st.pyplot(fig_t)
        st.dataframe(t_data.drop(columns=['Team', 'Role']), use_container_width=True)
        
    with c_r:
        st.markdown("#### Radar Spotlight")
        sel_p = st.selectbox("Select Player:", t_data['Player'].tolist())
        p_stats = t_data[t_data['Player'] == sel_p].iloc[0]
        st.pyplot(plot_radar_chart(p_stats, ['Firepower', 'Utility', 'Entry', 'Clutch', 'AWP'], f"{sel_p} Stats", "#e74c3c"))







