import streamlit as st
import datetime
import sqlite3
import pandas as pd

# ==========================================
# 🛡️ 系統底層：本地資料庫與自動計算引擎 (Ops-AI-CRF)
# ==========================================
def init_db():
    conn = sqlite3.connect('fuxing_guardian_v3.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS health_logs (
            date TEXT PRIMARY KEY,
            visceral_fat REAL,
            muscle_mass REAL,
            bmi REAL,
            resting_hr INTEGER,
            blood_pressure TEXT,
            readiness_score INTEGER,
            social_mode_active BOOLEAN,
            micro_workouts_done INTEGER,
            water_intake_cc INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def calculate_readiness(vf, hr, bp_sys, social_mode, micro_workouts, water_intake, water_goal):
    """計算綜合評分"""
    base_score = 100
    if vf > 10: base_score -= (vf - 10) * 1.5 
    if hr > 65: base_score -= (hr - 65) * 2
    if bp_sys > 130: base_score -= (bp_sys - 130) * 1 
    if social_mode: base_score -= 20
    
    base_score += (micro_workouts * 3)
    if water_intake >= water_goal:
        base_score += 5 
        
    return max(0, min(100, int(base_score)))

def load_history():
    """讀取歷史紀錄"""
    conn = sqlite3.connect('fuxing_guardian_v3.db')
    try:
        df = pd.read_sql_query("SELECT * FROM health_logs ORDER BY date DESC", conn)
    except:
        df = pd.DataFrame()
    conn.close()
    return df

st.set_page_config(page_title="復興守護者", page_icon="🛡️", layout="centered")
init_db()

today_date = datetime.date.today()
today_str = today_date.strftime("%Y-%m-%d")
is_weekend = today_date.weekday() >= 5 

# ==========================================
# 🧠 狀態機初始化 (綁定蘇區長體檢數據)
# ==========================================
if 'social_mode' not in st.session_state: st.session_state.social_mode = False
if 'metrics' not in st.session_state: 
    st.session_state.metrics = {'vf': 25.0, 'muscle': 26.7, 'bmi': 33.8, 'hr': 63, 'bp_sys': 119, 'bp_dia': 79}
if 'micro_workouts' not in st.session_state: st.session_state.micro_workouts = 0 
if 'water_intake' not in st.session_state: st.session_state.water_intake = 0 

water_goal = 3000 if st.session_state.social_mode else 2000

if 'readiness_score' not in st.session_state:
    st.session_state.readiness_score = calculate_readiness(
        st.session_state.metrics['vf'], st.session_state.metrics['hr'], st.session_state.metrics['bp_sys'],
        st.session_state.social_mode, st.session_state.micro_workouts, st.session_state.water_intake, water_goal
    )

# ==========================================
# 🎨 介面層：區長專屬動態儀表板
# ==========================================
st.title("🛡️ 復興守護者")
st.markdown(f"**蘇區長，早安。今天是 {today_str} {'(週末重置日)' if is_weekend else '(市政高壓期)'}**")

# --- 📥 今日數值輸入區 ---
with st.expander("📥 點此輸入今日最新數值 (同步體脂計/血壓計)", expanded=False):
    col_a, col_b = st.columns(2)
    with col_a:
        new_vf = st.number_input("內臟脂肪等級", value=st.session_state.metrics['vf'], step=0.5)
        new_bmi = st.number_input("BMI", value=st.session_state.metrics['bmi'], step=0.1)
        new_bp_sys = st.number_input("收縮壓 (高壓)", value=st.session_state.metrics['bp_sys'], step=1)
    with col_b:
        new_muscle = st.number_input("骨骼肌率 (%)", value=st.session_state.metrics['muscle'], step=0.1)
        new_hr = st.number_input("安靜心率 (bpm)", value=st.session_state.metrics['hr'], step=1)
        new_bp_dia = st.number_input("舒張壓 (低壓)", value=st.session_state.metrics['bp_dia'], step=1)
        
    if st.button("🔄 更新今日數值"):
        st.session_state.metrics.update({'vf': new_vf, 'muscle': new_muscle, 'bmi': new_bmi, 'hr': new_hr, 'bp_sys': new_bp_sys, 'bp_dia': new_bp_dia})
        st.session_state.readiness_score = calculate_readiness(new_vf, new_hr, new_bp_sys, st.session_state.social_mode, st.session_state.micro_workouts, st.session_state.water_intake, water_goal)
        st.rerun()

st.divider()

# --- 🔋 綜合狀態儀表板 ---
st.subheader("🔋 今日身體恢復度")
col1, col2 = st.columns(2)
with col1:
    if st.session_state.readiness_score >= 70:
        st.metric("代謝綜合評分", f"{st.session_state.readiness_score}%", "狀態穩定")
    else:
        st.metric("代謝綜合評分", f"{st.session_state.readiness_score}%", "- 肝臟/代謝負載過重", delta_color="inverse")
with col2:
    st.metric("心血管防線 (血壓)", f"{st.session_state.metrics['bp_sys']}/{st.session_state.metrics['bp_dia']}", "優良狀態")

st.divider()

# --- 擴充模組整合區 ---
if is_weekend:
    st.success("🌲 【週末重置模式啟動】清空一週壓力與胰島素殘留")
    st.markdown("* **14小時微斷食**：今日早餐延後至 10:00，清空胰島素。\n* **大自然重置**：進行 30 分鐘森林漫步，重置迷走神經。")
else:
    st.subheader("⏱️ 零碎時間運動")
    available_time = st.radio("區長，您現在有多少空檔？", ["3 分鐘", "10 分鐘", "15 分鐘"], horizontal=True)
    if "3 分鐘" in available_time: st.write("🪑 **辦公椅深蹲 (15下)** + 🧱 **靠牆伏地挺身 (15下)**")
    elif "10 分鐘" in available_time: st.write("🚶‍♂️ **原地高抬腿 (3分鐘)** + 🪜 **階梯微喘 (5分鐘)** + 🫁 **深呼吸 (2分鐘)**")
    else: st.write("⛰️ **微喘步道健行**：維持「微喘」連續步行 15 分鐘。")
    
    if st.button("✅ 完成一次微訓練 (+3分)"):
        st.session_state.micro_workouts += 1
        st.session_state.readiness_score = calculate_readiness(st.session_state.metrics['vf'], st.session_state.metrics['hr'], st.session_state.metrics['bp_sys'], st.session_state.social_mode, st.session_state.micro_workouts, st.session_state.water_intake, water_goal)
        st.balloons()
        st.rerun()

st.divider()

# --- 💧 動態水杯 ---
st.subheader(f"💧 喝水 (目標: {water_goal} cc)")
progress = min(st.session_state.water_intake / water_goal, 1.0)
st.progress(progress)
st.write(f"目前已飲用：**{st.session_state.water_intake} cc**")

col_w1, col_w2 = st.columns(2)
with col_w1:
    if st.button("➕ 喝一杯水 (250cc)"):
        st.session_state.water_intake += 250
        st.session_state.readiness_score = calculate_readiness(st.session_state.metrics['vf'], st.session_state.metrics['hr'], st.session_state.metrics['bp_sys'], st.session_state.social_mode, st.session_state.micro_workouts, st.session_state.water_intake, water_goal)
        st.rerun()
with col_w2:
    if st.button("➕ 喝一瓶水 (500cc)"):
        st.session_state.water_intake += 500
        st.session_state.readiness_score = calculate_readiness(st.session_state.metrics['vf'], st.session_state.metrics['hr'], st.session_state.metrics['bp_sys'], st.session_state.social_mode, st.session_state.micro_workouts, st.session_state.water_intake, water_goal)
        st.rerun()

st.divider()

# --- 🗓️ 應酬防禦與酒精衝擊警告 (強化警告版) ---
st.subheader("🗓️ 飲食控管與應酬防禦")
with st.expander("🍽️ 點此查看：今日會議便當/桌菜破解法", expanded=False):
    st.info("💡 核心邏輯：控制進食順序，避免血糖飆升囤積脂肪。")
    st.markdown("1. 先吃青菜 ➔ 2. 再吃肉類 ➔ 3. 白飯最後且減半。")

if st.session_state.social_mode:
    st.error("🚨 酒精衝擊警報：內臟脂肪 (目前: 25) 面臨核彈級風險")
    
    st.markdown("### 🍷 酒精生理影響分析")
    alc_type = st.selectbox("選擇今晚飲用的酒類：", ["🥃 烈酒 (威士忌/高粱)", "🍷 葡萄酒", "🍺 啤酒/調酒 (絕對禁忌)"])
    alc_count = st.number_input("預計飲用杯數：", min_value=1, value=1)
    
    # 警告邏輯計算
    burn_pause = alc_count * (1.5 if "烈酒" in alc_type else 1.0)
    
    st.markdown(f"""
    * 🛑 **燃脂停滯**：您的身體將有 **{burn_pause} 小時** 處於「零燃脂」狀態。這期間您吃下的任何澱粉都會**直接轉化為內臟脂肪**。
    * ⚠️ **代謝霸佔**：肝臟將被迫放下所有修復工作，您的**身體年齡 (目前: 69歲)** 在酒精排空前將持續老化。
    * ☢️ **內臟脂肪核爆**：{'如果您喝的是啤酒，糖分與酒精的協同作用會讓脂肪囤積效率提高 200%！' if '啤酒' in alc_type else '請嚴守 1:1 水分法則，強迫肝臟降溫。'}
    """)

    if st.button("✅ 應酬平安結束 (啟動 14H 排毒協議)"):
        st.session_state.social_mode = False
        st.rerun()
else:
    if st.button("🍷 臨時追加應酬 (啟動生理損害控管)"):
        st.session_state.social_mode = True
        st.session_state.readiness_score = calculate_readiness(st.session_state.metrics['vf'], st.session_state.metrics['hr'], st.session_state.metrics['bp_sys'], True, st.session_state.micro_workouts, st.session_state.water_intake, 3000)
        st.rerun()

st.divider()

# --- 💾 存檔與歷史紀錄管理 (一字不漏) ---
if st.button("💾 儲存今日完整日誌"):
    bp_str = f"{st.session_state.metrics['bp_sys']}/{st.session_state.metrics['bp_dia']}"
    conn = sqlite3.connect('fuxing_guardian_v3.db')
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO health_logs 
        (date, visceral_fat, muscle_mass, bmi, resting_hr, blood_pressure, readiness_score, social_mode_active, micro_workouts_done, water_intake_cc) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        today_str, st.session_state.metrics['vf'], st.session_state.metrics['muscle'], 
        st.session_state.metrics['bmi'], st.session_state.metrics['hr'], bp_str,
        st.session_state.readiness_score, st.session_state.social_mode, 
        st.session_state.micro_workouts, st.session_state.water_intake
    ))
    conn.commit()
    conn.close()
    st.success("✅ 區長，今日完整日誌已成功儲存！")

st.divider()
st.subheader("📖 歷史健康管理")
tab_view, tab_manage = st.tabs(["📊 查看趨勢", "✏️ 修改/刪除"])
with tab_view:
    history_df = load_history()
    if not history_df.empty:
        history_df.columns = ['日期', '內臟脂肪', '骨骼肌(%)', 'BMI', '安靜心率', '血壓(mmHg)', '恢復度', '有應酬?', '微訓練', '喝水(cc)']
        st.dataframe(history_df, use_container_width=True, hide_index=True)
with tab_manage:
    if not history_df.empty:
        selected_date = st.selectbox("選擇日期：", history_df['日期'].tolist())
        if st.button("🗑️ 刪除該日紀錄"):
            conn = sqlite3.connect('fuxing_guardian_v3.db')
            c = conn.cursor()
            c.execute("DELETE FROM health_logs WHERE date=?", (selected_date,))
            conn.commit()
            conn.close()
            st.rerun()

