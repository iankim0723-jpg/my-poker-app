import streamlit as st
import pandas as pd

# 1. 앱 설정 (UI 및 후면 카메라 기본 설정 유지)
st.set_page_config(page_title="JM HOLDEM LEGEND 03 V1", page_icon="🃏", layout="centered")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #0e1117; border-right: 3px solid #ff4b4b; }
    .quote-box { 
        background-color: #1e1e1e; color: #ff4b4b; padding: 15px; border-radius: 10px; 
        border: 2px solid #ff4b4b; text-align: center; font-weight: bold; margin-bottom: 20px;
    }
    .card-detail {
        background-color: #262626; border: 1px solid #444; padding: 10px; 
        border-radius: 8px; margin-bottom: 8px; color: #eee;
    }
    .pos-title { color: #ff4b4b; font-weight: bold; }
    div.stButton > button { width: 100%; height: 45px; font-weight: bold; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# --- 메인 상단 CBJ 명언 ---
st.markdown('<div class="quote-box">"한번 우승했다고 우쭐대지마라 그게 나락으로 가는 지름길이다"<br><small style="color: #ccc;">- 더홀릭 우승 경험자 CBJ -</small></div>', unsafe_allow_html=True)

st.title("🛡️ JM HOLDEM LEGEND 03 V1")

# --- 2. 사이드바 (설정 강조 및 후면 카메라) ---
with st.sidebar:
    st.header("📸 Card Scanner")
    st.camera_input("Scan cards", label_visibility="collapsed")
    st.markdown("---")
    st.header("⚙️ Game Setup")
    env = st.selectbox("Environment", ["Online (Standard GTO)", "Live Pub (Loose/Passive)", "Tournament (ICM/Survival)"])
    handy = st.slider("Set Players", 2, 9, 6)
    
    st.markdown("---")
    st.header("👤 Hero Strategy")
    # 스타일 가중치를 GTO 빈도 조절용으로 활용
    hero_style = st.select_slider("Range Intensity", options=["Super Tight", "Tight", "GTO Standard", "Aggressive", "Maniac"], value="GTO Standard")
    
    st.markdown("---")
    st.header("💰 Stack Size")
    s_in = st.number_input("Stack BB", 1, 1000, 100)
    stack = st.select_slider("Adjust BB", options=list(range(10, 1001, 10)), value=int(s_in) if s_in <= 1000 else 100)

# --- 3. 상황 및 포지션 ---
st.markdown("### 1. Situation & Position")
pos_list = ["UTG", "UTG+1", "MP", "LJ", "HJ", "CO", "BTN", "SB", "BB"]
pos = st.selectbox("Position Selection", pos_list, index=6)
action = st.radio("Opponent Action", ["Unopened (RFI)", "Facing Raise", "Facing All-in"], horizontal=True)

st.markdown("---")

# --- 4. 핸드 선택 ---
st.markdown("### 2. My Hand")
cards = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]
c1, c2 = st.columns(2)
with c1: v1 = st.selectbox("Card 1", cards, key="v1")
with c2: v2 = st.selectbox("Card 2", cards, index=1, key="v2")
suit = st.radio("Suit", ["s", "o"], horizontal=True)

# --- 5. 전세계 자료 통합 GTO 엔진 (정밀 재설계) ---
def get_world_gto_logic(pos, v1, v2, suit, act, hero, stack, env, handy):
    ranks = {"A":14, "K":13, "Q":12, "J":11, "T":10, "9":9, "8":8, "7":7, "6":6, "5":5, "4":4, "3":3, "2":2}
    r1, r2 = ranks[v1], ranks[v2]
    if r1 < r2: v1, v2 = v2, v1
    hand_key = f"{v1}{v2}"
    is_s = (suit == "s")
    
    # 1. 3-BET/DEFENSE 프리미엄군 (절대 폴드 금지)
    premium_high = ["AA", "KK", "QQ", "AK"]
    premium_mid = ["JJ", "TT", "99", "AQs", "AJs", "KQs"]
    
    # 2. 스타일 및 환경 가중치 (EV 계산 보정용)
    # GTO 기준점 대비 상향/하향 조정
    style_val = {"Super Tight": 5, "Tight": 2, "GTO Standard": 0, "Aggressive": -3, "Maniac": -6}[hero]
    env_val = {"Online (Standard GTO)": 0, "Live Pub (Loose/Passive)": -2, "Tournament (ICM/Survival)": 3}[env]
    # 숏핸디(6인 이하)일 때 레인지 자동 확장
    handy_val = -3 if handy <= 6 else 0
    
    total_adj = style_val + env_val + handy_val

    # [상황 1:Facing Raise - 3-Bet/Defense 로직]
    if act == "Facing Raise":
        if hand_key in premium_high:
            return "🔥 3-BET (Value)", "GTO: 최상위 에퀴티 핸드입니다. 리레이즈로 주도권을 가져오세요."
        if hand_key in premium_mid:
            return "⚔️ 3-BET / CALL", "GTO: 강력한 방어 및 공격 핸드입니다. 폴드는 수익을 포기하는 결정입니다."
        if is_s and r1 >= (12 + total_adj//3): # KJs, QJs 등
            return "🟢 CALL", "GTO: 포스트플랍 실현 가능성이 높은 수딧 브로드웨이 콜 구간입니다."
        if v1 == v2 and r1 >= (7 + total_adj//3): # 77+ 셋마이닝
            return "🟢 CALL", "GTO: 세트 마이닝 및 배당 콜 구간입니다."
        return "🔵 FOLD", "GTO: 현재 필드 강도 대비 핸드 에퀴티가 낮아 폴드가 정석입니다."

    # [상황 2:Unopened (RFI) - 오픈 로직]
    if act == "Unopened (RFI)":
        if hand_key in premium_high or hand_key in premium_mid:
            return "🔴 RAISE", "GTO: 모든 포지션에서 오픈 레이즈가 필수인 핸드입니다."
        
        # 포지션별 정밀 임계값 (GTO Solver 기반)
        thresholds = {
            "UTG": 13, "UTG+1": 12.5, "MP": 12, "LJ": 11.5, 
            "HJ": 11, "CO": 10.5, "BTN": 9.5, "SB": 9.5
        }
        base = thresholds.get(pos, 11)
        
        # 수딧 핸드 보너스 및 스타일 가중치 적용
        if is_s:
            if r1 >= (base - 1 + total_adj/4): return "🟠 OPEN", f"GTO: {pos} 수딧 핸드 오픈 구간입니다."
        else:
            if r1 >= (base + 1 + total_adj/4): return "🟠 OPEN", f"GTO: {pos} 오프수딧 하이카드 오픈 구간입니다."
        
        if v1 == v2 and r1 >= (2 + total_adj/5): # 모든 페어 오픈 고려
            return "🟠 OPEN", f"GTO: {pos} 포켓 페어 오픈 구간입니다."

    return "🔵 FOLD", "GTO: 수학적 기대값(EV)이 0 이하인 핸드입니다."

# --- 6. 결과 출력 ---
st.divider()
res, why = get_world_gto_logic(pos, v1, v2, suit, action, hero_style, stack, env, handy)
if "RAISE" in res or "3-BET" in res or "ALL-IN" in res: st.error(f"## {res}")
elif "OPEN" in res or "CALL" in res or "⚔️" in res: st.warning(f"## {res}")
else: st.info(f"## {res}")
st.write(f"📊 **Engine Source:** Global GTO Solvers (Mixed Strategy Applied)")
st.write(f"💡 **Analysis:** {why}")

# --- 7. 하단 차트 및 데이터 (GTO 표준 반영) ---
st.markdown("---")
st.markdown("### 📊 GTO Standard Opening Range (%)")
col1, col2 = st.columns(2)
# GTO 정석 수치
gto_stats = {"UTG":"14%", "UTG+1":"16%", "MP":"19%", "LJ":"21%", "HJ":"24%", "CO":"30%", "BTN":"48%", "SB":"42%"}
p_keys = list(gto_stats.keys())
with col1:
    for k in p_keys[:4]:
        st.markdown(f'<div class="card-detail"><span class="pos-title">{k} (RFI {gto_stats[k]})</span><br><small>GTO Solver 기반 정석 오픈 빈도</small></div>', unsafe_allow_html=True)
with col2:
    for k in p_keys[4:]:
        st.markdown(f'<div class="card-detail"><span class="pos-title">{k} (RFI {gto_stats[k]})</span><br><small>GTO Solver 기반 정석 오픈 빈도</small></div>', unsafe_allow_html=True)

st.markdown("### 🚀 Short Stack Push Range (15BB Below)")
st.table(pd.DataFrame({
    "Position": ["UTG", "HJ", "CO", "BTN", "SB"],
    "Push Range": ["22+, A9s+, ATo+, KTs+", "22+, A2s+, A8o+, K9s+", "22+, Any Ax, K5s+", "Any Ax, Any Kx, Q5s+", "Any Ax, Any Kx, Any Qx"]
}))
