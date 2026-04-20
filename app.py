import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import List, Dict, Any, Tuple
import warnings

# 忽略潜在的 Seaborn 警告
warnings.filterwarnings("ignore", category=FutureWarning)

# ==========================================
# 1. 页面配置与全局主题设置
# ==========================================
st.set_page_config(
    page_title="CS2 Pro Analytics Pro Max", 
    layout="wide", 
    page_icon="🎮"
)

# 设置全局绘图主题
sns.set_theme(style="darkgrid", context="talk")

# 全局常量配置
COLOR_PALETTE_PRIMARY = "Set3"
COLOR_PALETTE_HEATMAP = "mako"
COLOR_PALETTE_BAR = "viridis"
COLOR_PALETTE_RADAR = "#e74c3c"
COLOR_RADAR_ALPHA = 0.3

# ==========================================
# 2. 数据处理流水线模块
# ==========================================

def get_raw_dataset() -> Dict[str, List[Any]]:
    """
    Returns the raw dataset for the CS2 analytics pipeline.
    Formatted vertically for maximum readability and PEP 8 compliance.
    """
    return {
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
        'Impact': [
            1.42, 1.18, 1.15, 0.98, 1.00,
            1.12, 1.05, 0.85, 1.15, 1.08,
            1.10, 1.04, 1.02, 0.98, 0.78,
            1.08, 1.01, 0.95, 0.99, 1.00,
            1.20, 1.16, 1.08, 0.95, 1.12
        ],
        'Firepower': [
            92, 80, 75, 35, 51,
            72, 53, 4, 86, 60,
            85, 68, 74, 44, 6,
            72, 50, 24, 28, 65,
            86, 85, 62, 25, 78
        ],
        'Utility': [
            52, 54, 51, 89, 72,
            35, 54, 89, 52, 51,
            79, 48, 62, 32, 81,
            60, 45, 46, 94, 35,
            35, 56, 45, 91, 45
        ],
        'Entry': [
            56, 70, 42, 85, 24,
            66, 28, 86, 90, 33,
            62, 69, 22, 79, 52,
            6, 52, 51, 42, 41,
            36, 82, 52, 42, 66
        ],
        'Clutch': [
            82, 35, 75, 31, 60,
            32, 78, 51, 36, 79,
            38, 50, 77, 48, 40,
            66, 54, 38, 34, 42,
            82, 35, 54, 34, 45
        ],
        'AWP': [
            94, 1, 0, 1, 0,
            0, 92, 0, 0, 2,
            0, 0, 92, 0, 1,
            91, 0, 0, 2, 7,
            92, 0, 0, 2, 1
        ]
    }

def set_detailed_role(row: pd.Series) -> str:
    """
    Evaluates player statistics to determine their specialized in-game role.
    """
    if row['AWP'] > 75: 
        return 'Sniper'
    if row['Entry'] > 70: 
        return 'Entry Fragger'
    if row['Utility'] > 80: 
        return 'IGL / Support'
    if row['Clutch'] > 70: 
        return 'Clutch Minister'
    return 'Rifler'

def impute_missing_metrics(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """
    Performs Team-Based Mean Imputation for missing values.
    """
    df_cleaned = df.copy()
    for col in columns:
        df_cleaned[col] = pd.to_numeric(df_cleaned[col], errors='coerce')
        team_mean = df_cleaned.groupby('Team')[col].transform('mean')
        df_cleaned[col] = df_cleaned[col].fillna(team_mean).round(2)
    return df_cleaned

def calculate_combat_index(df: pd.DataFrame) -> pd.Series:
    """
    Calculates the weighted Combat Index based on technical parameters.
    """
    firepower_weight = 0.4
    entry_weight = 0.3
    clutch_weight = 0.3
    
    index_values = (
        df['Firepower'] * firepower_weight + 
        df['Entry'] * entry_weight + 
        df['Clutch'] * clutch_weight
    )
    return index_values.round(1)

@st.cache_data
def get_final_data() -> pd.DataFrame:
    """
    Main execution pipeline for data ingestion, cleaning, and feature engineering.
    """
    raw_data = get_raw_dataset()
    df = pd.DataFrame(raw_data)
    
    # 1. Impute Missing Values
    df = impute_missing_metrics(df, ['Rating', 'Impact'])
    
    # 2. Feature Engineering: Combat Index
    df['Combat_Index'] = calculate_combat_index(df)
    
    # 3. Role Classification
    df['Role'] = df.apply(set_detailed_role, axis=1)
    
    return df

# 初始化全局数据
df_full = get_final_data()
global_avg_rating = df_full['Rating'].mean()
global_avg_firepower = df_full['Firepower'].mean()

# ==========================================
# 3. 数据可视化渲染模块 (解耦的画图函数)
# ==========================================

def plot_radar_chart(player_series: pd.Series, categories: List[str], title: str, color: str) -> plt.Figure:
    """Generates a professional radar chart for player attribute visualization."""
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    values = player_series[categories].values.flatten().tolist()
    
    values += values[:1]
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    ax.fill(angles, values, color=color, alpha=COLOR_RADAR_ALPHA)
    ax.plot(angles, values, color=color, linewidth=2)
    
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=10, weight='bold')
    ax.set_title(title, size=14, color=color, y=1.1)
    
    return fig

def plot_global_rating_spread(df: pd.DataFrame) -> plt.Figure:
    """Generates boxplot and swarmplot for team rating distribution."""
    fig, ax = plt.subplots(figsize=(12, 5))
    sns.boxplot(data=df, x='Team', y='Rating', palette=COLOR_PALETTE_PRIMARY, ax=ax)
    sns.swarmplot(data=df, x='Team', y='Rating', color=".25", size=5, ax=ax)
    return fig

def plot_global_correlation(df: pd.DataFrame) -> plt.Figure:
    """Generates a correlation heatmap for key performance metrics."""
    fig, ax = plt.subplots(figsize=(12, 5))
    metrics_df = df[['Rating', 'Impact', 'Firepower', 'Utility', 'Entry', 'Clutch']]
    sns.heatmap(metrics_df.corr(), annot=True, cmap=COLOR_PALETTE_HEATMAP, ax=ax, fmt=".2f")
    return fig

def plot_tactical_attribute_stack(comp_df: pd.DataFrame) -> plt.Figure:
    """Generates a horizontal bar chart comparing tactical attributes."""
    melted = comp_df.melt(id_vars='Player', value_vars=['Firepower', 'Utility', 'Entry', 'Clutch'])
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(data=melted, x='value', y='Player', hue='variable', palette=COLOR_PALETTE_BAR, ax=ax)
    return fig

def plot_rating_vs_impact_trend(comp_df: pd.DataFrame) -> plt.Figure:
    """Generates a line plot comparing Rating and Impact trends."""
    fig, ax = plt.subplots(figsize=(12, 5))
    sns.lineplot(data=comp_df, x='Player', y='Rating', marker='o', label='Rating', color='royalblue', ax=ax)
    sns.lineplot(data=comp_df, x='Player', y='Impact', marker='s', label='Impact', color='crimson', ax=ax)
    plt.xticks(rotation=45)
    return fig

def plot_carry_vs_team_quadrant(comp_df: pd.DataFrame) -> plt.Figure:
    """Generates a scatter plot quadrant for Utility vs Firepower."""
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.scatterplot(data=comp_df, x='Firepower', y='Utility', hue='Player', s=400, palette='deep', ax=ax)
    ax.axhline(50, color='gray', linestyle='--')
    ax.axvline(50, color='gray', linestyle='--')
    return fig

def plot_combat_index_heatmap(comp_df: pd.DataFrame) -> plt.Figure:
    """Generates a simplified heatmap for individual combat stats."""
    heat_data = comp_df.set_index('Player')[['Firepower', 'Utility', 'Entry', 'Clutch', 'Rating']]
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.heatmap(heat_data, annot=True, cmap="RdYlGn", ax=ax, cbar=False)
    return fig

def render_team_card_ui(team_name: str) -> str:
    """Returns raw HTML for rendering the Team Entry CSS cards."""
    return f"""
        <div style='text-align:center; padding:15px; border-radius:10px; 
        background-color:white; color:#1e1e2e; border: 1px solid #ddd;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05); margin-bottom:10px;'>
            <h4 style='margin:0;'>{team_name}</h4>
            <p style='font-size:0.8em; color:#666;'>Pro Roster</p >
        </div>
    """

# ==========================================
# 4. 侧边栏与全局过滤器
# ==========================================
st.sidebar.header("⚙️ Global Filters")

min_rating = st.sidebar.slider("Minimum Rating", 0.8, 1.4, 0.9, 0.01)
available_roles = df_full['Role'].unique().tolist()
selected_roles = st.sidebar.multiselect(
    "Filter by Detailed Role", 
    options=available_roles, 
    default=available_roles
)

# 应用过滤逻辑
df_filtered = df_full[
    (df_full['Rating'] >= min_rating) & 
    (df_full['Role'].isin(selected_roles))
]

# ==========================================
# 5. 页面导航状态管理逻辑
# ==========================================
if 'page' not in st.session_state: 
    st.session_state.page = 'home'

# ==========================================
# 6. 主页视图 (Home View)
# ==========================================
if st.session_state.page == 'home':
    st.title("🏆 CS2 Pro Analytics: Global Dashboard")
    
    tabs = st.tabs(["🚀 Pipeline Summary", "⚔️ Multi-Player Battleground", "🛡️ Team Entry"])

    # --- TAB 1: Pipeline Summary ---
    with tabs[0]:
        st.subheader("Automated Data Pipeline")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.success("✅ Cleaned: Imputed missing Rating using Team Average.")
            st.info(f"✅ Categorized: Defined {len(available_roles)} unique player roles.")
        with col_p2:
            st.dataframe(
                df_filtered[['Player', 'Team', 'Rating', 'Role']].head(10), 
                use_container_width=True
            )

    # --- TAB 2: Multi-Player Battleground ---
    with tabs[1]:
        st.header("📊 Global Performance Overview")
        
        st.subheader("Global Team Rating Spread")
        st.pyplot(plot_global_rating_spread(df_filtered))

        st.subheader("Global Metric Correlation")
        st.pyplot(plot_global_correlation(df_filtered))

        st.divider()

        st.header("⚔️ Multi-Player Battleground")
        all_players = df_filtered['Player'].tolist()
        comp_players = st.multiselect(
            "Select Players to Compare:", 
            options=all_players, 
            default=all_players[:5]
        )
        
        if len(comp_players) > 0:
            comp_df = df_filtered[df_filtered['Player'].isin(comp_players)].sort_values('Rating', ascending=False)
            
            st.subheader("1. Tactical Attribute Stack")
            st.pyplot(plot_tactical_attribute_stack(comp_df))
            
            st.divider()

            st.subheader("2. Rating vs Impact Trend")
            st.pyplot(plot_rating_vs_impact_trend(comp_df))
            
            st.divider()

            st.subheader("3. Carry vs Team-Player (Quadrant)")
            st.pyplot(plot_carry_vs_team_quadrant(comp_df))
            
            st.divider()

            st.subheader("4. Combat Index Heatmap")
            st.pyplot(plot_combat_index_heatmap(comp_df))
        else:
            st.warning("Please select players to activate the battleground.")

    # --- TAB 3: Team Entry ---
    with tabs[2]:
        st.header("🛡️ Team Deep Dive")
        teams = df_full['Team'].unique()
        team_cols = st.columns(len(teams))
        
        for i, t in enumerate(teams):
            with team_cols[i]:
                st.markdown(render_team_card_ui(t), unsafe_allow_html=True)
                
                if st.button(f"Enter {t}", key=f"btn_{t}", use_container_width=True):
                    st.session_state.selected_team = t
                    st.session_state.page = 'detail'
                    st.rerun()

# ==========================================
# 7. 战队详情页视图 (Detail View)
# ==========================================
elif st.session_state.page == 'detail':
    target = st.session_state.selected_team
    
    st.button(
        "⬅ Back to Global", 
        on_click=lambda: setattr(st.session_state, 'page', 'home')
    )
    
    st.title(f"🚀 {target} Roster Intelligence")
    t_data = df_full[df_full['Team'] == target]
    
    # 指标对比计算
    team_avg_rating = t_data['Rating'].mean()
    team_avg_firepower = t_data['Firepower'].mean()
    rating_delta = team_avg_rating - global_avg_rating
    firepower_delta = team_avg_firepower - global_avg_firepower

    # 渲染顶部指标栏
    col_metrics = st.columns(3)
    
    col_metrics[0].metric(
        label="Avg Rating", 
        value=f"{team_avg_rating:.2f}", 
        delta=f"{rating_delta:+.2f} vs Global Avg"
    )
    
    top_player = t_data.loc[t_data['Rating'].idxmax(), 'Player']
    col_metrics[1].metric("Top Gun", top_player)
    
    col_metrics[2].metric(
        label="Avg Firepower", 
        value=f"{team_avg_firepower:.1f}", 
        delta=f"{firepower_delta:+.1f} vs Global Avg"
    )

    st.divider()

    # 战队数据与雷达图双栏布局
    c_l, c_r = st.columns([1.5, 1])
    
    with c_l:
        st.markdown("#### Performance Matrix")
        t_melt = t_data.melt(
            id_vars='Player', 
            value_vars=['Firepower', 'Utility', 'Entry', 'Clutch']
        )
        fig_t, ax_t = plt.subplots(figsize=(8, 5))
        sns.barplot(data=t_melt, x='value', y='Player', hue='variable', palette='magma', ax=ax_t)
        st.pyplot(fig_t)
        
        st.dataframe(t_data.drop(columns=['Team', 'Role']), use_container_width=True)
        
    with c_r:
        st.markdown("#### Radar Spotlight")
        sel_p = st.selectbox("Select Player:", t_data['Player'].tolist())
        p_stats = t_data[t_data['Player'] == sel_p].iloc[0]
        
        radar_fig = plot_radar_chart(
            player_series=p_stats, 
            categories=['Firepower', 'Utility', 'Entry', 'Clutch', 'AWP'], 
            title=f"{sel_p} Stats", 
            color=COLOR_PALETTE_RADAR
        )
        st.pyplot(radar_fig)










