import streamlit as st
import pandas as pd
import math

# 設定網頁標題與圖示
st.set_page_config(page_title="工程計算工具箱", page_icon="🏗️", layout="wide")

st.title("🏗️ 工程計算工具箱")
st.markdown("---")

# 建立兩個分頁
tab1, tab2 = st.tabs(["🧱 連續壁規劃 (含特殊工法)", "💧 沉沙池計算"])

# ==========================================
# 分頁 1: 連續壁規劃
# ==========================================
with tab1:
    st.header("連續壁工程量與工法規劃")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("1️⃣ 尺寸參數")
        
        # --- 輸入模式切換 ---
        input_mode = st.radio(
            "長度輸入模式",
            ["由中心線自動推算 (搭配轉角)", "自行輸入內/外/中心長度"],
            horizontal=True
        )
        
        # 共同參數：厚度
        dw_width_cm = st.number_input("連續壁厚度 (W) [cm]", min_value=50.0, value=80.0, step=10.0)
        dw_width_m = dw_width_cm / 100.0

        # --- 根據模式顯示不同輸入框 ---
        if input_mode == "由中心線自動推算 (搭配轉角)":
            dw_center_len = st.number_input("中心線總長 (L) [m]", min_value=0.0, value=120.0, step=1.0)
            corners = st.number_input("90度轉角數量 (個)", min_value=0, value=4, step=1)
            len_outer = dw_center_len + (corners * dw_width_m)
            len_inner = dw_center_len - (corners * dw_width_m)
        else:
            dw_center_len = st.number_input("中心線長度 [m]", min_value=0.0, value=120.0)
            len_outer = st.number_input("外皮線長度 [m]", min_value=0.0, value=123.2)
            len_inner = st.number_input("內皮線長度 [m]", min_value=0.0, value=116.8)
            corners = 0

        dw_depth = st.number_input("連續壁施作深度 (D) [m]", min_value=0.0, value=30.0, step=1.0)
        loss_rate = st.slider("混凝土損耗率 (%)", min_value=0, max_value=30, value=10)

        st.markdown("---")
        st.subheader("2️⃣ 施工工法選擇")
        
        # --- 新增：工法選擇選單 ---
        construction_method = st.selectbox(
            "導溝/障礙排除工法",
            ["一般導溝工法 (Standard)", "深導溝工法 (Deep Guide Wall)", "全套管障礙排除 (All-Casing)"],
            help="針對都更案舊基礎或特殊地質選擇對應工法"
        )

        # --- 根據工法跳出動態欄位 ---
        special_items = {}  # 用來儲存特殊項目的字典
        
        if construction_method == "一般導溝工法 (Standard)":
            st.caption("✅ 適用於素地或無淺層障礙物之基地。")
            guide_depth = 1.5  # 預設一般導溝深

        elif construction_method == "深導溝工法 (Deep Guide Wall)":
            st.warning("⚠️ 適用於淺層土質軟弱或有淺層舊構造物。")
            guide_depth = st.number_input("深導溝施作深度 [m]", min_value=1.5, value=3.0, step=0.5)
            # 儲存特殊數據
            special_items['深導溝開挖'] = guide_depth

        elif construction_method == "全套管障礙排除 (All-Casing)":
            st.error("🛑 適用於排除深層舊基礎、鋼筋混凝土障礙或舊基樁。")
            st.markdown("#### 全套管與地改參數")
            casing_dia = st.selectbox("使用套管尺寸", ["1000mm", "1200mm", "1500mm"], index=1)
            obstacle_depth = st.number_input("預估障礙物/切削深度 [m]", min_value=0.0, value=10.0, step=1.0)
            
            # 地改與微型樁
            soil_imp_area = st.number_input("地盤改良面積 (m²)", min_value=0.0, value=0.0, help="例如導溝兩側改良")
            micro_pile_count = st.number_input("微型樁支數 (支)", min_value=0, value=0, help="用於保護鄰房或導溝穩定")
            micro_pile_len = st.number_input("微型樁單支長度 (m)", min_value=0.0, value=0.0)
            
            guide_depth = 1.5 # 全套管通常配合一般導溝或臨時導溝，這裡暫設 1.5
            
            # 儲存特殊數據
            special_items['套管尺寸'] = casing_dia
            special_items['障礙切削深'] = obstacle_depth
            special_items['地改面積'] = soil_imp_area
            special_items['微型樁'] = (micro_pile_count, micro_pile_len)

        st.markdown("---")
        st.subheader("3️⃣ 排程參數")
        # 根據工法調整預設天數 (全套管比較慢)
        default_days = 5.0 if construction_method == "全套管障礙排除 (All-Casing)" else 3.0
        
        unit_std_len = st.number_input("標準單元長度 [m]", min_value=2.0, max_value=10.0, value=4.5, step=0.5)
        days_per_unit = st.number_input("單單元循環天數 (天/單元)", min_value=0.5, value=default_days, step=0.5, help="全套管工法通常需較長作業時間")
        machine_sets = st.number_input("施作機具組數 (組)", min_value=1, value=1)

    with col2:
        if dw_center_len > 0 and dw_width_cm > 0:
            # --- 主計算邏輯 ---
            dw_vol = dw_center_len * dw_width_m * dw_depth
            dw_conc = dw_vol * (1 + loss_rate / 100)
            dw_area = dw_center_len * dw_depth
            total_units = math.ceil(dw_center_len / unit_std_len)
            total_days = (total_units * days_per_unit) / machine_sets

            # --- 顯示結果 ---
            st.subheader("📏 幾何尺寸確認")
            if input_mode == "自行輸入內/外/中心長度":
                st.caption("依據手動輸入數值：")
            else:
                st.caption(f"依據中心線 {dw_center_len}m 推算：")

            g1, g2, g3 = st.columns(3)
            g1.metric("外皮線長度", f"{len_outer:.2f} m")
            g2.metric("中心線長度", f"{dw_center_len:.2f} m")
            g3.metric("內皮線長度", f"{len_inner:.2f} m")

            st.markdown("---")

            # --- 特殊工法 數量計算區塊 ---
            st.subheader(f"🏗️ 工法分析：{construction_method}")
            
            # 這裡計算假設工程數量
            if construction_method == "一般導溝工法 (Standard)":
                st.info("採用標準導溝施作，無特殊假設工程項目。")
                
            elif construction_method == "深導溝工法 (Deep Guide Wall)":
                # 粗估深導溝開挖體積：長度 x (壁厚+預留寬度1m) x 深度
                dg_width = dw_width_m + 1.0 
                dg_vol = dw_center_len * dg_width * guide_depth
                
                c1, c2 = st.columns(2)
                c1.metric("深導溝預估開挖量", f"{dg_vol:,.0f} m³", help=f"計算式: L x (W+1m) x {guide_depth}m")
                c2.metric("深導溝深度", f"{guide_depth} m")
                st.caption("註：深導溝通常需回填低強度混凝土或構築加深RC導溝。")

            elif construction_method == "全套管障礙排除 (All-Casing)":
                # 計算預估障礙排除體積
                obs_vol = dw_center_len * dw_width_m * obstacle_depth
                mp_total_len = special_items['微型樁'][0] * special_items['微型樁'][1]
                
                c1, c2, c3 = st.columns(3)
                c1.metric("障礙切削預估體積", f"{obs_vol:,.0f} m³", help=f"深度 {obstacle_depth}m 範圍內")
                c2.metric("地質改良面積", f"{special_items['地改面積']:,.0f} m²")
                c3.metric("微型樁總長度", f"{mp_total_len:,.0f} m", f"{special_items['微型樁'][0]} 支")
                
                st.warning(f"注意：需確認 {special_items['套管尺寸']} 套管與抓斗/切削機具之匹配性。")

            st.markdown("---")

            # --- 主要工程數量 ---
            st.subheader("📦 連續壁本體工程數量")
            m1, m2, m3 = st.columns(3)
            m1.metric("總挖掘土方", f"{dw_vol:,.0f} m³")
            m2.metric("預估混凝土", f"{dw_conc:,.0f} m³", f"{loss_rate}% 損耗")
            m3.metric("總壁體面積", f"{dw_area:,.0f} m²")

            st.markdown("---")
            
            # --- 進度排程 ---
            st.subheader("🗓️ 進度排程預估")
            t1, t2, t3 = st.columns(3)
            t1.metric("預計總單元數", f"{total_units} 單元")
            t2.metric("預估施作工期", f"{total_days:.1f} 天", help=f"含 {construction_method} 作業時間")
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