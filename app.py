import streamlit as st
import pandas as pd
import math

# 設定網頁標題與圖示
st.set_page_config(page_title="工程計算工具箱", page_icon="🏗️", layout="wide")

st.title("🏗️ 工程計算工具箱")
st.markdown("---")

# 建立兩個分頁
tab1, tab2 = st.tabs(["🧱 連續壁規劃", "💧 假設工程：沉沙與棄土"])

# ==========================================
# 分頁 1: 連續壁規劃 (保持不變)
# ==========================================
with tab1:
    st.header("連續壁工程量與工法規劃")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("1️⃣ 尺寸參數")
        input_mode = st.radio("長度輸入模式",["由中心線自動推算 (搭配轉角)", "自行輸入內/外/中心長度"], horizontal=True)
        dw_width_cm = st.number_input("連續壁厚度 (W) [cm]", min_value=50.0, value=80.0, step=10.0)
        dw_width_m = dw_width_cm / 100.0

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
        st.subheader("2️⃣ 導溝/核心工法")
        construction_method = st.selectbox("選擇工法",["一般導溝工法 (Standard)", "深導溝工法 (Deep Guide Wall)", "全套管障礙排除 (All-Casing)"])

        special_vars = {} 
        if construction_method == "一般導溝工法 (Standard)":
            guide_depth = 1.5
            gw_speed_default = 20.0
        elif construction_method == "深導溝工法 (Deep Guide Wall)":
            guide_depth = st.number_input("深導溝施作深度 [m]", min_value=1.5, value=3.0, step=0.5)
            gw_speed_default = 10.0
            special_vars['guide_depth'] = guide_depth
        elif construction_method == "全套管障礙排除 (All-Casing)":
            casing_dia = st.selectbox("使用套管尺寸", ["1000mm", "1200mm", "1500mm"], index=1)
            obstacle_depth = st.number_input("障礙物/切削深度 [m]", min_value=0.0, value=10.0, step=1.0)
            guide_depth = 1.5 
            gw_speed_default = 20.0
            special_vars['casing_dia'] = casing_dia
            special_vars['obstacle_depth'] = obstacle_depth

        st.markdown("---")
        st.subheader("3️⃣ 輔助/保護工程")
        soil_imp_area = st.number_input("地盤改良面積 (m²)", min_value=0.0, value=0.0)
        c1_aux, c2_aux = st.columns(2)
        with c1_aux: micro_pile_count = st.number_input("微型樁支數", min_value=0, value=0)
        with c2_aux: micro_pile_len = st.number_input("微型樁長度 [m]", min_value=0.0, value=0.0)

        st.markdown("---")
        st.subheader("4️⃣ 排程參數")
        gw_speed = st.number_input("導溝施作速度 (m/天)", min_value=1.0, value=gw_speed_default, step=1.0)
        default_days = 5.0 if construction_method == "全套管障礙排除 (All-Casing)" else 3.0
        unit_std_len = st.number_input("標準單元長度 [m]", min_value=2.0, max_value=10.0, value=4.5, step=0.5)
        days_per_unit = st.number_input("單單元循環天數 (天/單元)", min_value=0.5, value=default_days, step=0.5)
        machine_sets = st.number_input("施作機具組數 (組)", min_value=1, value=1)

    with col2:
        if dw_center_len > 0 and dw_width_cm > 0:
            dw_vol = dw_center_len * dw_width_m * dw_depth
            dw_conc = dw_vol * (1 + loss_rate / 100)
            dw_area = dw_center_len * dw_depth
            gw_days = math.ceil(dw_center_len / gw_speed)
            total_units = math.ceil(dw_center_len / unit_std_len)
            dw_days = (total_units * days_per_unit) / machine_sets
            total_project_days = gw_days + dw_days

            st.subheader("📏 幾何尺寸確認")
            g1, g2, g3 = st.columns(3)
            g1.metric("外皮線長度", f"{len_outer:.2f} m")
            g2.metric("中心線長度", f"{dw_center_len:.2f} m")
            g3.metric("內皮線長度", f"{len_inner:.2f} m")

            st.markdown("---")
            st.subheader(f"🏗️ 工法與假設工程：{construction_method}")
            if construction_method == "深導溝工法 (Deep Guide Wall)":
                dg_vol = dw_center_len * (dw_width_m + 1.0) * special_vars['guide_depth']
                st.metric("深導溝預估開挖量", f"{dg_vol:,.0f} m³")
            elif construction_method == "全套管障礙排除 (All-Casing)":
                obs_vol = dw_center_len * dw_width_m * special_vars['obstacle_depth']
                st.metric("障礙切削預估體積", f"{obs_vol:,.0f} m³")
            
            if soil_imp_area > 0 or micro_pile_count > 0:
                st.markdown("#### 🛡️ 輔助與保護工程")
                a1, a2 = st.columns(2)
                if soil_imp_area > 0: a1.metric("地盤改良面積", f"{soil_imp_area:,.0f} m²")
                if micro_pile_count > 0: a2.metric("微型樁總長", f"{micro_pile_count * micro_pile_len:,.0f} m")

            st.markdown("---")
            st.subheader("📦 連續壁本體工程數量")
            m1, m2, m3 = st.columns(3)
            m1.metric("總挖掘土方", f"{dw_vol:,.0f} m³")
            m2.metric("預估混凝土", f"{dw_conc:,.0f} m³", f"{loss_rate}% 損耗")
            m3.metric("總壁體面積", f"{dw_area:,.0f} m²")

            st.markdown("---")
            st.subheader("🗓️ 施工進度排程表")
            c_s1, c_s2, c_s3 = st.columns(3)
            c_s1.metric("1. 導溝工期", f"{gw_days} 天")
            c_s2.metric("2. 壁體工期", f"{dw_days:.1f} 天")
            c_s3.metric("🏆 預估總工期", f"{total_project_days:.1f} 天")
        else:
            st.warning("👈 請輸入完整參數")

# ==========================================
# 分頁 2: 假設工程 (沉沙與棄土)
# ==========================================
with tab2:
    st.header("💧 假設工程：沉沙池與棄土坑規劃")
    
    # 全局變數初始化，避免未定義錯誤
    pool_total_exc_vol = 0
    pit_total_exc_vol = 0
    pool_count = 0
    pit_count = 0

    # 1. 基地參數
    st.subheader("1️⃣ 基地參數輸入")
    col_base1, col_base2, col_base3 = st.columns(3)
    with col_base1:
        site_area = st.number_input("基地/開挖平面面積 (m²)", min_value=0.0, value=1000.0, step=100.0)
        area_ping = site_area * 0.3025
        st.caption(f"換算坪數：約 **{area_ping:,.1f} 坪**")
    with col_base2:
        avg_depth = st.number_input("平均開挖深度 (m)", min_value=0.0, value=10.0, step=0.5)
    with col_base3:
        total_mass_vol = site_area * avg_depth
        st.metric("總計畫挖掘實方體積", f"{total_mass_vol:,.0f} m³")

    st.markdown("---")
    col_left, col_right = st.columns([1, 1])

    # ----------------------------------------------------
    # 區塊 A: 沉沙池
    # ----------------------------------------------------
    with col_left:
        with st.expander("A. 沉沙池規格計算", expanded=True):
            st.caption("依據「法規係數」反推深度")
            req_factor = st.number_input("法規係數 (m³/ha)", min_value=0.0, value=600.0, step=50.0)
            pool_count = st.number_input("預計設置座數 (座)", min_value=1, value=2, step=1)
            
            c_pl, c_pw = st.columns(2)
            pool_l = c_pl.number_input("沉沙池長 (m)", min_value=1.0, value=6.0, step=0.5)
            pool_w = c_pw.number_input("沉沙池寬 (m)", min_value=1.0, value=5.0, step=0.5)
            
            total_req_sed_vol = (site_area / 10000.0) * req_factor
            total_pool_area = pool_count * (pool_l * pool_w)
            required_depth = total_req_sed_vol / total_pool_area if total_pool_area > 0 else 0
            
            # 記錄沉沙池挖掘總量 (為了後面計算時間)
            pool_total_exc_vol = total_pool_area * required_depth
            
            st.markdown("---")
            st.subheader("📊 所需深度")
            c_p1, c_p2 = st.columns(2)
            c_p1.metric("法規總量", f"{total_req_sed_vol:,.2f} m³")
            depth_label = f"{required_depth:.2f} m"
            if required_depth > 3.0:
                c_p2.metric("單池深度", depth_label, "過深", delta_color="inverse")
            else:
                c_p2.metric("單池深度", depth_label, "適中")

    # ----------------------------------------------------
    # 區塊 B: 棄土坑
    # ----------------------------------------------------
    with col_right:
        with st.expander("B. 棄土坑規格計算", expanded=True):
            st.caption("依據「土方運能平衡」反推深度")
            daily_solid_vol = st.number_input("每日計畫出土實方 (m³/天)", min_value=1.0, value=200.0, step=50.0)
            swell_factor = st.number_input("土方鬆弛係數", min_value=1.0, value=1.25, step=0.05)
            
            truck_vol = st.number_input("運土車斗容量 (m³/車)", value=10.0)
            max_trips = st.number_input("每日最大車次 (車/天)", value=15)
            
            st.markdown("---")
            pit_count = st.number_input("預計設置座數 (座)", min_value=1, value=1, step=1, key="pit_count")
            c_sl, c_sw = st.columns(2)
            pit_l = c_sl.number_input("單坑長度 (m)", min_value=1.0, value=6.0, step=0.5, key="pit_l")
            pit_w = c_sw.number_input("單坑寬度 (m)", min_value=1.0, value=5.0, step=0.5, key="pit_w")
            
            daily_loose_vol = daily_solid_vol * swell_factor
            daily_haul_cap = truck_vol * max_trips
            buffer_needed = daily_loose_vol - daily_haul_cap
            
            total_pit_area = pit_count * (pit_l * pit_w)
            pit_depth_needed = buffer_needed / total_pit_area if (buffer_needed > 0 and total_pit_area > 0) else 0
            
            # 記錄棄土坑挖掘總量 (為了後面計算時間)
            pit_total_exc_vol = total_pit_area * pit_depth_needed
            excavation_days_mass = math.ceil(total_mass_vol / daily_solid_vol) if daily_solid_vol > 0 else 0
            
            st.markdown("---")
            c_r1, c_r2 = st.columns(2)
            c_r1.metric("需暫存鬆方", f"{buffer_needed:,.1f} m³")
            depth_str = f"{pit_depth_needed:.2f} m"
            if pit_depth_needed > 2.5:
                c_r2.metric("單坑深度", depth_str, "過深", delta_color="inverse")
            else:
                c_r2.metric("單坑深度", depth_str, "適中")
            st.caption(f"預估全基地開挖總工期：{excavation_days_mass} 天")

    st.markdown("---")

    # ----------------------------------------------------
    # 新增區塊 C: 假設工程施作時間
    # ----------------------------------------------------
    st.subheader("2️⃣ 假設工程施作工期預估")
    st.info("計算完成沉沙池與棄土坑所需之「挖掘」與「構築」時間。此為正式開挖前之準備工期。")
    
    with st.expander("C. 施作時間參數設定", expanded=True):
        col_time_in, col_time_out = st.columns([1, 2])
        
        with col_time_in:
            st.markdown("##### 效率參數")
            # 針對小坑挖掘的效率 (跟大面積出土不同)
            small_exc_rate = st.number_input(
                "小型挖掘效率 (m³/天)", 
                min_value=10.0, value=50.0, step=10.0, 
                help="針對沉沙池/棄土坑之精修挖掘，通常使用 PC120 或 PC200，效率較低。"
            )
            
            st.markdown("##### 沉沙池構築")
            pool_install_days = st.number_input(
                "單池構築天數 (天/座)", 
                min_value=0.0, value=2.0, step=0.5, 
                help="含放置內襯、配管、簡易擋土或抽水機安裝時間。"
            )
            
        with col_time_out:
            # 計算邏輯
            # 1. 沉沙池時間
            # 挖掘時間 = 總體積 / 效率
            pool_dig_days = pool_total_exc_vol / small_exc_rate if small_exc_rate > 0 else 0
            # 構築時間 = 座數 * 單座天數
            pool_setup_days = pool_count * pool_install_days
            total_pool_days = math.ceil(pool_dig_days + pool_setup_days)
            
            # 2. 棄土坑時間
            # 僅計算挖掘時間 (棄土坑通常無需複雜構築)
            pit_dig_days = pit_total_exc_vol / small_exc_rate if small_exc_rate > 0 else 0
            total_pit_days = math.ceil(pit_dig_days)
            
            # 總準備工期
            # 假設兩者可以平行施作(取大值) 或 順序施作(相加)，這裡預設採順序計算比較保守
            total_prep_days = total_pool_days + total_pit_days
            
            st.markdown("##### ⏳ 工期計算結果")
            t1, t2, t3 = st.columns(3)
            
            t1.metric(
                "沉沙池施作工期", 
                f"{total_pool_days} 天", 
                f"挖 {pool_dig_days:.1f} 天 + 構 {pool_setup_days:.1f} 天"
            )
            
            t2.metric(
                "棄土坑挖掘工期", 
                f"{total_pit_days} 天", 
                f"挖掘體積 {pit_total_exc_vol:.1f} m³"
            )
            
            t3.metric(
                "假設工程總準備期", 
                f"{total_prep_days} 天", 
                "沉沙池 + 棄土坑",
                delta_color="off"
            )
            
            st.caption(f"註：計算基準為 {pool_count} 座沉沙池與 {pit_count} 座棄土坑。")

st.markdown("---")
st.caption("Designed for Civil Engineering Plans | Built with Streamlit")