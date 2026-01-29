import streamlit as st

# 1. 앱 설정 (최상단 필수)
st.set_page_config(page_title="JM HOLDEM LEGEND 03 V1", page_icon="🃏", layout="centered")

# CSS: 모바일 7열 강제 배열 및 가독성 최적화
st.markdown("""
    <style>
    [data-testid="column"] { padding: 0px 0.5px !important; flex: 1 1 0% !important; min-width: 0px !important; }
    div.stButton > button { width: 100% !important; height: 42px !important; font-size: 14px !important; font-weight: bold !important; padding: 0px !important; border-radius: 4px !important; border: 1px solid #ddd !important; }
    .stSelectbox { margin-bottom: -10px; }
    </style>
""", unsafe_allow_html=True)

st.title("🃏 JM HOLDEM LEGEND 03 V1")
st.error("⚠️ PRO CHART DATA LOADED (배포금지)")

# --- 2. 사이드바 (프로 차트 기반 설정) ---
with st.sidebar:
    st.header("⚙️ Game Setup")
    env = st.selectbox("Field", ["Online", "Live Pub", "Tournament"])
    
    st.markdown("---")
    # 이미지 3번: 세분화된 9인 포지션 반영
    pos_list = ["UTG", "UTG+1", "MP", "LJ", "HJ", "CO", "BTN", "SB"]
    pos = st.selectbox("My Position", pos_list, index=6) # 기본 BTN

    st.markdown("---")
    s_in = st.number_input("Stack BB (Direct)", 1, 1000, 100)
    stack = st.select_slider("Stack BB (Slider)", options=list(range(10, 1001, 10)), value=int(s_in) if s_in <= 1000 else 100)

# --- 3. 메인 화면 (상황 설정) ---
st.markdown("### 1. Situation")
action = st.radio("Opponent Action", ["Unopened (RFI)", "Facing Raise", "Facing All-in"], horizontal=True)

st.markdown("---")

# --- 4. 카드 선택 (7x2 강제 배열) ---
st.markdown("### 2. Select Hand")
cards = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]

def card_picker(label):
    st.write(f"**{label}**")
    key = f"state_{label}"
    if key not in st.session_state: st.session_state[key] = "A"
    
    idx = cards.index(st.session_state[key])
    sel = st.selectbox(f"Select {label}", cards, index=idx, key=f"sel_{label}")
    st.session_state[key] = sel

    r1 = st.columns(7)
    for i, c in enumerate(cards[:7]):
        with r1[i]:
            if st.button(c, key=f"b1_{label}_{c}"):
                st.session_state[key] = c
                st.rerun()
    r2 = st.columns(7)
    for i, c in enumerate(cards[7:]):
        with r2[i]:
            if st.button(c, key=f"b2_{label}_{c}"):
                st.session_state[key] = c
                st.rerun()
    return st.session_state[key]

v1 = card_picker("Card 1")
v2 = card_picker("Card 2")
suit = st.radio("Suit", ["s", "o"], horizontal=True)

# --- 5. 프로 차트 데이터 로직 (이미지 3번 기반) ---
def get_pro_logic(pos, v1, v2, suit, act):
    ranks = {"A":14, "K":13, "Q":12, "J":11, "T":10, "9":9, "8":8, "7":7, "6":6, "5":5, "4":4, "3":3, "2":2}
    r1, r2 = ranks[v1], ranks[v2]
    if r1 < r2: v1, v2 = v2, v1
    hand = f"{v1}{v2}{suit}"

    # 프리미엄 핸드 공통
    if hand[:2] in ["AA", "KK", "QQ", "JJ", "AK"]:
        return "🔴 RAISE (Standard)", "최상위 프리미엄 핸드입니다. 밸류를 키우세요."

    # RFI 오픈 차트 (이미지 3번 반영)
    if act == "Unopened (RFI)":
        if pos == "UTG":
            if r1 >= 14 and suit == "s": return "🟠 OPEN", "UTG: 가장 타이트한 범위(14-15%)로 오픈하세요."
        elif pos == "HJ":
            if r1 >= 10: return "🟠 OPEN", "HJ: 스틸이 시작되는 지점입니다 (23-25%)."
        elif pos == "BTN":
            if r1 >= 10 or suit == "s": return "🟠 OPEN", "BTN: 가장 넓은 범위(45-50%)로 압박하세요."
        elif pos == "CO":
            if r1 >= 11: return "🟠 OPEN", "CO: 스틸의 핵심 포지션입니다 (28-32%)."

    return "🔵 FOLD", "수학적으로 기대값이 낮아 폴드를 권장합니다."

# --- 6. 결과 출력 ---
st.divider()
res, why = get_pro_logic(pos, v1, v2, suit, action)

if "🔴" in res: st.error(f"## {res}")
elif "🟠" in res: st.warning(f"## {res}")
else: st.info(f"## {res}")

st.info(f"**💡 CHART ADVICE:** {why}")
