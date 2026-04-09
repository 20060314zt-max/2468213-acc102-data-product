import streamlit as st
import pandas as pd
import matplotlib as plt
import numpy as np

# 1. 准备数据
data = {
    '属性': ['火力', '突破', '补枪', '首杀', '残局', '狙击', '道具'],
    'ZywOo': [99, 40, 73, 83, 87, 92, 77],
    'apEX': [33, 80, 25, 53, 30, 0, 97],
    'ropz': [70, 12, 40, 35, 69, 5, 31],
    'mezii': [23, 92, 48, 27, 50, 0, 68],
    'flameZ': [93, 84, 62, 89, 49, 0, 70]
}
df = pd.DataFrame(data)

st.title("🎮 Vitality 战队选手数据看板")

# 2. 交互式选择
players = st.multiselect("请选择想要对比的选手", list(data.keys())[1:], default=['ZywOo', 'flameZ'])

# 3. 绘图逻辑
fig, ax = plt.subplots(figsize=(10, 5))
x = np.arange(len(df['属性']))
width = 0.15

for i, player in enumerate(players):
    ax.bar(x + (i - len(players)/2)*width, df[player], width, label=player)

ax.set_xticks(x)
ax.set_xticklabels(df['属性'])
ax.legend()
st.pyplot(fig) # 注意：这里用 st.pyplot 替代了 plt.show()

