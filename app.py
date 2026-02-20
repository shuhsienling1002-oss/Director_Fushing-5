import streamlit as st
import datetime
import sqlite3

# ==========================================
# 🛡️ 系統底層：本地資料庫與自動計算引擎 (Ops-AI-CRF)
# ==========================================
def init_db():
    """初始化 SQLite 資料庫 (已升級為 v2 避免欄位衝突)"""
    conn = sqlite3.connect('fuxing_guardian_v2.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS health_logs (
            date TEXT PRIMARY KEY,
            visceral_fat REAL,
            muscle_mass REAL,
            bmi REAL,
            resting_hr INTEGER,
            readiness_score INTEGER,
            social_mode_active BOOLEAN,
            micro_workouts_done INTEGER,
            water_intake_cc INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def calculate_readiness(vf, hr, social_mode, micro_workouts, water_intake, water_goal):
    """加入「微型運動」與「水份達標」的正向加分機制"""
    base_score = 100
    if vf > 10: base_score -= (vf - 10) * 1.5 
    if hr > 65: base_score -= (hr - 65) * 2
    if social_mode: base_score -= 20
    
    # 努力回饋：運動加分與喝水加分
    base_score += (micro_workouts * 3)
    if water_intake >= water_goal:
        base_score += 5 
        
    return max(0, min(100, int(base_score)))

st.set_page_config(page_title="復興守護者", page_icon="🛡️", layout="centered")
init_db()

today_date = datetime.date.today()
today_str = today_date.strftime("%Y-%m-%d")
is_weekend = today_date.weekday() >= 5 # 判斷是否為週六或週日

# ==========================================
# 🧠 狀態機初始化 (預設帶入區長的體檢基線)
# ==========================================
if 'social_mode' not in st.session_state: st.session_state.social_mode = False
if 'metrics' not in st.session_state: st.session_state.metrics = {'vf': 25.0, 'muscle': 26.7, 'bmi': 33.8, 'hr': 63}
if 'micro_workouts' not in st.session_state: st.session_state.micro_workouts = 0 
if 'water_intake' not in st.session_state: st.session_state.water_intake = 0 

# 動態水分目標：平時 2000cc，應酬日強制提升至 3000cc 加速代謝
water_goal = 3000 if st.session_state.social_mode else 2000

if 'readiness_score' not in st.session_state:
    st.session_state.readiness_score = calculate_readiness(
        st.session_state.metrics['vf'], st.session_state.metrics['hr'], 
        st.session_state.social_mode, st.session_state.micro_workouts,
        st.session_state.water_intake, water_goal
    )

# ==========================================
# 🎨 介面層：區長專屬動態儀表板
# ==========================================
st.title("🛡️ 復興守護者 (Fuxing Guardian)")
st.markdown(f"**蘇區長，早安。今天是 {today_str} {'(週末重置日)' if is_weekend else '(市政高壓期)'}**")

# --- 📥 今日數值輸入區 ---
with st.expander("📥 點此輸入今日最新數值 (同步體脂計)", expanded=False):
    col_a, col_b = st.columns(2)
    with col_a:
        new_vf = st.number_input("內臟脂肪等級", value=st.session_state.metrics['vf'], step=0.5)
        new_bmi = st.number_input("BMI", value=st.session_state.metrics['bmi'], step=0.1)
    with col_b:
        new_muscle = st.number_input("骨骼肌率 (%)", value=st.session_state.metrics['muscle'], step=0.1)
        new_hr = st.number_input("安靜心率 (bpm)", value=st.session_state.metrics['hr'], step=1)
        
    if st.button("🔄 更新今日數值"):
        st.session_state.metrics.update({'vf': new_vf, 'muscle': new_muscle, 'bmi': new_bmi, 'hr': new_hr})
        st.session_state.readiness_score = calculate_readiness(new_vf, new_hr, st.session_state.social_mode, st.session_state.micro_workouts, st.session_state.water_intake, water_goal)
        st.rerun()

st.divider()

# --- 🔋 綜合狀態儀表板 ---
st.subheader("🔋 今日身體恢復度 (Readiness)")
col1, col2 = st.columns(2)
with col1:
    if st.session_state.readiness_score >= 70:
        st.metric("代謝綜合評分", f"{st.session_state.readiness_score}%", "狀態穩定")
    else:
        st.metric("代謝綜合評分", f"{st.session_state.readiness_score}%", "- 肝臟/皮質醇負載重", delta_color="inverse")
with col2:
    st.metric("今日微訓練完成", f"{st.session_state.micro_workouts} 次", "防禦骨骼肌流失")

st.divider()

# ==========================================
# 🌟 新增擴充模組整合區
# ==========================================

if is_weekend:
    # --- 🛌 週末皮質醇卸載協議 ---
    st.success("🌲 【週末重置模式啟動】清空一週壓力與胰島素殘留")
    st.markdown("""
    * **14小時微斷食**：建議今日早餐延後至 10:00，讓肝臟與腸胃徹底休假。
    * **大自然迷走神經重置**：放下手機，前往拉拉山或角板山進行 30 分鐘森林漫步，強制降低皮質醇。
    """)
else:
    # --- ⏱️ 平日：隨時微護甲 ---
    st.subheader("⏱️ 隨時微護甲 (零碎時間訓練)")
    available_time = st.radio("區長，您現在有多少空檔？", ["3 分鐘 (等車)", "10 分鐘 (辦公室)", "15 分鐘 (視察)"], horizontal=True)
    if "3 分鐘" in available_time:
        st.write("🪑 **辦公椅深蹲 (15下)** + 🧱 **靠牆伏地挺身 (15下)**")
    elif "10 分鐘" in available_time:
        st.write("🚶‍♂️ **原地高抬腿 (3分鐘)** + 🪜 **階梯微喘 (5分鐘)** + 🫁 **深呼吸 (2分鐘)**")
    else:
        st.write("⛰️ **微喘步道健行**：維持「微喘但還能對話」的速度連續步行 15 分鐘。")
    
    if st.button("✅ 完成一次微訓練 (+3分)"):
        st.session_state.micro_workouts += 1
        st.session_state.readiness_score = calculate_readiness(st.session_state.metrics['vf'], st.session_state.metrics['hr'], st.session_state.social_mode, st.session_state.micro_workouts, st.session_state.water_intake, water_goal)
        st.balloons()
        st.rerun()

st.divider()

# --- 💧 動態水杯引擎 ---
st.subheader(f"💧 動態水分代謝沖刷 (目標: {water_goal} cc)")
progress = min(st.session_state.water_intake / water_goal, 1.0)
st.progress(progress)
st.write(f"目前已飲用：**{st.session_state.water_intake} cc**")

col_w1, col_w2, col_w3 = st.columns(3)
with col_w1:
    if st.button("➕ 喝了一杯水 (250cc)"):
        st.session_state.water_intake += 250
        st.session_state.readiness_score = calculate_readiness(st.session_state.metrics['vf'], st.session_state.metrics['hr'], st.session_state.social_mode, st.session_state.micro_workouts, st.session_state.water_intake, water_goal)
        st.rerun()
with col_w2:
    if st.button("➕ 喝了一瓶水 (500cc)"):
        st.session_state.water_intake += 500
        st.session_state.readiness_score = calculate_readiness(st.session_state.metrics['vf'], st.session_state.metrics['hr'], st.session_state.social_mode, st.session_state.micro_workouts, st.session_state.water_intake, water_goal)
        st.rerun()

st.divider()

# --- 🍱 會議便當與應酬防禦系統 ---
st.subheader("🗓️ 飲食控管與應酬防禦")

with st.expander("🍽️ 點此查看：今日會議便當/桌菜破解法", expanded=False):
    st.info("💡 核心邏輯：控制進食順序，避免血糖飆升囤積脂肪。")
    st.markdown("""
    1. **先建立纖維網**：吃掉便當裡的所有青菜。
    2. **蛋白質護底**：吃掉主食肉類（如排骨/雞腿，建議去皮）。
    3. **碳水減半**：白飯最後吃，且**最多只吃一半**。
    4. **桌菜應對**：吃一口肥肉，請務必配兩口青菜代償。
    """)

if st.session_state.social_mode:
    st.warning("⚠️ 應酬防禦已啟動：請堅守 1:1 水分法則，**絕對拒絕**收尾澱粉！")
    if st.button("✅ 應酬平安結束 (解除防禦)"):
        st.session_state.social_mode = False
        st.rerun()
else:
    if st.button("🍷 臨時追加應酬 (立即上調水分目標並啟動防禦)"):
        st.session_state.social_mode = True
        st.session_state.readiness_score = calculate_readiness(st.session_state.metrics['vf'], st.session_state.metrics['hr'], True, st.session_state.micro_workouts, st.session_state.water_intake, 3000)
        st.rerun()

# --- 💾 安全存檔 ---
st.divider()
if st.button("💾 儲存今日日誌 (存於雲端伺服器空間)"):
    conn = sqlite3.connect('fuxing_guardian_v2.db')
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO health_logs 
        (date, visceral_fat, muscle_mass, bmi, resting_hr, readiness_score, social_mode_active, micro_workouts_done, water_intake_cc) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        today_str, st.session_state.metrics['vf'], st.session_state.metrics['muscle'], 
        st.session_state.metrics['bmi'], st.session_state.metrics['hr'], 
        st.session_state.readiness_score, st.session_state.social_mode, 
        st.session_state.micro_workouts, st.session_state.water_intake
    ))
    conn.commit()
    conn.close()
    st.toast("✅ 區長，今日完整日誌已成功儲存！")
