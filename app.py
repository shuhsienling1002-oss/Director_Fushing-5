import streamlit as st
import datetime
import sqlite3
import pandas as pd

# ==========================================
# 🛡️ 系統底層：本地資料庫與自動遷移
# ==========================================
def init_db():
    conn = sqlite3.connect('fuxing_guardian_v4.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS health_logs (
            date TEXT PRIMARY KEY, actual_age INTEGER, body_age INTEGER,
            visceral_fat REAL, muscle_mass REAL, bmi REAL, resting_hr INTEGER,
            blood_pressure TEXT, readiness_score INTEGER, social_mode_active BOOLEAN,
            micro_workouts_done INTEGER, water_intake_cc INTEGER
        )
    ''')
    # 自動補齊酒精防禦欄位
    c.execute("PRAGMA table_info(health_logs)")
    columns = [column[1] for column in c.fetchall()]
    if 'no_alcohol' not in columns:
        c.execute("ALTER TABLE health_logs ADD COLUMN no_alcohol BOOLEAN DEFAULT 1")
    conn.commit()
    conn.close()

def calculate_readiness(vf, hr, bp_sys, body_age, actual_age, social_mode, micro_workouts, water_intake, water_goal, no_alcohol):
    base_score = 100
    if vf > 10: base_score -= (vf - 10) * 1.5 
    if hr > 65: base_score -= (hr - 65) * 2
    if bp_sys > 130: base_score -= (bp_sys - 130) * 1 
    if (body_age - actual_age) > 0: base_score -= (body_age - actual_age) * 1
    if social_mode:
        base_score -= 20
        if no_alcohol: base_score += 20 # 應酬但沒喝酒，抵銷懲罰
    if no_alcohol: base_score += 10 # 肝臟修復加分
    base_score += (micro_workouts * 3)
    if water_intake >= water_goal: base_score += 5 
    return max(0, min(100, int(base_score)))

def load_history():
    conn = sqlite3.connect('fuxing_guardian_v4.db')
    try:
        df = pd.read_sql_query("SELECT * FROM health_logs ORDER BY date DESC", conn)
    except: df = pd.DataFrame()
    conn.close()
    return df

# ==========================================
# 🧠 狀態機初始化
# ==========================================
st.set_page_config(page_title="復興守護者", page_icon="🛡️", layout="wide")
init_db()

today_date = datetime.date.today()
today_str = today_date.strftime("%Y-%m-%d")
is_weekend = today_date.weekday() >= 5 

if 'social_mode' not in st.session_state: st.session_state.social_mode = False
if 'no_alcohol' not in st.session_state: st.session_state.no_alcohol = True 
if 'metrics' not in st.session_state: 
    st.session_state.metrics = {'actual_age': 54, 'body_age': 69, 'vf': 25.0, 'muscle': 26.7, 'bmi': 33.8, 'hr': 63, 'bp_sys': 119, 'bp_dia': 79}
if 'micro_workouts' not in st.session_state: st.session_state.micro_workouts = 0 
if 'water_intake' not in st.session_state: st.session_state.water_intake = 0 

water_goal = 3000 if st.session_state.social_mode else 2000
st.session_state.readiness_score = calculate_readiness(st.session_state.metrics['vf'], st.session_state.metrics['hr'], st.session_state.metrics['bp_sys'], st.session_state.metrics['body_age'], st.session_state.metrics['actual_age'], st.session_state.social_mode, st.session_state.micro_workouts, st.session_state.water_intake, water_goal, st.session_state.no_alcohol)

# ==========================================
# 🎨 介面層
# ==========================================
st.title("🛡️ 復興守護者")
st.markdown(f"**蘇區長，早安。今天是 {today_str} {'(週末重置日)' if is_weekend else '(市政高壓期)'}**")

with st.expander("📥 輸入今日最新數值", expanded=False):
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        new_actual_age = st.number_input("實際年齡", value=st.session_state.metrics['actual_age'], step=1)
        new_vf = st.number_input("內臟脂肪", value=st.session_state.metrics['vf'], step=0.5)
    with col_b:
        new_body_age = st.number_input("身體年齡", value=st.session_state.metrics['body_age'], step=1)
        new_muscle = st.number_input("骨骼肌率 (%)", value=st.session_state.metrics['muscle'], step=0.1)
    with col_c:
        new_bp_sys = st.number_input("高壓", value=st.session_state.metrics['bp_sys'], step=1)
        new_hr = st.number_input("安靜心率", value=st.session_state.metrics['hr'], step=1)
    if st.button("🔄 更新今日數值"):
        st.session_state.metrics.update({'actual_age': new_actual_age, 'body_age': new_body_age, 'vf': new_vf, 'muscle': new_muscle, 'bp_sys': new_bp_sys, 'hr': new_hr})
        st.rerun()

st.divider()

col1, col2, col3 = st.columns(3)
with col1: st.metric("代謝綜合評分", f"{st.session_state.readiness_score}%", delta_color="normal" if st.session_state.readiness_score >= 70 else "inverse")
with col2: st.metric("心血管狀態", f"{st.session_state.metrics['bp_sys']} mmHg")
with col3: st.metric("身體年齡", f"{st.session_state.metrics['body_age']} 歲", f"老化 +{st.session_state.metrics['body_age']-st.session_state.metrics['actual_age']} 歲", delta_color="inverse")

st.divider()

# --- 🏃 零碎時間運動 (還原蘇區長最愛的詳細選單) ---
if is_weekend:
    st.success("🌲 【週末重置模式】14小時微斷食 + 大自然漫步")
else:
    st.subheader("⏱️ 零碎時間運動")
    available_time = st.radio("區長，現在有多少空檔？", ["3 分鐘", "10 分鐘", "15 分鐘"], horizontal=True)
    if "3 分鐘" in available_time: st.info("🪑 **辦公椅深蹲 (15下)** + 🧱 **靠牆伏地挺身 (15下)**")
    elif "10 分鐘" in available_time: st.info("🚶‍♂️ **原地高抬腿 (3分鐘)** + 🪜 **階梯微喘 (5分鐘)** + 🫁 **深呼吸 (2分鐘)**")
    else: st.info("⛰️ **微喘步道健行**：連續步行 15 分鐘。")
    if st.button("✅ 完成一次微訓練"):
        st.session_state.micro_workouts += 1
        st.balloons()
        st.rerun()

st.subheader("🚫 酒精防禦")
is_sober = st.checkbox("🍺 今日沒喝酒 (啟動代謝修復模式)", value=st.session_state.no_alcohol)
if is_sober != st.session_state.no_alcohol:
    st.session_state.no_alcohol = is_sober
    st.rerun()

st.divider()

# --- 💧 喝水與應酬 ---
st.subheader(f"💧 喝水 (目標: {water_goal} cc)")
st.progress(min(st.session_state.water_intake / water_goal, 1.0))
if st.button("➕ 喝一杯水 (250cc)"): 
    st.session_state.water_intake += 250
    st.rerun()

st.divider()

if st.session_state.social_mode:
    st.error("🚨 應酬模式：內臟脂肪警戒中")
    if st.button("✅ 應酬結束"): 
        st.session_state.social_mode = False
        st.rerun()
else:
    if st.button("🍷 臨時追加應酬"): 
        st.session_state.social_mode = True
        st.rerun()

if st.button("💾 儲存今日完整日誌"):
    conn = sqlite3.connect('fuxing_guardian_v4.db')
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO health_logs VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)', (today_str, st.session_state.metrics['actual_age'], st.session_state.metrics['body_age'], st.session_state.metrics['vf'], st.session_state.metrics['muscle'], 33.8, st.session_state.metrics['hr'], f"{st.session_state.metrics['bp_sys']}/79", st.session_state.readiness_score, st.session_state.social_mode, st.session_state.micro_workouts, st.session_state.water_intake, st.session_state.no_alcohol))
    conn.commit()
    conn.close()
    st.success("✅ 數據已成功存檔！")

# ==========================================
# 📖 歷史管理 (欄位名稱還原為中文)
# ==========================================
st.divider()
st.subheader("📖 歷史健康日誌管理")
tab1, tab2 = st.tabs(["📊 查看歷史紀錄", "✏️ 修改 / 刪除紀錄"])

with tab1:
    history_df = load_history()
    if not history_df.empty:
        # 還原蘇區長指定的中文欄位
        display_df = history_df.copy()
        display_df.columns = ['日期', '實際年齡', '身體年齡', '內臟脂肪', '骨骼肌(%)', 'BMI', '安靜心率', '血壓(mmHg)', '綜合評分', '有應酬?', '微訓練(次)', '喝水量(cc)', '沒喝酒?']
        st.dataframe(display_df, use_container_width=True, hide_index=True)

with tab2:
    if not history_df.empty:
        dates_list = history_df['date'].tolist()
        selected_date = st.selectbox("請選擇日期：", dates_list)
        if st.button("🗑️ 刪除這筆紀錄"):
            conn = sqlite3.connect('fuxing_guardian_v4.db'); c = conn.cursor()
            c.execute("DELETE FROM health_logs WHERE date=?", (selected_date,))
            conn.commit(); conn.close()
            st.rerun()
