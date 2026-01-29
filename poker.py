import streamlit as st

# 1. 앱 설정 (최상단 필수)
st.set_page_config(page_title="JM HOLDEM LEGEND 03 V1", page_icon="🃏", layout="centered")

# CSS: 모바일 7열 강제 배열 및 프로 스타일 디자인
st.markdown("""
    <style>
    [data-testid="column"] {
        padding: 0px 0.5px !important;
        flex: 1 1 0% !important;
        min-width: 0px !important;
    }
    div.stButton > button {
        width: 100% !important;
        height: 42px !important;
        font-size: 13px !important;
        font-weight: bold !important;
        padding: 0px !important;
        border-radius: 4px !important;
        border: 1px solid #ddd !important;
    }
    .stNumberInput { margin-bottom: -15px; }
    .stSelectbox { margin-bottom: -10px; }
    </style>
""", unsafe_allow_html=True)

st.title("🃏 JM HOLDEM LEGEND 03 V1")
st.error("⚠️ PRO DATA INTEGRATED (배포금지)")

# --- 2. 사이드바 (설정 하이브리드) ---
with st.sidebar:
    st.header("⚙️ Game Setup")
    env = st.selectbox("Field Type", ["Online (Standard)", "Live Pub (Loose)", "Tournament (Tight)"])
    
    st.markdown("---")
    pos_list = ["UTG", "UTG+1", "MP", "LJ", "HJ", "CO", "BTN", "SB", "BB"]
    pos = st.selectbox("My Position", pos_list, index=6)

    st.markdown("---")
    s_in = st.number_input("Stack BB (Direct)", 1, 1000, 100)
    s_opts = list(range(10, 1001, 10))
    def_s = int(s_in) if int(s_in) in s_opts else 100
    stack = st.select_slider("Stack BB (Slider)", options=s_opts, value=def_s)

# --- 3. 메인 화면 ---
st.markdown("### 1. Situation")
action = st.radio("Opponent Action", ["Unopened (RFI)", "Facing Raise", "Facing All-in"], horizontal=True)

st.markdown("---")

# --- 4. 카드 선택 (7x2 강제 배열) ---
st.markdown("### 2. My Hand")
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
    with r2[6]: st.write("")
    return st.session_state[key]

v1 = card_picker("Card 1")
v2 = card_picker("Card 2")
suit = st.radio("Suit", ["Suited(s)", "Off-suit(o)"], horizontal=True)

# --- 5. 전략 엔진 ---
def get_pro_logic(env, pos, stack, v1, v2, suit, act):
    ranks = {"A":14, "K":13, "Q":12, "J":11, "T":10, "9":9, "8":8, "7":7, "6":6, "5":5, "4":4, "3":3, "2":2}
    r1, r2 = ranks[v1], ranks[v2]
    if r1 < r2: v1, v2 = v2, v1
    hand = f"{v1}{v2}" + ("s" if suit == "Suited(s)" and v1 != v2 else "o")

    if stack <= 20 and act == "Unopened (RFI)":
        if r1 >= 14 or (v1 == v2 and r1 >= 6) or (suit == "Suited(s)" and r1 >= 11):
            return "🔴 PUSH (ALL-IN)", f"{stack}BB 전략: 핸드 보호 및 에퀴티 실현을 위해 올인하세요."
        return "🔵 FOLD", "숏스택에서는 칩을 아껴야 합니다."

    if act == "Unopened (RFI)":
        if hand[:2] in ["AA", "KK", "QQ", "JJ", "AK", "AQ"]:
            return "🔴 RAISE (Standard)", "강력한 프리미엄입니다. 밸류를 키우세요."
        
        tight_pos = ["UTG", "UTG+1", "MP", "LJ"]
        if pos in tight_pos:
            if r1 >= 13 and suit == "Suited(s)": return "Open Raise", f"{pos} 포지션: 타이트한 운영이 필수입니다."
        else:
            if r1 >= 10 or suit == "Suited(s)": return "Open Raise", f"{pos} 포지션: 스틸 범위를 넓히세요."

    if env == "Live Pub (Loose)":
        if suit == "Suited(s)" and r1 >= 10: return "🟢 CALL", "라이브 펍: 멀티웨이 배당을 위해 플랍을 봅니다."

    return "🔵 FOLD", "수학적 기대값이 낮아 폴드를 권장합니다."

# --- 6. 결과 출력 ---
st.divider()
res, why = get_pro_logic(env, pos, stack, v1, v2, suit, action)

if "🔴" in res: st.error(f"## {res}")
elif "Standard" in res or "Open" in res: st.warning(f"## {res}")
elif "🟢" in res: st.success(f"## {res}")
else: st.info(f"## {res}")

st.info(f"**💡 ANALYSIS:** {why}")
