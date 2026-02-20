import streamlit as st
import datetime
import sqlite3
import pandas as pd  # 新增：用來讀取資料庫並畫出漂亮的表格

# ==========================================
# 🛡️ 系統底層：本地資料庫與自動計算引擎 (Ops-AI-CRF)
# ==========================================
def init_db():
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
    base_score = 100
    if vf > 10: base_score -= (vf - 10) * 1.5 
    if hr > 65: base_score -= (hr - 65) * 2
    if social_mode: base_score -= 20
    base_score += (micro_workouts * 3)
    if water_intake >= water_goal:
        base_score += 5 
    return max(0, min(100, int(base_score)))

# --- 新增：讀取歷史紀錄的函數 ---
def load_history():
    conn = sqlite3.connect('fuxing_guardian_v2.db')
    # 將資料庫的內容讀取成表格格式，並依照日期由新到舊排序
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
# 🧠 狀態機初始化 
# ==========================================
if 'social_mode' not in st.session_state: st.session_state.social_mode = False
if 'metrics' not in st.session_state: st.session_state.metrics = {'vf': 25.0, 'muscle': 26.7, 'bmi': 33.8, 'hr': 63}
if 'micro_workouts' not in st.session_state: st.session_state.micro_workouts = 0 
if 'water_intake' not in st.session_state: st.session_state.water_intake = 0 

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

if is_weekend:
    st.success("🌲 【週末重置模式啟動】清空一週壓力與胰島素殘留")
    st.markdown("""
    * **14小時微斷食**：建議今日早餐延後至 10:00，讓肝臟與腸胃徹底休假。
    * **大自然迷走神經重置**：放下手機，前往拉拉山或角板山進行 30 分鐘森林漫步，強制降低皮質醇。
    """)
else:
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

st.subheader(f"💧 動態水分代謝沖刷 (目標: {water_goal} cc)")
progress = min(st.session_state.water_intake / water_goal, 1.0)
st.progress(progress)
st.write(f"目前已飲用：**{st.session_state.water_intake} cc**")

col_w1, col_w2, col_w3 = st.columns(3)
with col_w1:
    if st.button("➕ 喝一杯水 (250cc)"):
        st.session_state.water_intake += 250
        st.session_state.readiness_score = calculate_readiness(st.session_state.metrics['vf'], st.session_state.metrics['hr'], st.session_state.social_mode, st.session_state.micro_workouts, st.session_state.water_intake, water_goal)
        st.rerun()
with col_w2:
    if st.button("➕ 喝一瓶水 (500cc)"):
        st.session_state.water_intake += 500
        st.session_state.readiness_score = calculate_readiness(st.session_state.metrics['vf'], st.session_state.metrics['hr'], st.session_state.social_mode, st.session_state.micro_workouts, st.session_state.water_intake, water_goal)
        st.rerun()

st.divider()

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
    st.success("✅ 區長，今日完整日誌已成功儲存！")

# ==========================================
# 📖 新增模組：歷史紀錄檢視區塊
# ==========================================
st.divider()
st.subheader("📖 歷史健康日誌 (History Logs)")
with st.expander("點此查看過去儲存的紀錄", expanded=False):
    history_df = load_history()
    if not history_df.empty:
        # 重新命名欄位讓區長更容易閱讀
        history_df.columns = ['日期', '內臟脂肪', '骨骼肌(%)', 'BMI', '安靜心率', '綜合評分', '有應酬?', '微訓練(次)', '喝水量(cc)']
        st.dataframe(history_df, use_container_width=True, hide_index=True)
    else:
        st.info("目前還沒有紀錄喔！請按下方的儲存按鈕來建立第一筆日誌。")
