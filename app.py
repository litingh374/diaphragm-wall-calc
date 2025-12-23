import streamlit as st
import pandas as pd

# 設定網頁標題與圖示
st.set_page_config(page_title="連續壁計算工具", page_icon="🏗️")

st.title("🏗️ 連續壁工程計算工具")
st.markdown("---")

# --- 側邊欄：輸入參數 ---
st.sidebar.header("📝 參數設定")

# 使用者輸入
length = st.sidebar.number_input("連續壁長度 (L) [公尺]", min_value=0.0, value=6.0, step=0.5, help="單元長度或是總長度")
width = st.sidebar.number_input("連續壁厚度/寬度 (W) [公尺]", min_value=0.0, value=1.0, step=0.1)
depth = st.sidebar.number_input("施作深度 (D) [公尺]", min_value=0.0, value=30.0, step=1.0)

st.sidebar.markdown("---")
# 進階設定：混凝土超灌比/損耗率
loss_rate = st.sidebar.slider("混凝土超灌/損耗率 (%)", min_value=0, max_value=30, value=10, help="通常連續壁會有劣質混凝土或超灌情形，一般抓 5% - 15%")

# --- 計算邏輯 ---
if length > 0 and width > 0 and depth > 0:
    # 1. 理論體積 (土方量)
    theoretical_volume = length * width * depth
    
    # 2. 預估混凝土需求量 (含損耗)
    concrete_volume = theoretical_volume * (1 + loss_rate / 100)
    
    # 3. 壁體垂直面積 (可用於計算防護面積等)
    wall_area = length * depth

    # --- 主畫面：顯示結果 ---
    st.subheader("📊 計算結果")
    
    # 使用 metric 顯示大字體關鍵數據
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="理論挖掘體積 (土方量)", value=f"{theoretical_volume:,.2f} m³")
        st.caption(f"計算公式: $L \\times W \\times D$")
        
    with col2:
        st.metric(label="預估混凝土需求量", value=f"{concrete_volume:,.2f} m³", delta=f"{loss_rate}% 損耗")
        st.caption(f"包含 {loss_rate}% 的超灌/損耗預估")

    st.markdown("---")
    
    # --- 詳細數據表 ---
    st.subheader("📋 詳細數據清單")
    data = {
        "項目": ["連續壁長度", "連續壁厚度", "施作深度", "單面壁體面積", "理論體積", "預估混凝土量"],
        "數值": [length, width, depth, wall_area, theoretical_volume, concrete_volume],
        "單位": ["m", "m", "m", "m²", "m³", "m³"]
    }
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)

else:
    st.info("👈 請從左側側邊欄輸入長度、寬度與深度以開始計算。")

# --- 頁尾 ---
st.markdown("---")
st.markdown("Designed for Civil Engineering | Built with Streamlit")