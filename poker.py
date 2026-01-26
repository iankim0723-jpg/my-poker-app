import streamlit as st

# 1. 앱 설정 (최상단 필수)
st.set_page_config(page_title="JM HOLDEM LEGEND 03 V1", page_icon="🃏", layout="centered")

# CSS: 모바일 버튼 크기 및 간격 최적화
st.markdown("""
    <style>
    div.stButton > button {
        width: 100%;
        height: 42px;
        font-weight: bold;
        font-size: 15px;
        border-radius: 5px;
        padding: 0px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 타이틀 ---
st.title("🃏 JM HOLDEM LEGEND 03 V1")
st.error("⚠️ Unauthorized Distribution Prohibited (배포금지)")

# --- 2. 사이드바 (슬라이더 + 숫자입력 하이브리드) ---
with st.sidebar:
    st.header("⚙️ Game Setup")
    env = st.selectbox("Environment", ["Online", "Live Pub", "Tournament"])
    
    st.markdown("---")
    # Handy 설정
    h_val = st.number_input("Handy (Direct)", min_value=2, max_value=9, value=6)
    handy = st.slider("Handy (Slider)", 2, 9, int(h_val))

    st.markdown("---")
    # Stack 설정 (50~500, 25단위)
    s_val = st.number_input("Stack BB (Direct)", min_value=1, max_value=1000, value=100)
    stack_opts = list(range(25, 1001, 25))
    # 입력값이 옵션에 없을 경우 가장 가까운 값 선택
    default_s = int(s_val) if int(s_val) in stack_opts else 100
    stack = st.select_slider("Stack BB (Slider)", options=stack_opts, value=default_s)

# --- 3. 메인 화면 (상황 설정) ---
st.markdown("### 1. Situation")
pos = st.selectbox("My Position", ["UTG", "MP", "CO", "BTN", "SB", "BB"])
action = st.radio("Opponent Action", ["Unopened", "Raised"], horizontal=True)

st.markdown("---")

# --- 4. 카드 선택 (숫자 입력 + 7x2 버튼) ---
st.markdown("### 2. Select Hand")
cards = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]

def card_picker(label):
    st.write(f"**{label}**")
    key_name = f"card_state_{label}"
    
    if key_name not in st.session_state:
        st.session_state[key_name] = "A"

    # 상단 숫자 선택창 (입력/선택 겸용)
    idx = cards.index(st.session_state[key_name])
    sel_card = st.selectbox(f"Choose {label}", cards, index=idx, key=f"sel_{label}")
    st.session_state[key_name] = sel_card

    # 7장씩 두 줄 버튼
    r1_cols = st.columns(7)
    for i, c in enumerate(cards[:7]):
        with r1_cols[i]:
            if st.button(c, key=f"btn1_{label}_{c}"):
                st.session_state[key_name] = c
                st.rerun()

    r2_cols = st.columns(7)
    for i, c in enumerate(cards[7:]):
        with r2_cols[i]:
            if st.button(c, key=f"btn2_{label}_{c}"):
                st.session_state[key_name] = c
                st.rerun()
                
    return st.session_state[key_name]

v1 = card_picker("Card 1")
v2 = card_picker("Card 2")
suit = st.radio("Suit Type", ["Suited(s)", "Off-suit(o)"], horizontal=True)

# --- 5. 전략 로직 ---
def get_logic(env, handy, stack, pos, v1, v2, suit, act):
    ranks = {"A":14, "K":13, "Q":12, "J":11, "T":10, "9":9, "8":8, "7":7, "6":6, "5":5, "4":4, "3":3, "2":2}
    r1, r2 = ranks[v1], ranks[v2]
    if r1 < r2: v1, v2 = v2, v1
    hand = f"{v1}{v2}" + ("s" if suit == "Suited(s)" and v1 != v2 else "")

    if hand in ["AA", "KK", "QQ", "AKs", "AKo"]:
        return "🔴 RAISE / 3-BET", "Premium hand. Build the pot."
    if stack >= 200 and v1 == v2 and r1 <= 10:
        return "🟢 CALL (SET MINE)", "Deep stack efficiency for set mining."
    if pos in ["BTN", "CO"] and act == "Unopened":
        return "🟠 OPEN RAISE", "Positional advantage for stealing."
    return "🔵 FOLD", "Mathematical expectation is low."

# --- 6. 결과 출력 ---
st.divider()
res_act, res_why = get_logic(env, handy, stack, pos, v1, v2, suit, action)

if "🔴" in res_act: st.error(f"## {res_act}")
elif "🟠" in res_act: st.warning(f"## {res_act}")
elif "🟢" in res_act: st.success(f"## {res_act}")
else: st.info(f"## {res_act}")

st.caption(f"💡 {res_why} (Stack: {stack}BB / Handy: {handy})")

# --- 7. 복기 ---
with st.expander("📝 Review"):
    rev = st.radio("Result", ["Win", "Loss"], horizontal=True)
    if st.button("Save"):
        st.success(f"Saved: {rev}")
