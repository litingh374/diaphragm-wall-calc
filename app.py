import streamlit as st
import pandas as pd

# 設定網頁標題與圖示
st.set_page_config(page_title="工程計算工具箱", page_icon="🏗️", layout="wide")

st.title("🏗️ 工程計算工具箱")
st.markdown("---")

# 建立兩個分頁
tab1, tab2 = st.tabs(["🧱 連續壁計算", "💧 沉沙池計算"])

# ==========================================
# 分頁 1: 連續壁計算
# ==========================================
with tab1:
    st.header("連續壁工程量計算")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("📝 參數輸入")
        dw_length = st.number_input("連續壁長度 (L) [m]", min_value=0.0, value=6.0, step=0.5, key="dw_l")
        dw_width = st.number_input("連續壁厚度 (W) [m]", min_value=0.0, value=1.0, step=0.1, key="dw_w")
        dw_depth = st.number_input("施作深度 (D) [m]", min_value=0.0, value=30.0, step=1.0, key="dw_d")
        loss_rate = st.slider("混凝土損耗率 (%)", min_value=0, max_value=30, value=10, key="dw_loss")

    with col2:
        if dw_length > 0 and dw_width > 0 and dw_depth > 0:
            # 計算邏輯
            dw_vol = dw_length * dw_width * dw_depth
            dw_conc = dw_vol * (1 + loss_rate / 100)
            dw_area = dw_length * dw_depth

            st.subheader("📊 計算結果")
            
            # 顯示關鍵指標
            m_col1, m_col2, m_col3 = st.columns(3)
            m_col1.metric("理論挖掘體積", f"{dw_vol:,.2f} m³")
            m_col2.metric("預估混凝土量", f"{dw_conc:,.2f} m³", f"+{loss_rate}% 損耗")
            m_col3.metric("垂直壁體面積", f"{dw_area:,.2f} m²")
            
            st.info("💡 提示：此數據可用於叫料或預估出土車次。")
        else:
            st.warning("請在左側輸入完整尺寸以顯示結果")

# ==========================================
# 分頁 2: 沉沙池計算
# ==========================================
with tab2:
    st.header("沉沙池容量檢核")
    st.markdown("用於計算臨時沉沙池或泥水處理設備的有效容積。")

    col_input, col_result = st.columns([1, 2])

    with col_input:
        st.subheader("📝 尺寸設定")
        # 讓使用者選擇形狀，雖然工地多為矩形，但也保留彈性
        pool_length = st.number_input("沉沙池長度 (L) [m]", min_value=0.0, value=5.0, step=0.5)
        pool_width = st.number_input("沉沙池寬度 (W) [m]", min_value=0.0, value=3.0, step=0.5)
        pool_depth = st.number_input("有效水深 (H) [m]", min_value=0.0, value=2.0, step=0.1, help="請扣除出水高程後的有效深度")
        pool_count = st.number_input("設置數量 (座)", min_value=1, value=1, step=1)
        
        st.markdown("---")
        target_vol = st.number_input("法規/計畫要求容量 [m³] (選填)", min_value=0.0, value=0.0, help="若輸入數值，將自動判斷是否合格")

    with col_result:
        if pool_length > 0 and pool_width > 0 and pool_depth > 0:
            # 計算邏輯
            single_vol = pool_length * pool_width * pool_depth
            total_vol = single_vol * pool_count
            
            st.subheader("📊 容量計算結果")
            
            r_col1, r_col2 = st.columns(2)
            with r_col1:
                st.metric("單座有效容量", f"{single_vol:,.2f} m³")
            with r_col2:
                st.metric("總設置容量", f"{total_vol:,.2f} m³", f"{pool_count} 座總計")

            # 檢核邏輯
            if target_vol > 0:
                st.markdown("#### ✅ 檢核判定")
                if total_vol >= target_vol:
                    st.success(f"**合格！** 設計容量 ({total_vol} m³) 大於 要求容量 ({target_vol} m³)")
                else:
                    st.error(f"**不合格！** 設計容量不足，尚缺 {target_vol - total_vol:.2f} m³")
            
            # 製作簡單的表格
            st.markdown("---")
            st.caption("詳細規格表")
            pool_data = pd.DataFrame({
                "項目": ["長度", "寬度", "有效深度", "數量", "總容量"],
                "數值": [pool_length, pool_width, pool_depth, pool_count, total_vol],
                "單位": ["m", "m", "m", "座", "m³"]
            })
            st.dataframe(pool_data, use_container_width=True)
            
        else:
            st.info("請輸入沉沙池的尺寸資料。")

st.markdown("---")
st.markdown("Designed for Civil Engineering Plans | Built with Streamlit")