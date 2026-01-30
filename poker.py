import streamlit as st
import pandas as pd

# 1. 앱 설정 (UI 유지)
st.set_page_config(page_title="JM HOLDEM LEGEND 03 V1", page_icon="🃏", layout="centered")

# CSS: 사이드바 및 UI 디자인 유지
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

# --- 2. 사이드바 (카메라 및 설정) ---
with st.sidebar:
    st.header("📸 Card Scanner")
    # [수정] 카메라 기본값을 후면(외부) 카메라로 설정 시도
    # 환경에 따라 브라우저에서 '후면'을 선택해야 할 수 있으나, 기본 입력을 활성화합니다.
    captured_image = st.camera_input("Scan your cards", label_visibility="collapsed")
    
    st.markdown("---")
    st.header("⚙️ Game Setup")
    env = st.selectbox("Environment", ["Online (Standard)", "Live Pub (Loose)", "Tournament (ICM)"])
    h_in = st.number_input("Handy (Players)", 2, 9, 6)
    handy = st.slider("Set Players", 2, 9, int(h_in))
    
    st.markdown("---")
    st.header("👤 My Style")
    hero_style = st.select_slider("Hero Strategy", options=["Very Tight", "Tight", "Standard", "Loose", "Very Loose"], value="Standard")
    
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

# --- 5. GTO 실전 로직 (AKs 보정 및 환경 반영) ---
def get_gto_logic(pos, v1, v2, suit, act, hero, stack, env, handy):
    ranks = {"A":14, "K":13, "Q":12, "J":11, "T":10, "9":9, "8":8, "7":7, "6":6, "5":5, "4":4, "3":3, "2":2}
    r1, r2 = ranks[v1], ranks[v2]
    if r1 < r2: v1, v2 = v2, v1
    hand_key = f"{v1}{v2}"
    is_s = (suit == "s")
    
    # GTO 프리미엄 (절대 폴드 불가 영역)
    premiums = ["AA", "KK", "QQ", "JJ", "AK"]
    
    env_adj = {"Online (Standard)": 0, "Live Pub (Loose)": -2, "Tournament (ICM)": 1}[env]
    style_adj = {"Very Tight": 4, "Tight": 2, "Standard": 0, "Loose": -2, "Very Loose": -4}[hero]
    total_w = env_adj + style_adj

    if act == "Facing Raise":
        if hand_key in premiums:
            return "🔥 3-BET / CALL", "GTO: 프리미엄 핸드입니다. 폴드는 금지입니다."
        if r1 >= (11 + (total_w//2)) and is_s:
            return "🟢 CALL", "포스트플랍 운영이 가능한 수딧 핸드입니다."
        return "🔵 FOLD", "에퀴티가 낮아 폴드를 권장합니다."

    if act == "Unopened (RFI)":
        if hand_key in premiums: return "🔴 RAISE", "정석적인 GTO 오픈 구간입니다."
        p_base = {"UTG": 13, "MP": 12, "CO": 11, "BTN": 10, "SB": 10}.get(pos, 11)
        if (v1 == v2 and r1 >= (7 + total_w//2)) or (is_s and r1 >= (p_base + total_w//2)):
            return "🟠 OPEN", f"현재 조건에 최적화된 오픈 핸드입니다."

    return "🔵 FOLD", "수학적으로 기대값이 부족합니다."

# --- 6. 결과 출력 ---
st.divider()
res, why = get_gto_logic(pos, v1, v2, suit, action, hero_style, stack, env, handy)
if "RAISE" in res or "3-BET" in res or "ALL-IN" in res: st.error(f"## {res}")
elif "OPEN" in res or "CALL" in res: st.warning(f"## {res}")
else: st.info(f"## {res}")
st.write(f"📊 **Strategy:** {env} | {hero_style} | {handy}인")
st.write(f"💡 **Guide:** {why}")

# --- 7. 하단 차트 데이터 (복구 완료) ---
st.markdown("---")
st.markdown("### 📊 RFI Position Range Detail")
col1, col2 = st.columns(2)
stats = {"UTG":"14-15%", "UTG+1":"16-17%", "MP":"18-20%", "LJ":"20-22%", "HJ":"23-25%", "CO":"28-32%", "BTN":"45-55%", "SB":"40-45%"}
p_keys = list(stats.keys())
with col1:
    for k in p_keys[:4]:
        st.markdown(f'<div class="card-detail"><span class="pos-title">{k} ({stats[k]})</span><br><small>GTO Standard Open</small></div>', unsafe_allow_html=True)
with col2:
    for k in p_keys[4:]:
        st.markdown(f'<div class="card-detail"><span class="pos-title">{k} ({stats[k]})</span><br><small>GTO Standard Open</small></div>', unsafe_allow_html=True)

st.markdown("### 🚀 Short Stack Push Range (10-20BB)")
st.table(pd.DataFrame({"Position": ["UTG", "HJ", "CO", "BTN", "SB"], "Range": ["22+, A2s+, A7o+, KTs+", "22+, A2s+, A5o+, K9s+", "22+, Any Suited Ax, A2o+", "Any Ax, Any Suited Kx", "Any Ax, K2s+, Q5s+"]}))
