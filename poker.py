import streamlit as st

# 1. 페이지 설정
st.set_page_config(page_title="JM HOLDEM LEGEND 03 V1", page_icon="🃏", layout="centered")

# 커스텀 CSS: 버튼을 카드처럼 보이게 디자인
st.markdown("""
    <style>
    div.stButton > button {
        width: 100%;
        height: 50px;
        font-weight: bold;
        font-size: 18px;
        border-radius: 10px;
        margin-bottom: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 메인 타이틀 ---
st.title("🃏 JM HOLDEM LEGEND 03 V1")
st.error("⚠️ Unauthorized Distribution Prohibited (배포금지)")

# --- 2. 사이드바 (기본 설정) ---
with st.sidebar:
    st.header("⚙️ Settings")
    env = st.selectbox("Environment", ["Online", "Live Pub", "Tournament"])
    handy = st.slider("Handy", 2, 9, 6)
    stack_options = list(range(50, 501, 25))
    stack = st.select_slider("Stack (BB)", options=stack_options, value=100)

# --- 3. 메인 화면 (상황 설정) ---
st.markdown("### 1. Situation")
pos = st.selectbox("My Position", ["UTG", "MP", "CO", "BTN", "SB", "BB"])
action = st.radio("Opponent Action", ["Unopened", "Facing a Raise"], horizontal=True)

st.markdown("---")

# --- 4. 카드 선택 (버튼/타일 방식) ---
st.markdown("### 2. Select Cards")

def card_selector(label):
    st.write(f"**{label}**")
    cards = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]
    # 폰 화면에 맞게 4~5개씩 끊어서 배치
    cols = st.columns(7)
    selected = None
    
    # 세션 스테이트를 이용해 선택 상태 유지
    key_name = f"selected_{label}"
    if key_name not in st.session_state:
        st.session_state[key_name] = "A"

    for i, card in enumerate(cards):
        with cols[i % 7]:
            if st.button(card, key=f"{label}_{card}"):
                st.session_state[key_name] = card
    
    st.markdown(f"Selected {label}: **{st.session_state[key_name]}**")
    return st.session_state[key_name]

# 카드 1, 2 선택 타일
v1 = card_selector("Card 1")
v2 = card_selector("Card 2")

st.write("")
suit = st.radio("Suit Type", ["Suited(s)", "Off-suit(o)"], horizontal=True)

# --- 5. 전략 로직 ---
def get_poker_action(env, handy, stack, pos, v1, v2, suit, act):
    ranks = {"A":14, "K":13, "Q":12, "J":11, "T":10, "9":9, "8":8, "7":7, "6":6, "5":5, "4":4, "3":3, "2":2}
    r1, r2 = ranks[v1], ranks[v2]
    if r1 < r2: v1, v2 = v2, v1
    hand = f"{v1}{v2}" + ("s" if suit == "Suited(s)" and v1 != v2 else "")

    if hand in ["AA", "KK", "QQ", "AKs", "AKo"]:
        return "🔴 RAISE / 3-BET", "가장 강력한 프리미엄 핸드입니다."
    if stack >= 200 and v1 == v2 and r1 <= 10:
        return "🟢 CALL / SET MINE", "딥스택 셋마이닝 효율이 좋은 구간입니다."
    if pos in ["BTN", "CO"] and act == "Unopened":
        return "🟠 OPEN RAISE", "포지션 스틸을 적극적으로 고려하세요."
    return "🔵 FOLD", "수학적으로 폴드가 정석인 구간입니다."

# --- 6. 결과 출력 ---
st.divider()
res_act, res_why = get_poker_action(env, handy, stack, pos, v1, v2, suit, action)

st.subheader("🎯 Result")
if "🔴" in res_act: st.error(f"## {res_act}")
elif "🟠" in res_act: st.warning(f"## {res_act}")
elif "🟢" in res_act: st.success(f"## {res_act}")
else: st.info(f"## {res_act}")

st.info(f"💡 {res_why}")

# --- 7. 복기 ---
with st.expander("📝 Game Review"):
    rev = st.radio("Result", ["Win 🏆", "Loss 💀"], horizontal=True)
    if st.button("Save Record"):
        st.success(f"Saved: {rev}")
