import streamlit as st
import datetime
import sqlite3
import pandas as pd

# ==========================================
# 🛡️ 系統底層：資料庫與狀態初始化 (Ops-AI-CRF)
# ==========================================

# 1. 初始化本地資料庫 (絕對隱私，無雲端上傳)
def init_db():
    conn = sqlite3.connect('fuxing_guardian.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS daily_logs (
            date TEXT PRIMARY KEY,
            energy_level INTEGER,
            social_mode BOOLEAN,
            water_done BOOLEAN,
            squats_done BOOLEAN,
            breathing_done BOOLEAN
        )
    ''')
    conn.commit()
    conn.close()

# 2. 頁面設定 (強制暗黑模式與降低認知負荷)
st.set_page_config(page_title="復興守護者", page_icon="🛡️", layout="centered")
init_db()

# 3. 狀態機初始化 (Session State)
today_str = datetime.date.today().strftime("%Y-%m-%d")
current_hour = datetime.datetime.now().hour

if 'social_mode' not in st.session_state:
    st.session_state.social_mode = False
if 'energy_level' not in st.session_state:
    st.session_state.energy_level = 85 # 預設能量

# ==========================================
# 🎨 模組 B：UI/UX 視覺與互動層
# ==========================================

st.title("🛡️ 復興守護者 (Fuxing Guardian)")
st.markdown(f"**蘇區長，您好。今天是 {today_str}**")
st.divider()

# --- 區塊一：高階主管儀表板 (模糊渲染層) ---
st.subheader("🔋 今日能量電池")
col1, col2 = st.columns(2)

with col1:
    if st.session_state.energy_level > 60:
        st.metric(label="身體狀態", value=f"{st.session_state.energy_level}%", delta="充沛：適合視察與決策")
    else:
        st.metric(label="身體狀態", value=f"{st.session_state.energy_level}%", delta="- 疲勞：啟動溫和修復", delta_color="inverse")

with col2:
    if st.session_state.social_mode:
        st.error("🍷 應酬防禦模式：啟動中")
    else:
        st.success("🟢 代謝平衡模式：穩定")

st.divider()

# --- 區塊二：一鍵應酬防禦中心 (核心引擎) ---
st.subheader("🗓️ 晚間行程與防禦協議")
if st.session_state.social_mode:
    st.warning("⚠️ 系統偵測：今晚有高壓應酬行程。")
    st.markdown("""
    **🛡️ 損害控管戰術：**
    1. **赴宴前 (18:00前)**：請吃兩顆茶葉蛋或喝一杯無糖豆漿墊胃。
    2. **酒局中**：嚴守「1杯酒配1杯水」法則。
    3. **收尾時**：**絕對拒絕**最後的炒飯與麵線。
    """)
    st.info("💡 明晨運動已自動取消，改為 14-16 小時溫和肝臟排毒斷食。")
    
    if st.button("✅ 應酬平安結束 (點擊重置能量)"):
        st.session_state.social_mode = False
        st.session_state.energy_level -= 25 # 模擬應酬後的能量消耗
        st.rerun()
else:
    st.write("今日無特殊高壓行程，建議維持清淡飲食。")
    if st.button("🍷 臨時追加應酬 (啟動防禦)"):
        st.session_state.social_mode = True
        st.rerun()

st.divider()

# --- 區塊三：最小有效劑量 (MED) 日常任務 ---
st.subheader("⛰️ 今日起居微任務 (MED)")
st.write("針對 26.7% 骨骼肌流失防禦與自律神經穩定：")

water = st.checkbox("💧 晨間重置：已飲用 500cc 溫鹽水")
squats = st.checkbox("🦵 辦公室微護甲：已完成 15 下無負重深蹲")

with st.expander("🫁 點此展開：夜間 4-7-8 迷走神經呼吸法"):
    st.write("準備就寢前，請坐在床邊執行：")
    st.markdown("- **吸氣** 4 秒\n- **憋氣** 7 秒\n- **吐氣** 8 秒 (發出呼呼聲)")
    st.caption("重複 4 次循環，強制關閉交感神經，幫助肝臟進入深度修復。")
breathing = st.checkbox("🌙 夜間降落：已完成 4-7-8 呼吸重置")

# --- 區塊四：資料庫儲存 ---
st.divider()
if st.button("💾 儲存今日健康日誌 (本地加密)"):
    conn = sqlite3.connect('fuxing_guardian.db')
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO daily_logs 
        (date, energy_level, social_mode, water_done, squats_done, breathing_done) 
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (today_str, st.session_state.energy_level, st.session_state.social_mode, water, squats, breathing))
    conn.commit()
    conn.close()
    st.toast("✅ 區長的日誌已安全儲存於本地端！")
