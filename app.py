import streamlit as st
import pandas as pd
import os

# 設置網頁標題與圖示
st.set_page_config(page_title="LLM YouTube Tracker", page_icon="🤖", layout="wide")

st.title("🤖 LLM Video Insight Tracker")
st.markdown("""
This dashboard tracks the latest videos from top LLM researchers and uses **DeepSeek-V3** to summarize key insights.
""")

# --- 1. 讀取數據 ---
db_file = "llm_tracker_database.csv"

if os.path.exists(db_file):
    df = pd.read_csv(db_file, encoding="utf-8-sig")

    # --- 2. 側邊欄篩選器 ---
    st.sidebar.header("Filters")
    authors = ["All"] + sorted(df["Author"].unique().tolist())
    selected_author = st.sidebar.selectbox("Select Channel", authors)

    search_query = st.sidebar.text_input("Search in Title/Summary", "")

    # --- 3. 數據過濾邏輯 ---
    filtered_df = df.copy()
    if selected_author != "All":
        filtered_df = filtered_df[filtered_df["Author"] == selected_author]

    if search_query:
        # 在標題或總結中搜索關鍵字
        filtered_df = filtered_df[
            filtered_df["Title"].str.contains(search_query, case=False, na=False) |
            filtered_df["Summary"].str.contains(search_query, case=False, na=False)
            ]

    # --- 4. 顯示結果 ---
    st.subheader(f"Found {len(filtered_df)} Videos")

    for index, row in filtered_df.iterrows():
        with st.expander(f"📺 {row['Author']} - {row['Title']}"):
            col1, col2 = st.columns([1, 2])

            with col1:
                st.write(f"**URL:** [Watch on YouTube]({row['URL']})")
                # 這裡如果想更專業，可以加入 YouTube 預覽圖
                video_id = row['URL'].split("v=")[-1]
                st.image(f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg")

            with col2:
                st.write("**AI Summary & Key Takeaways:**")
                st.info(row['Summary'])

else:
    st.error("Data file not found. Please run main_app.py first to generate the database!")