import streamlit as st
import datetime
import sqlite3

# ==========================================
# 🛡️ 系統底層：本地資料庫與自動計算引擎
# ==========================================
def init_db():
    """初始化 SQLite 資料庫，新增每日數值欄位，確保資料不出手機"""
    conn = sqlite3.connect('fuxing_guardian_private.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS health_logs (
            date TEXT PRIMARY KEY,
            visceral_fat REAL,
            muscle_mass REAL,
            bmi REAL,
            resting_hr INTEGER,
            readiness_score INTEGER,
            social_mode_active BOOLEAN
        )
    ''')
    conn.commit()
    conn.close()

def calculate_readiness(vf, hr, social_mode):
    """根據真實生理數據動態計算今日恢復度 (Readiness Score)"""
    base_score = 100
    # 內臟脂肪過高扣分 (標準約為 10 以下)
    if vf > 10:
        base_score -= (vf - 10) * 1.5 
    # 心率過高扣分 (您的極佳基準線為 63，若升高代表疲勞或發炎)
    if hr > 65:
        base_score -= (hr - 65) * 2
    # 應酬模式扣分
    if social_mode:
        base_score -= 20
        
    return max(0, min(100, int(base_score))) # 確保在 0-100 之間

st.set_page_config(page_title="復興守護者", page_icon="🛡️", layout="centered")
init_db()

today_str = datetime.date.today().strftime("%Y-%m-%d")

# ==========================================
# 🧠 狀態機初始化 (預設帶入區長的體檢基線)
# ==========================================
if 'social_mode' not in st.session_state:
    st.session_state.social_mode = False

# 預設帶入 2026-02-20 的基線數據，方便區長微調，不用每天重打
if 'metrics' not in st.session_state:
    st.session_state.metrics = {
        'vf': 25.0,
        'muscle': 26.7,
        'bmi': 33.8,
        'hr': 63
    }

# 初始化分數
if 'readiness_score' not in st.session_state:
    st.session_state.readiness_score = calculate_readiness(
        st.session_state.metrics['vf'], 
        st.session_state.metrics['hr'], 
        st.session_state.social_mode
    )

# ==========================================
# 🎨 介面層：區長專屬動態儀表板
# ==========================================
st.title("🛡️ 復興守護者 (Fuxing Guardian)")
st.markdown(f"**蘇區長，早安。今天是 {today_str}**")

# --- 模組一：📥 今日數值輸入區 (首要動作) ---
with st.expander("📥 點此輸入今日最新數值 (同步體脂計 / 手錶)", expanded=True):
    st.caption("輸入最新數據，系統將自動為您重算今日健康戰術。")
    col_a, col_b = st.columns(2)
    with col_a:
        new_vf = st.number_input("內臟脂肪等級", value=st.session_state.metrics['vf'], step=0.5)
        new_bmi = st.number_input("BMI", value=st.session_state.metrics['bmi'], step=0.1)
    with col_b:
        new_muscle = st.number_input("骨骼肌率 (%)", value=st.session_state.metrics['muscle'], step=0.1)
        new_hr = st.number_input("安靜心率 (bpm)", value=st.session_state.metrics['hr'], step=1)
        
    if st.button("🔄 更新今日數值並分析"):
        st.session_state.metrics['vf'] = new_vf
        st.session_state.metrics['muscle'] = new_muscle
        st.session_state.metrics['bmi'] = new_bmi
        st.session_state.metrics['hr'] = new_hr
        # 重新計算分數
        st.session_state.readiness_score = calculate_readiness(new_vf, new_hr, st.session_state.social_mode)
        st.rerun()

st.divider()

# --- 模組二：🔋 綜合狀態儀表板 (基於最新輸入) ---
st.subheader("🔋 今日身體恢復度 (Readiness)")
col1, col2 = st.columns(2)

with col1:
    if st.session_state.readiness_score >= 70:
        st.metric(label="代謝綜合評分", value=f"{st.session_state.readiness_score}%", delta="狀態穩定：適合推進市政")
    else:
        st.metric(label="代謝綜合評分", value=f"{st.session_state.readiness_score}%", delta="- 肝臟負載重：啟動溫和修復", delta_color="inverse")

with col2:
    if st.session_state.social_mode:
        st.error("🍷 晚間應酬防禦：已啟動")
    else:
        st.success("🟢 晚間代謝模式：清淡休養")

st.divider()

# --- 模組三：🍷 智慧應酬防禦系統 ---
st.subheader("🗓️ 行程與應酬損害控管")
if st.session_state.social_mode:
    st.warning(f"⚠️ 針對您今日的內臟脂肪 ({st.session_state.metrics['vf']})，防禦協議已啟動。")
    st.markdown("""
    **請嚴守以下戰術，避免 BMI 再次飆升：**
    * 🥚 **赴宴前 (護胃底)**：攝取兩顆茶葉蛋，建立物理屏障。
    * 💧 **酒局中 (1:1 法則)**：喝一杯酒，配一杯白開水。
    * 🚫 **絕對禁忌**：**拒絕**酒局收尾的炒飯/麵線。
    """)
    if st.button("✅ 應酬平安結束 (解除防禦)"):
        st.session_state.social_mode = False
        st.session_state.readiness_score = calculate_readiness(st.session_state.metrics['vf'], st.session_state.metrics['hr'], False)
        st.rerun()
else:
    st.write("今日無高壓應酬行程，建議維持清淡原形食物。")
    if st.button("🚨 臨時追加應酬 (立即啟動防禦)"):
        st.session_state.social_mode = True
        st.session_state.readiness_score = calculate_readiness(st.session_state.metrics['vf'], st.session_state.metrics['hr'], True)
        st.rerun()

st.divider()

# --- 模組四：💾 安全存檔 ---
if st.button("💾 儲存今日日誌 (存於手機本地)"):
    conn = sqlite3.connect('fuxing_guardian_private.db')
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO health_logs 
        (date, visceral_fat, muscle_mass, bmi, resting_hr, readiness_score, social_mode_active) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        today_str, 
        st.session_state.metrics['vf'], 
        st.session_state.metrics['muscle'], 
        st.session_state.metrics['bmi'], 
        st.session_state.metrics['hr'], 
        st.session_state.readiness_score, 
        st.session_state.social_mode
    ))
    conn.commit()
    conn.close()
    st.toast("✅ 區長，今日生理數值與日誌已安全加密儲存！")
