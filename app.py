import streamlit as st
import datetime
import sqlite3
import pandas as pd

# ==========================================
# 🛡️ 系統底層：本地資料庫與自動計算引擎 (Ops-AI-CRF)
# ==========================================
def init_db():
    """初始化 SQLite v3 資料庫，確保區長隱私數據本地化存儲"""
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
    """根據生理數據與行為動態計算今日身體恢復度"""
    base_score = 100
    # 內臟脂肪負荷扣分
    if vf > 10: base_score -= (vf - 10) * 1.5 
    # 自律神經與心血管負擔扣分
    if hr > 65: base_score -= (hr - 65) * 2
    if bp_sys > 130: base_score -= (bp_sys - 130) * 1 
    if social_mode: base_score -= 20 # 應酬模式預扣能量
    
    # 復原行為加分
    base_score += (micro_workouts * 3)
    if water_intake >= water_goal:
        base_score += 5 
        
    return max(0, min(100, int(base_score)))

def load_history():
    """讀取歷史健康日誌紀錄"""
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
is_weekend = today_date.weekday() >= 5 # 週六與週日判定

# ==========================================
# 🧠 狀態機初始化 (綁定蘇區長體檢基線)
# ==========================================
if 'social_mode' not in st.session_state: st.session_state.social_mode = False
if 'metrics' not in st.session_state: 
    st.session_state.metrics = {'vf': 25.0, 'muscle': 26.7, 'bmi': 33.8, 'hr': 63, 'bp_sys': 119, 'bp_dia': 79}
if 'micro_workouts' not in st.session_state: st.session_state.micro_workouts = 0 
if 'water_intake' not in st.session_state: st.session_state.water_intake = 0 

# 動態水分目標：應酬日上調以加速乙醛代謝
water_goal = 3000 if st.session_state.social_mode else 2000

if 'readiness_score' not in st.session_state:
    st.session_state.readiness_score = calculate_readiness(
        st.session_state.metrics['vf'], st.session_state.metrics['hr'], st.session_state.metrics['bp_sys'],
        st.session_state.social_mode, st.session_state.micro_workouts, st.session_state.water_intake, water_goal
    )

# ==========================================
# 🎨 介面層：區長專屬動態 UI
# ==========================================
st.title("🛡️ 復興守護者 (Fuxing Guardian)")
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
st.subheader("🔋 今日身體恢復度 (Readiness)")
col1, col2 = st.columns(2)
with col1:
    if st.session_state.readiness_score >= 70:
        st.metric("代謝綜合評分", f"{st.session_state.readiness_score}%", "狀態穩定：適合決策")
    else:
        st.metric("代謝綜合評分", f"{st.session_state.readiness_score}%", "- 肝臟/皮質醇負荷重", delta_color="inverse")
with col2:
    st.metric("心血管防線 (血壓)", f"{st.session_state.metrics['bp_sys']}/{st.session_state.metrics['bp_dia']}", "優良防護中")

st.divider()

# --- 擴充模組整合區 ---
if is_weekend:
    # 🛌 週末重置協議
    st.success("🌲 【週末重置模式啟動】清空壓力與胰島素殘留")
    st.markdown("""
    * **14小時微斷食**：建議今日早餐延後至 10:00，減少胰島素分泌。
    * **自然環境修復**：放下手機，進行 30 分鐘森林漫步，重置迷走神經。
    """)
else:
    # ⏱️ 零碎時間運動 (MED 訓練)
    st.subheader("⏱️ 零碎時間運動 (Micro-Workouts)")
    available_time = st.radio("區長，您現在有多少空檔？", ["3 分鐘", "10 分鐘", "15 分鐘"], horizontal=True)
    if "3 分鐘" in available_time: st.write("🪑 **辦公椅深蹲 (15下)** + 🧱 **靠牆伏地挺身 (15下)**")
    elif "10 分鐘" in available_time: st.write("🚶‍♂️ **原地高抬腿 (3分鐘)** + 🪜 **階梯微喘 (5分鐘)** + 🫁 **深呼吸 (2分鐘)**")
    else: st.write("⛰️ **微喘步道健行**：維持「微喘但能對話」速度步行 15 分鐘。")
    
    if st.button("✅ 完成一次微訓練 (+3分)"):
        st.session_state.micro_workouts += 1
        st.session_state.readiness_score = calculate_readiness(st.session_state.metrics['vf'], st.session_state.metrics['hr'], st.session_state.metrics['bp_sys'], st.session_state.social_mode, st.session_state.micro_workouts, st.session_state.water_intake, water_goal)
        st.balloons()
        st.rerun()

st.divider()

# --- 💧 動態水杯引擎 ---
st.subheader(f"💧 喝水進度 (目標: {water_goal} cc)")
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

# --- 🗓️ 應酬防禦與酒精衝擊分析 (關鍵升級) ---
st.subheader("🗓️ 飲食控管與應酬防禦")
with st.expander("🍽️ 查看：今日會議便當/桌菜破解法", expanded=False):
    st.markdown("1. 先吃青菜 ➔ 2. 再吃蛋白質 ➔ 3. 白飯最後吃且減半 ➔ 4. 一口肥肉配兩口菜")

if st.session_state.social_mode:
    st.warning("⚠️ 應酬防禦已啟動：嚴守 1:1 水分法則，**絕對拒絕**收尾澱粉！")
    
    st.markdown("### 🍷 酒精對內臟脂肪 (目前: 25) 的衝擊評估")
    col_alc1, col_alc2 = st.columns(2)
    with col_alc1:
        alc_type = st.selectbox("飲用酒類", ["烈酒 (高粱/威士忌)", "葡萄酒", "啤酒"])
        alc_count = st.number_input("飲用杯數", min_value=1, value=1)
    
    # 計算衝擊：酒精會暫停燃脂，碳水會直接轉化為脂肪
    burn_pause = alc_count * (1.5 if alc_type == "烈酒 (高粱/威士忌)" else 1.0)
    fat_risk = "🔥 極高 (液體麵包)" if alc_type == "啤酒" else "📈 高 (代謝路徑霸擋)"
    
    with col_alc2:
        st.info(f"🛑 **燃脂停滯**：{burn_pause} 小時")
        st.error(f"⚠️ **脂肪囤積風險**：{fat_risk}")
    
    if st.button("✅ 應酬平安結束 (解除防禦)"):
        st.session_state.social_mode = False
        st.rerun()
else:
    if st.button("🍷 臨時追加應酬 (啟動損害控管)"):
        st.session_state.social_mode = True
        st.session_state.readiness_score = calculate_readiness(st.session_state.metrics['vf'], st.session_state.metrics['hr'], st.session_state.metrics['bp_sys'], True, st.session_state.micro_workouts, st.session_state.water_intake, 3000)
        st.rerun()

st.divider()

# --- 💾 存檔與管理模組 ---
if st.button("💾 儲存今日完整日誌"):
    bp_str = f"{st.session_state.metrics['bp_sys']}/{st.session_state.metrics['bp_dia']}"
    conn = sqlite3.connect('fuxing_guardian_v3.db')
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO health_logs 
        (date, visceral_fat, muscle_mass, bmi, resting_hr, blood_pressure, readiness_score, social_mode_active, micro_workouts_done, water_intake_cc) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (today_str, st.session_state.metrics['vf'], st.session_state.metrics['muscle'], st.session_state.metrics['bmi'], st.session_state.metrics['hr'], bp_str, st.session_state.readiness_score, st.session_state.social_mode, st.session_state.micro_workouts, st.session_state.water_intake))
    conn.commit()
    conn.close()
    st.success("✅ 區長，今日完整數據已成功備份！")

st.divider()
st.subheader("📖 歷史健康管理 (History & Edit)")
tab_view, tab_edit = st.tabs(["📊 查看趨勢", "✏️ 修改/刪除"])
with tab_view:
    history_df = load_history()
    if not history_df.empty:
        history_df.columns = ['日期', '內臟脂肪', '骨骼肌(%)', 'BMI', '安靜心率', '血壓(mmHg)', '恢復度', '有應酬?', '微訓練', '喝水(cc)']
        st.dataframe(history_df, use_container_width=True, hide_index=True)
with tab_edit:
    if not history_df.empty:
        selected_date = st.selectbox("選擇日期：", history_df['日期'].tolist())
        if st.button("🗑️ 刪除該日紀錄"):
            conn = sqlite3.connect('fuxing_guardian_v3.db')
            c = conn.cursor()
            c.execute("DELETE FROM health_logs WHERE date=?", (selected_date,))
            conn.commit()
            conn.close()
            st.rerun()
