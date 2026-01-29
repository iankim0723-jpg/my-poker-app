import streamlit as st
import pandas as pd

# 1. 앱 설정
st.set_page_config(page_title="JM HOLDEM LEGEND 03 V1", page_icon="🃏", layout="centered")

# CSS: 모바일 최적화 및 디자인
st.markdown("""
    <style>
    div.stButton > button { width: 100%; height: 45px; font-weight: bold; border-radius: 8px; }
    .stSelectbox { margin-bottom: 5px; }
    .quote-box { 
        background-color: #1e1e1e; 
        color: #ff4b4b; 
        padding: 15px; 
        border-radius: 10px; 
        border: 2px solid #ff4b4b;
        text-align: center;
        font-weight: bold;
        font-size: 16px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 메인 상단 CBJ 명언 ---
st.markdown('<div class="quote-box">"한번 우승했다고 우쭐대지마라 그게 나락으로 가는 지름길이다"<br><small style="color: #ccc;">- 더홀릭 우승 경험자 CBJ -</small></div>', unsafe_allow_html=True)

st.title("🛡️ JM HOLDEM LEGEND 03 V1")

# --- 2. 사이드바 (플레이어 숫자 및 환경 설정) ---
with st.sidebar:
    st.header("⚙️ Game Setup")
    env = st.selectbox("Environment", ["Online", "Live Pub", "Tournament"])
    
    st.markdown("---")
    # 플레이어 숫자(Handy) 추가
    h_in = st.number_input("Handy (Player Count)", 2, 9, 6)
    handy = st.slider("Adjust Handy", 2, 9, int(h_in))
    
    st.markdown("---")
    st.header("👤 My Playing Style")
    hero_style = st.select_slider(
        "Select My Range Tightness",
        options=["Very Tight", "Tight", "Standard", "Loose", "Very Loose"],
        value="Standard"
    )
    
    st.markdown("---")
    s_in = st.number_input("Stack BB", 1, 1000, 100)
    stack = st.select_slider("Adjust BB", options=list(range(10, 1001, 10)), value=int(s_in) if s_in <= 1000 else 100)

# --- 3. 메인 화면: 상황 및 포지션 ---
st.markdown("### 1. Situation & Position")
pos_list = ["UTG", "UTG+1", "MP", "LJ", "HJ", "CO", "BTN", "SB", "BB"]
pos = st.selectbox("Select Position (Scroll/Type)", pos_list, index=6)
action = st.radio("Opponent Action", ["Unopened (RFI)", "Facing Raise", "Facing All-in"], horizontal=True)

st.markdown("---")

# --- 4. 카드 선택 ---
st.markdown("### 2. Select My Hand")
cards = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]

c1_col, c2_col = st.columns(2)
with c1_col:
    v1 = st.selectbox("Card 1", cards, key="v1")
with c2_col:
    v2 = st.selectbox("Card 2", cards, index=1, key="v2")

suit = st.radio("Suit", ["s", "o"], horizontal=True)

# --- 5. 레인지 조절 엔진 (Handy 반영) ---
def get_adjusted_strategy(pos, v1, v2, suit, act, hero, stack, handy):
    ranks = {"A":14, "K":13, "Q":12, "J":11, "T":10, "9":9, "8":8, "7":7, "6":6, "5":5, "4":4, "3":3, "2":2}
    r1, r2 = ranks[v1], ranks[v2]
    if r1 < r2: v1, v2 = v2, v1
    hand = f"{v1}{v2}{suit}"
    
    style_weights = {"Very Tight": 2, "Tight": 1, "Standard": 0, "Loose": -1, "Very Loose": -2}
    w = style_weights[hero]

    # 플레이어 숫자(Handy)가 적을수록(숏핸디) 레인지 확장 보정
    handy_adj = 0 if handy >= 6 else -1

    if stack <= 15 and act == "Unopened (RFI)":
        if r1 >= (13 + w + handy_adj) or (v1 == v2 and r1 >= (5 + w)):
            return "🔴 ALL-IN (Push)", f"현재 {handy}인 테이블 및 나의 {hero} 성향에 맞춘 푸쉬 범위입니다."

    if act == "Unopened (RFI)":
        base_threshold = {"UTG": 13, "MP": 12, "CO": 11, "BTN": 10, "SB": 10}.get(pos, 12)
        final_threshold = base_threshold + w + handy_adj

        if hand[:2] in ["AA", "KK", "QQ", "JJ", "AK"]:
            return "🔴 RAISE", "프리미엄 핸드: 무조건 레이즈.", "N/A"
            
        if r1 >= final_threshold:
            return "🟠 OPEN", f"{handy}인 테이블 기준, 나의 {hero} 스타일에 최적화된 오픈 범위입니다.", "N/A"

    return "🔵 FOLD", "현재 설정 기준으로는 폴드를 추천합니다.", "N/A"

# --- 6. 결과 출력 ---
st.divider()
res, why, prob = get_adjusted_strategy(pos, v1, v2, suit, action, hero_style, stack, handy)

if "RAISE" in res or "ALL-IN" in res or "OPEN" in res:
    st.error(f"## Action: {res}")
else:
    st.info(f"## Action: {res}")

st.write(f"👤 **스타일:** {hero_style} | 👥 **Handy:** {handy}인 | 💡 **가이드:** {why}")
