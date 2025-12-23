import streamlit as st
import pandas as pd
import math  # 用於無條件進位計算

# 設定網頁標題與圖示
st.set_page_config(page_title="工程計算工具箱", page_icon="🏗️", layout="wide")

st.title("🏗️ 工程計算工具箱")
st.markdown("---")

# 建立兩個分頁
tab1, tab2 = st.tabs(["🧱 連續壁規劃", "💧 沉沙池計算"])

# ==========================================
# 分頁 1: 連續壁規劃 (含工期)
# ==========================================
with tab1:
    st.header("連續壁工程量與工期試算")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("1️⃣ 尺寸參數")
        dw_total_length = st.number_input("連續壁總長度 (L) [m]", min_value=0.0, value=120.0, step=1.0)
        
        # --- 修改處：單位改為 cm，步進值改為 10 ---
        dw_width_cm = st.number_input("連續壁厚度 (W) [cm]", min_value=50.0, value=80.0, step=10.0, help="常見規格：60, 70, 80, 100, 120 cm")
        
        dw_depth = st.number_input("施作深度 (D) [m]", min_value=0.0, value=30.0, step=1.0)
        loss_rate = st.slider("混凝土損耗率 (%)", min_value=0, max_value=30, value=10)

        st.markdown("---")
        st.subheader("2️⃣ 排程參數")
        unit_std_len = st.number_input("標準單元長度 [m]", min_value=2.0, max_value=8.0, value=6.0, step=0.5)
        days_per_unit = st.number_input("單單元循環天數 (天/單元)", min_value=0.5, value=3.0, step=0.5)
        machine_sets = st.number_input("施作機具組數 (組)", min_value=1, value=1, help="現場同時作業的 MHL/抓斗組數")

    with col2:
        if dw_total_length > 0 and dw_width_cm > 0:
            # --- 計算邏輯 ---
            
            # 1. 單位換算：將 cm 轉為 m 進行體積計算
            dw_width_m = dw_width_cm / 100.0
            
            # 2. 體積計算
            dw_vol = dw_total_length * dw_width_m * dw_depth
            dw_conc = dw_vol * (1 + loss_rate / 100)
            dw_area = dw_total_length * dw_depth

            # 3. 單元數與工期
            total_units = math.ceil(dw_total_length / unit_std_len)
            total_days = (total_units * days_per_unit) / machine_sets

            # --- 顯示結果 ---
            st.subheader("📊 規劃結果概覽")
            
            # 顯示實際計算用的厚度 (m)
            st.caption(f"計算基礎：厚度 {dw_width_cm} cm (即 {dw_width_m} m)")

            # 第一排：工程數量
            st.markdown("##### 📦 工程數量")
            m1, m2, m3 = st.columns(3)
            m1.metric("總挖掘土方", f"{dw_vol:,.0f} m³")
            m2.metric("預估混凝土", f"{dw_conc:,.0f} m³", f"{loss_rate}% 損耗")
            m3.metric("總壁體面積", f"{dw_area:,.0f} m²")

            st.markdown("---")
            
            # 第二排：排程與單元
            st.markdown("##### 🗓️ 進度排程")
            t1, t2, t3 = st.columns(3)
            t1.metric("預計總單元數", f"{total_units} 單元", help=f"以 {unit_std_len}m 為標準")
            t2.metric("預估施作工期", f"{total_days:.1f} 天", help=f"配置 {machine_sets} 組機具")
            t3.metric("平均每日進度", f"{total_units/total_days:.2f} 單元/天")

        else:
            st.warning("👈 請輸入完整參數")

# ==========================================
# 分頁 2: 沉沙池計算 (維持不變)
# ==========================================
with tab2:
    st.header("沉沙池容量檢核")
    col_input, col_result = st.columns([1, 2])

    with col_input:
        st.subheader("📝 尺寸設定")
        pool_length = st.number_input("沉沙池長度 (L) [m]", min_value=0.0, value=5.0, step=0.5)
        pool_width = st.number_input("沉沙池寬度 (W) [m]", min_value=0.0, value=3.0, step=0.5)
        pool_depth = st.number_input("有效水深 (H) [m]", min_value=0.0, value=2.0, step=0.1)
        pool_count = st.number_input("設置數量 (座)", min_value=1, value=1, step=1)
        target_vol = st.number_input("法規/計畫要求容量 [m³] (選填)", min_value=0.0, value=0.0)

    with col_result:
        if pool_length > 0 and pool_width > 0:
            single_vol = pool_length * pool_width * pool_depth
            total_vol = single_vol * pool_count
            
            st.subheader("📊 容量計算結果")
            r_col1, r_col2 = st.columns(2)
            r_col1.metric("單座有效容量", f"{single_vol:,.2f} m³")
            r_col2.metric("總設置容量", f"{total_vol:,.2f} m³", f"{pool_count} 座總計")

            if target_vol > 0:
                st.markdown("#### ✅ 檢核判定")
                if total_vol >= target_vol:
                    st.success(f"**合格！** ({total_vol} m³ >= {target_vol} m³)")
                else:
                    st.error(f"**不合格！** 尚缺 {target_vol - total_vol:.2f} m³")

st.markdown("---")
st.caption("Designed for Civil Engineering Plans | Built with Streamlit")