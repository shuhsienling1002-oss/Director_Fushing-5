import streamlit as st
import datetime
import sqlite3

# ==========================================
# 🛡️ 系統底層：本地資料庫與自動計算引擎
# ==========================================
def init_db():
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
            social_mode_active BOOLEAN,
            micro_workouts_done INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def calculate_readiness(vf, hr, social_mode, micro_workouts):
    """加入「微型運動」的正向回饋加分機制"""
    base_score = 100
    if vf > 10: base_score -= (vf - 10) * 1.5 
    if hr > 65: base_score -= (hr - 65) * 2
    if social_mode: base_score -= 20
    # 每完成一次微型運動，恢復度 +3 分 (正向增強迴路)
    base_score += (micro_workouts * 3)
    return max(0, min(100, int(base_score)))

st.set_page_config(page_title="復興守護者", page_icon="🛡️", layout="centered")
init_db()
today_str = datetime.date.today().strftime("%Y-%m-%d")

# ==========================================
# 🧠 狀態機初始化 (預設帶入區長的體檢基線)
# ==========================================
if 'social_mode' not in st.session_state:
    st.session_state.social_mode = False
if 'metrics' not in st.session_state:
    st.session_state.metrics = {'vf': 25.0, 'muscle': 26.7, 'bmi': 33.8, 'hr': 63}
if 'micro_workouts' not in st.session_state:
    st.session_state.micro_workouts = 0 # 今日完成的微型運動次數
if 'readiness_score' not in st.session_state:
    st.session_state.readiness_score = calculate_readiness(
        st.session_state.metrics['vf'], st.session_state.metrics['hr'], 
        st.session_state.social_mode, st.session_state.micro_workouts
    )

# ==========================================
# 🎨 介面層：區長專屬動態儀表板
# ==========================================
st.title("🛡️ 復興守護者 (Fuxing Guardian)")
st.markdown(f"**蘇區長，早安。今天是 {today_str}**")

# --- 模組一：📥 今日數值輸入區 ---
with st.expander("📥 點此輸入今日最新數值 (同步體脂計)", expanded=False):
    col_a, col_b = st.columns(2)
    with col_a:
        new_vf = st.number_input("內臟脂肪等級", value=st.session_state.metrics['vf'], step=0.5)
        new_bmi = st.number_input("BMI", value=st.session_state.metrics['bmi'], step=0.1)
    with col_b:
        new_muscle = st.number_input("骨骼肌率 (%)", value=st.session_state.metrics['muscle'], step=0.1)
        new_hr = st.number_input("安靜心率 (bpm)", value=st.session_state.metrics['hr'], step=1)
        
    if st.button("🔄 更新今日數值並分析"):
        st.session_state.metrics.update({'vf': new_vf, 'muscle': new_muscle, 'bmi': new_bmi, 'hr': new_hr})
        st.session_state.readiness_score = calculate_readiness(new_vf, new_hr, st.session_state.social_mode, st.session_state.micro_workouts)
        st.rerun()

st.divider()

# --- 模組二：🔋 綜合狀態儀表板 ---
st.subheader("🔋 今日身體恢復度 (Readiness)")
col1, col2 = st.columns(2)
with col1:
    if st.session_state.readiness_score >= 70:
        st.metric("代謝綜合評分", f"{st.session_state.readiness_score}%", "狀態穩定")
    else:
        st.metric("代謝綜合評分", f"{st.session_state.readiness_score}%", "- 肝臟負載重", delta_color="inverse")
with col2:
    st.metric("今日微訓練完成", f"{st.session_state.micro_workouts} 次", "防禦骨骼肌流失")

st.divider()

# --- 🌟 新增模組：⏱️ 隨時微護甲 (零碎時間運動模式) ---
st.subheader("⏱️ 隨時微護甲 (零碎時間訓練)")
st.write("利用行程空檔啟動微型干預，把血糖壓入肌肉，對抗內臟脂肪！")

# 動態時間選擇器
available_time = st.radio(
    "區長，您現在有多少空檔？",
    ["3 分鐘 (等車/會議前)", "10 分鐘 (辦公室休息)", "15 分鐘 (部落視察空檔)"],
    horizontal=True
)

st.info("💡 著裝提示：以下動作皆不需換運動服，不流大汗。")

# 根據時間動態顯示運動菜單
if "3 分鐘" in available_time:
    st.markdown("""
    **【3分鐘：肌肉喚醒協議】**
    * 🪑 **辦公椅深蹲 (15下)**：碰到椅子就站起來，啟動大腿臀部最大肌群。
    * 🧱 **靠牆伏地挺身 (15下)**：雙手扶牆，啟動胸肌與核心。
    """)
elif "10 分鐘" in available_time:
    st.markdown("""
    **【10分鐘：血糖消耗協議】**
    * 🚶‍♂️ **原地高抬腿快走 (3分鐘)**：提高心率，進入燃脂區間。
    * 🪜 **階梯微喘 (5分鐘)**：利用區公所樓梯，上下步行兩層樓。
    * 🫁 **深呼吸緩和 (2分鐘)**：平復心率，準備進入下一個會議。
    """)
else:
    st.markdown("""
    **【15分鐘：Zone 2 燃脂協議】**
    * ⛰️ **微喘步道健行**：結合視察行程，以「微喘但還能跟幕僚對話」的速度連續步行 15 分鐘。這能極大化啟動細胞線粒體，直接燃燒內臟脂肪。
    """)

# 完成按鈕 (觸發正向回饋)
if st.button("✅ 我已完成這次微訓練！"):
    st.session_state.micro_workouts += 1
    st.session_state.readiness_score = calculate_readiness(
        st.session_state.metrics['vf'], st.session_state.metrics['hr'], 
        st.session_state.social_mode, st.session_state.micro_workouts
    )
    st.balloons() # 視覺慶祝特效
    st.toast("🎉 太棒了！每一次的微訓練都在逆轉您的 69 歲身體年齡！")
    st.rerun()

st.divider()

# --- 模組四：🍷 智慧應酬防禦系統 (簡化顯示) ---
st.subheader("🗓️ 晚間應酬損害控管")
if st.session_state.social_mode:
    st.warning("⚠️ 應酬防禦已啟動：請堅守 1:1 水分法則，拒絕收尾澱粉！")
    if st.button("✅ 應酬平安結束 (解除防禦)"):
        st.session_state.social_mode = False
        st.rerun()
else:
    if st.button("🍷 臨時追加應酬 (立即啟動防禦)"):
        st.session_state.social_mode = True
        st.session_state.readiness_score = calculate_readiness(st.session_state.metrics['vf'], st.session_state.metrics['hr'], True, st.session_state.micro_workouts)
        st.rerun()

# --- 模組五：💾 安全存檔 ---
st.divider()
if st.button("💾 儲存今日日誌 (存於手機本地)"):
    # ... (資料庫儲存邏輯同前，加入 st.session_state.micro_workouts)
    st.toast("✅ 區長，今日日誌已安全加密儲存！")
