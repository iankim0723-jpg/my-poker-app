import streamlit as st

# 1. 앱 설정 (최상단 고정)
st.set_page_config(page_title="JM HOLDEM LEGEND 03 V1", page_icon="🃏", layout="centered")

# CSS: 모바일 7열 강제 배열 및 UI 최적화
st.markdown("""
    <style>
    [data-testid="column"] {
        padding: 0px 0.5px !important;
        flex: 1 1 0% !important;
        min-width: 0px !important;
    }
    div.stButton > button {
        width: 100% !important;
        height: 40px !important;
        font-size: 13px !important;
        padding: 0px !important;
        border-radius: 4px !important;
        border: 1px solid #ddd !important;
    }
    .stNumberInput { margin-bottom: -15px; }
    </style>
""", unsafe_allow_html=True)

# --- 타이틀 ---
st.title("🃏 JM HOLDEM LEGEND 03 V1")
st.error("⚠️ Unauthorized Distribution Prohibited (배포금지)")

# --- 2. 사이드바 (하이브리드 입력) ---
with st.sidebar:
    st.header("⚙️ Game Setup")
    env = st.selectbox("Env", ["Online", "Live Pub", "Tournament"])
    
    st.markdown("---")
    h_in = st.number_input("Handy (Direct)", 2, 9, 6)
    handy = st.slider("Handy (Slider)", 2, 9, int(h_in))

    st.markdown("---")
    s_in = st.number_input("Stack BB (Direct)", 1, 1000, 100)
    s_opts = list(range(25, 1001, 25))
    def_s = int(s_in) if int(s_in) in s_opts else 100
    stack = st.select_slider("Stack BB (Slider)", options=s_opts, value=def_s)

# --- 3. 메인 화면 (상황 설정) ---
st.markdown("### 1. Situation")
pos = st.selectbox("My Position", ["UTG", "MP", "CO", "BTN", "SB", "BB"])
action = st.radio("Opponent Action", ["Unopened", "Raised"], horizontal=True)

st.markdown("---")

# --- 4. 카드 선택 (7x2 강제 배열) ---
st.markdown("### 2. Select Hand")
cards = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]

def card_picker(label):
    st.write(f"**{label}**")
    key = f"state_{label}"
    if key not in st.session_state:
        st.session_state[key] = "A"

    # 상단 숫자 직접 선택
    curr_idx = cards.index(st.session_state[key])
    sel = st.selectbox(f"Pick {label}", cards, index=curr_idx, key=f"sel_{label}")
    st.session_state[key] = sel

    # 7열 버튼 (첫 번째 줄)
    r1 = st.columns(7)
    for i, c in enumerate(cards[:7]):
        with r1[i]:
            if st.button(c, key=f"b1_{label}_{c}"):
                st.session_state[key] = c
                st.rerun()

    # 7열 버튼 (두 번째 줄)
    r2 = st.columns(7)
    for i, c in enumerate(cards[7:]):
        with r2[i]:
            if st.button(c, key=f"b2_{label}_{c}"):
                st.session_state[key] = c
                st.rerun()
    with r2[6]: st.write("") # 빈칸 채우기
                
    return st.session_state[key]

v1 = card_picker("Card 1")
v2 = card_picker("Card 2")
suit = st.radio("Suit", ["Suited(s)", "Off-suit(o)"], horizontal=True)

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
    return "🔵 FOLD", "Expectation is low."

# --- 6. 결과 출력 ---
st.divider()
res, why = get_logic(env, handy, stack, pos, v1, v2, suit, action)

if "🔴" in res: st.error(f"## {res}")
elif "🟠" in res: st.warning(f"## {res}")
elif "🟢" in res: st.success(f"## {res}")
else: st.info(f"## {res}")

st.caption(f"💡 {why}")

with st.expander("📝 Review"):
    rev = st.radio("Result", ["Win", "Loss"], horizontal=True)
    if st.button("Save"):
        st.success(f"Saved: {rev}")
