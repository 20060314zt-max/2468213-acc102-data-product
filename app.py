import streamlit as st
import pandas as pd

# 1. 标题
st.title("📊 我的数据分析展示工具")

# 2. 侧边栏
st.sidebar.header("控制面板")
st.sidebar.write("欢迎来到我的 ACC102 作业项目！")

# 3. 主页内容
st.header("1. 项目简介")
st.write("这是一个使用 Streamlit 开发的交互式数据产品。")

# 4. 做一个小互动，证明它不是空白的
name = st.text_input("请输入你的名字：")
if name:
    st.success(f"你好 {name}！你的 Streamlit 工具已经运行成功了！")

# 5. 展示一个示例表格
st.header("2. 数据预览示例")
df = pd.DataFrame({
    '年份': [2022, 2023, 2024],
    '数据量': [100, 150, 200]
})
st.table(df)
