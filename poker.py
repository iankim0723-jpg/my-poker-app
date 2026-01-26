import streamlit as st

# 1. 앱 설정 (최상단 필수)
st.set_page_config(page_title="JM HOLDEM LEGEND 03 V1", page_icon="🃏", layout="centered")

# CSS: 모바일 7열 배열 강제 및 UI 최적화
st.markdown("""
    <style>
    /* 7열 배치를 위해 컬럼 간격 및 패딩 최소화 */
    [data-testid="column"] {
        padding: 0px 0.5px !important;
        flex: 1 1 0% !important;
        min-width: 0px !important;
    }
    div.stButton > button {
        width: 100% !important;
        height: 42px !important;
        font-size: 14px !important;
        padding: 0px !important;
        border-radius: 4px !important;
        border: 1px solid #ddd !important;
    }
    /* 숫자 입력창 아래 여백 줄임 */
    .stNumberInput { margin-bottom: -10px; }
    </style>
""", unsafe_allow_html=True)

# --- 타이틀 ---
st.title("🃏 JM HOLDEM LEGEND 03 V1")
st.error("⚠️ Unauthorized Distribution Prohibited (배포금지)")

# --- 2. 사이드바 (하이브리드 입력) ---
with st.sidebar:
    st.header("⚙️ Game Setup")
    env = st.selectbox("Environment", ["Online", "Live Pub", "Tournament"])
    
    st.markdown("---")
    # Handy 하이브리드
    h_input = st.number_input("Handy (Direct)", min_value=2, max_value=9, value=6)
    handy = st.slider("Handy (Slider)", 2, 9, int(h_input))

    st.markdown("---")
    # Stack 하이브리드 (25~1000)
    s_input = st.number_input("Stack BB (Direct)", min_value=1, max_value=1000, value=100)
    stack_opts = list(range(25, 1001, 25))
    def_s = int(s_input) if int(s_input) in stack_opts else 100
    stack = st.select_slider("Stack BB (Slider)", options=stack_opts, value=def_s)

# --- 3. 메인 화면 (상황 설정) ---
st.markdown("### 1. Situation")
pos = st.selectbox("My Position", ["UTG", "MP", "CO", "BTN", "SB", "BB"])
action = st.radio("Opponent Action", ["Unopened", "Raised"], horizontal=True)

st.markdown("---")

# --- 4. 카드 선택 (7x2 강제 버튼 배열) ---
st.markdown("### 2. Select Hand")
cards = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]

def card_picker(label):
    st.write(f"**{label}**")
    key_name = f"state_{label}"
    if key_name not in st.session_state:
        st.session_state[key_name] = "A"

    # 상단 숫자 직접 선택창
    idx = cards.index(st.session_state[key_name])
    sel_card = st.selectbox(f"Select {label}", cards, index=idx, key=f"sel_{label}")
    st.session_state[key_name] = sel_card

    # 첫 번째 줄 (A, K, Q, J, T, 9, 8)
    r1 = st.columns(7)
    for i, c in enumerate(cards[:7]):
        with r1[i]:
            if st.button(c, key=f"b1_{label}_{c}"):
                st.session_state[key_name] = c
                st.rerun()

    # 두 번째 줄 (7, 6, 5, 4, 3, 2) + 빈칸
    r2 = st.columns(7)
    for i, c in enumerate(cards[7:]):
        with r2[i]:
            if st.button(c, key=f"b2_{label}_{c}"):
                st.session_state[key_name] = c
                st.rerun()
    with r2[6]: st.write("") # 7열 맞춤용 빈칸
                
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

st.caption(f"💡 {res_why}")

# --- 7. 심플 복기 ---
with st.expander("📝 Review"):
    rev = st.radio("Result",
