import streamlit as st
import datetime
import sqlite3
import pandas as pd

# ==========================================
# 🛡️ 系統底層：自動遷移與計算引擎
# ==========================================
def init_db():
    conn = sqlite3.connect('fuxing_guardian_v4.db')
    c = conn.cursor()
    # 建立表格
    c.execute('''
        CREATE TABLE IF NOT EXISTS health_logs (
            date TEXT PRIMARY KEY,
            actual_age INTEGER,
            body_age INTEGER,
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
    # 💥 自動遷移補丁：檢查是否存在 no_alcohol 欄位 [cite: 31]
    c.execute("PRAGMA table_info(health_logs)")
    columns = [column[1] for column in c.fetchall()]
    if 'no_alcohol' not in columns:
        c.execute("ALTER TABLE health_logs ADD COLUMN no_alcohol BOOLEAN DEFAULT 0")
    
    conn.commit()
    conn.close()

def calculate_readiness(vf, hr, bp_sys, body_age, actual_age, social_mode, micro_workouts, water_intake, water_goal, no_alcohol):
    base_score = 100
    if vf > 10: base_score -= (vf - 10) * 1.5 
    if hr > 65: base_score -= (hr - 65) * 2
    if bp_sys > 130: base_score -= (bp_sys - 130) * 1 
    
    age_gap = body_age - actual_age
    if age_gap > 0: base_score -= age_gap * 1
        
    # 🍷 酒精與社交邏輯博弈 [cite: 38, 51]
    if social_mode:
        base_score -= 20
        if no_alcohol:
            base_score += 20  # 抵銷應酬扣分
            
    if no_alcohol:
        base_score += 10      # 肝臟修復紅利金 [cite: 45]
    
    base_score += (micro_workouts * 3)
    if water_intake >= water_goal:
        base_score += 5 
        
    return max(0, min(100, int(base_score)))

# ==========================================
# 🧠 狀態機初始化 
# ==========================================
st.set_page_config(page_title="復興守護者", page_icon="🛡️", layout="wide")
init_db()

today_date = datetime.date.today()
today_str = today_date.strftime("%Y-%m-%d")
is_weekend = today_date.weekday() >= 5 

if 'social_mode' not in st.session_state: st.session_state.social_mode = False
if 'no_alcohol' not in st.session_state: st.session_state.no_alcohol = True # 預設今日為健康日

if 'metrics' not in st.session_state: 
    st.session_state.metrics = {
        'actual_age': 54, 'body_age': 69,
        'vf': 25.0, 'muscle': 26.7, 'bmi': 33.8, 'hr': 63, 'bp_sys': 119, 'bp_dia': 79
    }
    
if 'micro_workouts' not in st.session_state: st.session_state.micro_workouts = 0 
if 'water_intake' not in st.session_state: st.session_state.water_intake = 0 

water_goal = 3000 if st.session_state.social_mode else 2000

if 'readiness_score' not in st.session_state:
    st.session_state.readiness_score = calculate_readiness(
        st.session_state.metrics['vf'], st.session_state.metrics['hr'], st.session_state.metrics['bp_sys'], 
        st.session_state.metrics['body_age'], st.session_state.metrics['actual_age'],
        st.session_state.social_mode, st.session_state.micro_workouts, st.session_state.water_intake, water_goal, st.session_state.no_alcohol
    )

# ==========================================
# 🎨 介面層：區長專屬動態儀表板
# ==========================================
st.title("🛡️ 復興守護者")
st.markdown(f"**蘇區長，早安。今天是 {today_str} {'(週末重置日)' if is_weekend else '(市政高壓期)'}**")

# --- 📥 今日數值輸入區 ---
with st.expander("📥 點此輸入今日最新數值 (同步體脂計/血壓計)", expanded=False):
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        new_actual_age = st.number_input("實際年齡", value=st.session_state.metrics['actual_age'], step=1)
        new_vf = st.number_input("內臟脂肪等級", value=st.session_state.metrics['vf'], step=0.5)
        new_bp_sys = st.number_input("收縮壓 (高壓)", value=st.session_state.metrics['bp_sys'], step=1)
    with col_b:
        new_body_age = st.number_input("身體年齡", value=st.session_state.metrics['body_age'], step=1)
        new_muscle = st.number_input("骨骼肌率 (%)", value=st.session_state.metrics['muscle'], step=0.1)
        new_bp_dia = st.number_input("舒張壓 (低壓)", value=st.session_state.metrics['bp_dia'], step=1)
    with col_c:
        new_bmi = st.number_input("BMI", value=st.session_state.metrics['bmi'], step=0.1)
        new_hr = st.number_input("安靜心率 (bpm)", value=st.session_state.metrics['hr'], step=1)
        
    if st.button("🔄 更新今日數值"):
        st.session_state.metrics.update({
            'actual_age': new_actual_age, 'body_age': new_body_age,
            'vf': new_vf, 'muscle': new_muscle, 'bmi': new_bmi, 'hr': new_hr, 'bp_sys': new_bp_sys, 'bp_dia': new_bp_dia
        })
        st.session_state.readiness_score = calculate_readiness(
            new_vf, new_hr, new_bp_sys, new_body_age, new_actual_age, 
            st.session_state.social_mode, st.session_state.micro_workouts, st.session_state.water_intake, water_goal, st.session_state.no_alcohol
        )
        st.rerun()

st.divider()

# --- 🔋 綜合狀態儀表板 ---
st.subheader("🔋 今日身體狀態儀表板")
col1, col2, col3 = st.columns(3)
with col1:
    color = "normal" if st.session_state.readiness_score >= 70 else "inverse"
    st.metric("代謝綜合評分", f"{st.session_state.readiness_score}%", "狀態穩定" if color=="normal" else "- 肝臟/代謝負載過重", delta_color=color)
with col2:
    st.metric("心血管防線 (血壓)", f"{st.session_state.metrics['bp_sys']}/{st.session_state.metrics['bp_dia']}", "優良防護中")
with col3:
    age_gap = st.session_state.metrics['body_age'] - st.session_state.metrics['actual_age']
    st.metric("代謝老化指標 (身體年齡)", f"{st.session_state.metrics['body_age']} 歲", f"老化 +{age_gap} 歲" if age_gap > 0 else f"年輕 {-age_gap} 歲", delta_color="inverse" if age_gap > 0 else "normal")

st.divider()

# --- 🌿 健康行為監控 ---
col_h1, col_h2 = st.columns(2)
with col_h1:
    st.subheader("⏱️ 零碎時間運動")
    if st.button("✅ 完成一次微訓練 (+3分)"):
        st.session_state.micro_workouts += 1
        st.session_state.readiness_score = calculate_readiness(st.session_state.metrics['vf'], st.session_state.metrics['hr'], st.session_state.metrics['bp_sys'], st.session_state.metrics['body_age'], st.session_state.metrics['actual_age'], st.session_state.social_mode, st.session_state.micro_workouts, st.session_state.water_intake, water_goal, st.session_state.no_alcohol)
        st.balloons()
        st.rerun()
with col_h2:
    st.subheader("🚫 酒精防禦")
    # 💥 核心新功能：今日沒喝酒 [cite: 55, 60]
    is_sober = st.checkbox("🍺 今日沒喝酒 (啟動代謝修復模式)", value=st.session_state.no_alcohol)
    if is_sober != st.session_state.no_alcohol:
        st.session_state.no_alcohol = is_sober
        st.session_state.readiness_score = calculate_readiness(st.session_state.metrics['vf'], st.session_state.metrics['hr'], st.session_state.metrics['bp_sys'], st.session_state.metrics['body_age'], st.session_state.metrics['actual_age'], st.session_state.social_mode, st.session_state.micro_workouts, st.session_state.water_intake, water_goal, is_sober)
        st.rerun()
    if is_sober:
        st.success("✨ 肝臟目前正處於負熵修復狀態。")
    else:
        st.warning("⚠️ 檢測到酒精攝入，燃脂效率已降至 0。")

st.divider()

# --- 💧 動態水杯 ---
st.subheader(f"💧 喝水 (目標: {water_goal} cc)")
progress = min(st.session_state.water_intake / water_goal, 1.0)
st.progress(progress)
st.write(f"目前已飲用：**{st.session_state.water_intake} cc**")
col_w1, col_w2 = st.columns(2)
with col_w1:
    if st.button("➕ 喝 250cc"):
        st.session_state.water_intake += 250
        st.rerun()
with col_w2:
    if st.button("➕ 喝 500cc"):
        st.session_state.water_intake += 500
        st.rerun()

st.divider()

# --- 🗓️ 應酬防禦與酒精衝擊警告 ---
st.subheader("🗓️ 飲食控管與應酬防禦")
if st.session_state.social_mode:
    st.error("🚨 應酬模式：當前目標為「損害控管」而非「減脂」。")
    if not st.session_state.no_alcohol:
        st.markdown(f"**酒精衝擊警報**：您的身體將有 **{1.5 if is_sober else 4} 小時** 處於零燃脂狀態。")
    
    if st.button("✅ 應酬結束 (重置為常規模式)"):
        st.session_state.social_mode = False
        st.rerun()
else:
    if st.button("🍷 臨時追加應酬 (啟動損害控管)"):
        st.session_state.social_mode = True
        st.rerun()

st.divider()

# --- 💾 存檔紀錄 ---
if st.button("💾 儲存今日完整日誌"):
    bp_str = f"{st.session_state.metrics['bp_sys']}/{st.session_state.metrics['bp_dia']}"
    conn = sqlite3.connect('fuxing_guardian_v4.db')
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO health_logs 
        (date, actual_age, body_age, visceral_fat, muscle_mass, bmi, resting_hr, blood_pressure, readiness_score, social_mode_active, micro_workouts_done, water_intake_cc, no_alcohol) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        today_str, st.session_age := st.session_state.metrics['actual_age'], st.session_state.metrics['body_age'], 
        st.session_state.metrics['vf'], st.session_state.metrics['muscle'], 
        st.session_state.metrics['bmi'], st.session_state.metrics['hr'], bp_str,
        st.session_state.readiness_score, st.session_state.social_mode, 
        st.session_state.micro_workouts, st.session_state.water_intake, st.session_state.no_alcohol
    ))
    conn.commit()
    conn.close()
    st.success("✅ 區長，今日完整日誌已成功儲存！")

# --- 📖 歷史紀錄展示 (簡化版) ---
st.subheader("📊 歷史趨勢掃描")
history_df = pd.read_sql_query("SELECT * FROM health_logs ORDER BY date DESC LIMIT 7", sqlite3.connect('fuxing_guardian_v4.db'))
if not history_df.empty:
    st.dataframe(history_df[['date', 'visceral_fat', 'readiness_score', 'no_alcohol']], hide_index=True)
