import streamlit as st
import datetime

# --- [設定] 頁面與暗黑模式強制 (UI/UX-CRF v6.4) ---
st.set_page_config(page_title="復興守護者", page_icon="🛡️", layout="centered")

# --- [邏輯] 模擬本地狀態機 (HRA-CRF v6.4) ---
if 'social_mode' not in st.session_state:
    st.session_state.social_mode = False
if 'energy_level' not in st.session_state:
    st.session_state.energy_level = 85 # 模擬初始能量電池

def toggle_social_mode():
    st.session_state.social_mode = not st.session_state.social_mode
    if st.session_state.social_mode:
        st.session_state.energy_level -= 30 # 應酬預扣能量

# --- [介面] 模組 B：後置校準層 (模糊渲染) ---
st.title("🛡️ 復興守護者")
st.markdown(f"**蘇區長，您好。今天是 {datetime.date.today().strftime('%Y-%m-%d')}**")

st.divider()

# 1. 狀態指示器 (模糊化精確數據，降低焦慮)
col1, col2 = st.columns(2)
with col1:
    if st.session_state.energy_level > 60:
        st.metric(label="今日能量電池", value=f"{st.session_state.energy_level}%", delta="狀態良好")
    else:
        st.metric(label="今日能量電池", value=f"{st.session_state.energy_level}%", delta="- 需啟動修復", delta_color="inverse")

with col2:
    if st.session_state.social_mode:
        st.error("🍷 應酬防禦已啟動")
    else:
        st.success("🟢 代謝平衡中")

st.divider()

# 2. 戰術執行：一鍵應酬模式
st.subheader("🗓️ 行程防禦協議")
if st.session_state.social_mode:
    st.warning("⚠️ 今晚有高壓行程。請於 18:00 前攝取兩顆茶葉蛋或無糖豆漿，建立腸道屏障。")
    st.info("💡 明日早晨已自動為您鎖定高強度運動，替換為「16小時溫和斷食」與「深呼吸 3 分鐘」。")
    if st.button("✅ 應酬結束 (啟動重置)"):
        toggle_social_mode()
else:
    st.write("今日無特殊高壓行程，建議維持 Zone 2 基礎有氧。")
    if st.button("🍷 啟動應酬模式 (今晚有局)"):
        toggle_social_mode()

st.divider()

# 3. 復興區微步道推薦 (地理圍欄概念)
st.subheader("⛰️ 零碎時間微訓練")
st.write("根據您的 GPS 定位，距離下個會議還有 20 分鐘：")
st.button("🚶‍♂️ 啟動：角板山行館周邊 15 分鐘微喘步道 (Zone 2)")
