import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# ==========================================
# 1. 页面配置与主题设置
# ==========================================
st.set_page_config(page_title="CS2 Pro Analytics Pipeline", layout="wide", page_icon="🎮")
sns.set_theme(style="darkgrid", context="talk")

# 核心辅助函数：雷达图
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
# 2. 数据处理流水线 (合并与精简)
# ==========================================
@st.cache_data
def get_final_data():
    # 原始数据
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
    # 自动清洗
    for col in ['Rating', 'Impact']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        df[col] = df[col].fillna(df.groupby('Team')[col].transform('mean')).round(2)
    # 战斗指数计算
    df['Combat_Index'] = (df['Firepower']*0.4 + df['Entry']*0.3 + df['Clutch']*0.3).round(1)
    # 角色定义
    def set_role(r):
        if r['AWP'] > 75: return 'Sniper'
        if r['Utility'] > 75: return 'Support/IGL'
        return 'Rifler'
    df['Role'] = df.apply(set_role, axis=1)
    return df

df_full = get_final_data()

# ==========================================
# 3. 侧边栏 (保持不变)
# ==========================================
st.sidebar.image("https://cdn.akamai.steamstatic.com/apps/csgo/images/csgo_react/global/logo_cs_sm_global.svg", width=150)
st.sidebar.header("⚙️ Global Filters")
min_rating = st.sidebar.slider("Minimum Rating", 0.8, 1.4, 0.9, 0.01)
selected_roles = st.sidebar.multiselect("Filter by Role", options=df_full['Role'].unique(), default=df_full['Role'].unique())

# 应用全局过滤
df_filtered = df_full[(df_full['Rating'] >= min_rating) & (df_full['Role'].isin(selected_roles))]

# ==========================================
# 4. 页面导航逻辑
# ==========================================
if 'page' not in st.session_state: st.session_state.page = 'home'

if st.session_state.page == 'home':
    st.title("🏆 CS2 Pro Analytics: Global Dashboard")
    
    # 精简后的三个核心 Tab
    tabs = st.tabs(["🚀 Pipeline Summary", "📊 Global Analysis", "🛡️ Team Entry"])

    # --- TAB 1: 流程简述 ---
    with tabs[0]:
        st.subheader("Automated Data Pipeline")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.success("✅ Data Cleaned: Missing values handled via Team-Mean Imputation.")
            st.info("✅ Feature Engineering: 'Combat_Index' and 'Role' calculated.")
        with col_p2:
            st.dataframe(df_filtered[['Player', 'Team', 'Rating', 'Combat_Index', 'Role']].head(5), use_container_width=True)

    # --- TAB 2: 可视化大盘 (增加比重 & 互动对比) ---
    with tabs[1]:
        st.header("Comprehensive Player Breakdown")
        
        # 第一行：宏观分布（保留好的部分）
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Team Performance Spread")
            fig_box, ax_box = plt.subplots(figsize=(8, 6))
            sns.boxplot(data=df_filtered, x='Team', y='Rating', palette='pastel', ax=ax_box)
            sns.swarmplot(data=df_filtered, x='Team', y='Rating', color=".25", size=6, ax=ax_box)
            st.pyplot(fig_box)
        with c2:
            st.subheader("Metric Correlation")
            fig_heat, ax_heat = plt.subplots(figsize=(8, 6))
            corr = df_filtered[['Rating', 'Impact', 'Firepower', 'Utility', 'Entry', 'Clutch']].corr()
            sns.heatmap(corr, annot=True, cmap="YlGnBu", fmt=".2f", ax=ax_heat)
            st.pyplot(fig_heat)

        st.divider()

        # 第二行：互动式 25 选手大横评 (重点改进)
        st.subheader("⚔️ Multi-Player Battleground")
        st.markdown("Select specific players to compare their tactical attributes side-by-side.")
        
        # 互动选择
        all_players = df_filtered['Player'].tolist()
        comp_players = st.multiselect("Choose Players to Compare:", options=all_players, default=all_players[:5])
        
        if comp_players:
            comp_df = df_filtered[df_filtered['Player'].isin(comp_players)]
            
            # 多角度对比图：属性堆叠图
            fig_comp, ax_comp = plt.subplots(figsize=(12, 6))
            melted = comp_df.melt(id_vars='Player', value_vars=['Firepower', 'Utility', 'Entry', 'Clutch'])
            sns.barplot(data=melted, x='Player', y='value', hue='variable', palette='magma', ax=ax_comp)
            ax_comp.set_title("Tactical Attribute Comparison", fontsize=16)
            plt.xticks(rotation=45)
            st.pyplot(fig_comp)
            
            # 性能排序图：Combat Index
            st.markdown("#### Global Combat Index Ranking")
            fig_rank, ax_rank = plt.subplots(figsize=(12, 4))
            sorted_df = comp_df.sort_values('Combat_Index', ascending=False)
            sns.barplot(data=sorted_df, x='Combat_Index', y='Player', palette='viridis', ax=ax_rank)
            st.pyplot(fig_rank)
        else:
            st.warning("Please select at least one player to view the comparison.")

    # --- TAB 3: 战队入口 (底色改为白色) ---
    with tabs[2]:
        st.header("🛡️ Team Deep Dive")
        st.markdown("Select a team card to see the full roster analysis.")
        
        teams = df_full['Team'].unique()
        team_cols = st.columns(len(teams))
        
        for i, t in enumerate(teams):
            with team_cols[i]:
                # 关键改进：底色改为白色，文字改为黑色，增加阴影感
                st.markdown(f"""
                    <div style='text-align:center; padding:15px; border-radius:10px; 
                    background-color:white; color:#1e1e2e; border: 1px solid #e6e6e6;
                    box-shadow: 2px 2px 5px rgba(0,0,0,0.05); margin-bottom:10px;'>
                        <h3 style='margin:0;'>{t}</h3>
                        <p style='font-size:0.8em; color:gray;'>Roster size: 5</p >
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Analyze {t}", key=f"btn_{t}", use_container_width=True):
                    st.session_state.selected_team = t
                    st.session_state.page = 'detail'
                    st.rerun()

# ==========================================
# 5. 战队详情页 (保持原有逻辑)
# ==========================================
elif st.session_state.page == 'detail':
    target = st.session_state.selected_team
    st.button("⬅ Back to Global Dashboard", on_click=lambda: setattr(st.session_state, 'page', 'home'))
    
    st.title(f"🚀 {target} Franchise Report")
    t_data = df_full[df_full['Team'] == target]
    
    # 详情页指标
    m1, m2, m3 = st.columns(3)
    m1.metric("Avg Rating", f"{t_data['Rating'].mean():.2f}")
    m2.metric("Star Player", t_data.loc[t_data['Rating'].idxmax(), 'Player'])
    m3.metric("Team Combat Power", f"{t_data['Combat_Index'].sum():.1f}")
    
    st.divider()
    
    # 详情页数据分析
    c_l, c_r = st.columns([1.5, 1])
    with c_l:
        st.markdown("#### Attribute Composition")
        fig_t, ax_t = plt.subplots(figsize=(8, 5))
        t_melt = t_data.melt(id_vars='Player', value_vars=['Firepower', 'Utility', 'Entry', 'Clutch'])
        sns.barplot(data=t_t_melt, x='value', y='Player', hue='variable', palette='rocket', ax=ax_t)
        st.pyplot(fig_t)
        st.dataframe(t_data.drop(columns=['Team', 'Role']), use_container_width=True)
        
    with c_r:
        st.markdown("#### Player Spotlight")
        sel_p = st.selectbox("Select Player:", t_data['Player'].tolist())
        p_stats = t_data[t_data['Player'] == sel_p].iloc[0]
        st.pyplot(plot_radar_chart(p_stats, ['Firepower', 'Utility', 'Entry', 'Clutch', 'AWP'], f"{sel_p} Radar", "#3498db"))





