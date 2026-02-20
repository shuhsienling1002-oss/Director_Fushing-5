import streamlit as st
import datetime

# --- UI/UX 暗黑模式與設定 ---
st.set_page_config(page_title="復興守護者 24H", page_icon="🛡️", layout="centered")

# --- 模擬狀態機 (Session State) ---
if 'social_mode' not in st.session_state:
    st.session_state.social_mode = False
if 'drank_last_night' not in st.session_state:
    st.session_state.drank_last_night = False

# 取得當前小時 (用於動態顯示起居任務)
current_hour = datetime.datetime.now().hour

def toggle_social():
    st.session_state.social_mode = not st.session_state.social_mode
    if st.session_state.social_mode:
        st.session_state.drank_last_night = True # 假設今晚應酬，明早啟動代償

st.title("🛡️ 復興守護者：24H 生理節律")
st.divider()

# --- 根據時間動態渲染生活起居任務 ---
st.subheader("📍 當下最佳行動 (Next Best Action)")

if 5 <= current_hour < 9:
    st.info("🌅 【晨間重置期】")
    st.checkbox("💧 飲用 500cc 溫鹽水 (沖刷代謝物)")
    st.checkbox("☀️ 戶外接觸陽光 10 分鐘 (重置褪黑激素)")
    if st.session_state.drank_last_night:
        st.error("🚨 昨夜應酬檢測：今日強制跳過早餐，執行 16 小時斷食，僅限黑咖啡/水。")
    else:
        st.success("🟢 今日可正常享用高蛋白早餐。")

elif 9 <= current_hour < 17:
    st.info("⛰️ 【高壓辦公期】")
    st.write("利用會議空檔，防止骨骼肌流失：")
    st.checkbox("🦵 完成 15 下辦公椅深蹲 (激活大腿肌群)")
    st.checkbox("🥗 午餐防禦：順序必須是「菜 ➔ 肉 ➔ 飯」")

elif 17 <= current_hour < 21:
    st.info("🍷 【晚間防禦期】")
    if st.session_state.social_mode:
        st.warning("⚠️ 應酬防禦已啟動！")
        st.checkbox("🥚 赴宴前：已吃兩顆茶葉蛋墊胃")
        st.checkbox("🚫 酒局中：拒絕最後一道炒飯/麵線")
        st.checkbox("💧 飲酒法則：一杯酒配一杯水")
    else:
        st.success("🟢 今晚無應酬，建議 19:30 前完成晚餐。")
        if st.button("🍷 臨時追加應酬 (啟動損害控管)"):
            toggle_social()

else:
    st.info("🌙 【夜間降落期】")
    st.write("強制降低皮質醇，準備進入深度修復：")
    st.checkbox("🚿 已洗熱水澡 (促使核心降溫)")
    st.checkbox("🫁 躺床後執行 4-7-8 呼吸法 (4次循環)")
    if st.session_state.social_mode:
        if st.button("✅ 應酬結束，準備就寢 (重置系統)"):
            st.session_state.social_mode = False

st.divider()

# --- 隱藏焦慮數據，只顯示趨勢 (模糊渲染層) ---
st.subheader("📊 身體防線狀態")
col1, col2 = st.columns(2)
col1.metric("內臟脂肪壓力", "警戒中", delta="利用微型深蹲對抗", delta_color="off")
col2.metric("心血管代償", "優良", delta="BP 119 / HR 63", delta_color="normal")
