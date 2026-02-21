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
    # 💥 自動遷移補丁：確保具備酒精防禦欄位
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
    
    age_gap = body_age - actual_age
    if age_gap > 0: base_score -= age_gap * 1
        
    # 🍷 酒精與社交邏輯博弈 (源自 16-4 生物反饋)
    if social_mode:
        base_score -= 20
        if no_alcohol:
            base_score += 20  # 社交防禦成功：抵銷負載 [cite: 46]
            
    if no_alcohol:
        base_score += 10      # 肝臟修復紅利金 [cite: 38]
    
    base_score += (micro_workouts * 3)
    if water_intake >= water_goal:
        base_score += 5 
        
    return max(0, min(100, int(base_score)))

def load_history():
    conn = sqlite3.connect('fuxing_guardian_v4.db')
    try:
        df = pd.read_sql_query("SELECT * FROM health_logs ORDER BY date DESC", conn)
    except:
        df = pd.DataFrame()
    conn.close()
    return df

st.set_page_config(page_title="復興守護者", page_icon="🛡️", layout="wide")
init_db()

today_date = datetime.date.today()
today_str = today_date.strftime("%Y-%m-%d")
is_weekend = today_date.weekday() >= 5 

# ==========================================
# 🧠 狀態機初始化 (源自 10-1 Code-CRF)
# ==========================================
if 'social_mode' not in st.session_state: st.session_state.social_mode = False
if 'no_alcohol' not in st.session_state: st.session_state.no_alcohol = True 

if 'metrics' not in st.session_state: 
    st.session_state.metrics = {
        'actual_age': 54, 'body_age': 69,
        'vf': 25.0, 'muscle': 26.7, 'bmi': 33.8, 'hr': 63, 'bp_sys': 119, 'bp_dia': 79
    }
    
if 'micro_workouts' not in st.session_state: st.session_state.micro_workouts = 0 
if 'water_intake' not in st.session_state: st.session_state.water_intake = 0 

water_goal = 3000 if st.session_state.social_mode else 2000

# 確保分數同步
st.session_state.readiness_score = calculate_readiness(
    st.session_state.metrics['vf'], st.session_state.metrics['hr'], st.session_state.metrics['bp_sys'], 
    st.session_state.metrics['body_age'], st.session_state.metrics['actual_age'],
    st.session_state.social_mode, st.session_state.micro_workouts, st.session_state.water_intake, water_goal, st.session_state.no_alcohol
)

# ==========================================
# 🎨 介面層：蘇區長專屬儀表板 (還原 10-3 UI 規範)
# ==========================================
st.title("🛡️ 復興守護者")
st.markdown(f"**蘇區長，早安。今天是 {today_str} {'(週末重置日)' if is_weekend else '(市政高壓期)'}**")

# --- 📥 數據輸入 ---
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
        st.rerun()

st.divider()

# --- 🔋 綜合狀態 ---
st.subheader("🔋 今日身體狀態儀表板")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("代謝綜合評分", f"{st.session_state.readiness_score}%", "狀態穩定" if st.session_state.readiness_score >= 70 else "- 代謝負荷重", delta_color="normal" if st.session_state.readiness_score >= 70 else "inverse")
with col2:
    st.metric("心血管防線 (血壓)", f"{st.session_state.metrics['bp_sys']}/{st.session_state.metrics['bp_dia']}")
with col3:
    age_gap = st.session_state.metrics['body_age'] - st.session_state.metrics['actual_age']
    st.metric("代謝老化指標", f"{st.session_state.metrics['body_age']} 歲", f"老化 +{age_gap} 歲", delta_color="inverse")

st.divider()

# --- 🌲 擴充模組整合區 (還原原始功能) ---
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
        st.balloons()
        st.rerun()

# 💥 新增酒精防禦功能
st.subheader("🚫 代謝防禦")
is_sober = st.checkbox("🍺 今日沒喝酒 (啟動肝臟修復協議)", value=st.session_state.no_alcohol)
if is_sober != st.session_state.no_alcohol:
    st.session_state.no_alcohol = is_sober
    st.rerun()

st.divider()

# --- 💧 喝水 ---
st.subheader(f"💧 喝水 (目標: {water_goal} cc)")
st.progress(min(st.session_state.water_intake / water_goal, 1.0))
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

# --- 🗓️ 飲食與應酬防禦 ---
st.subheader("🍽️ 飲食控管與應酬防禦")
with st.expander("🍽️ 會議便當/桌菜破解法", expanded=False):
    st.info("💡 核心邏輯：控制進食順序，避免血糖飆升。")
    st.markdown("1. 先吃青菜 ➔ 2. 再吃肉類 ➔ 3. 白飯最後且減半。")

if st.session_state.social_mode:
    st.error("🚨 酒精衝擊警報：內臟脂肪 (目前: 25) 面臨核彈級風險")
    if st.button("✅ 應酬平安結束 (重置模式)"):
        st.session_state.social_mode = False
        st.rerun()
else:
    if st.button("🍷 臨時追加應酬 (啟動生理損害控管)"):
        st.session_state.social_mode = True
        st.rerun()

# --- 💾 存檔 ---
if st.button("💾 儲存今日完整日誌"):
    bp_str = f"{st.session_state.metrics['bp_sys']}/{st.session_state.metrics['bp_dia']}"
    conn = sqlite3.connect('fuxing_guardian_v4.db')
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO health_logs 
        (date, actual_age, body_age, visceral_fat, muscle_mass, bmi, resting_hr, blood_pressure, readiness_score, social_mode_active, micro_workouts_done, water_intake_cc, no_alcohol) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        today_str, st.session_state.metrics['actual_age'], st.session_state.metrics['body_age'], 
        st.session_state.metrics['vf'], st.session_state.metrics['muscle'], 
        st.session_state.metrics['bmi'], st.session_state.metrics['hr'], bp_str,
        st.session_state.readiness_score, st.session_state.social_mode, 
        st.session_state.micro_workouts, st.session_state.water_intake, st.session_state.no_alcohol
    ))
    conn.commit()
    conn.close()
    st.success("✅ 數據已成功存檔！")

# ==========================================
# 📖 歷史紀錄與管理 (完全還原 Tab 功能)
# ==========================================
st.divider()
st.subheader("📖 歷史健康日誌管理")
tab1, tab2 = st.tabs(["📊 查看歷史紀錄", "✏️ 修改 / 刪除紀錄"])

with tab1:
    history_df = load_history()
    if not history_df.empty:
        st.dataframe(history_df, use_container_width=True, hide_index=True)
    else:
        st.info("目前還沒有紀錄喔！")

with tab2:
    if not history_df.empty:
        dates_list = history_df['date'].tolist()
        selected_date = st.selectbox("請選擇要修改的日期：", dates_list)
        if st.button("🗑️ 刪除這筆紀錄"):
            conn = sqlite3.connect('fuxing_guardian_v4.db')
            c = conn.cursor()
            c.execute("DELETE FROM health_logs WHERE date=?", (selected_date,))
            conn.commit()
            conn.close()
            st.warning(f"🗑️ {selected_date} 的紀錄已刪除！")
            st.rerun()
