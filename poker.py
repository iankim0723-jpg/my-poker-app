import streamlit as st

# 1. 앱 설정
st.set_page_config(page_title="JM HOLDEM LEGEND 03 V1", page_icon="🃏", layout="centered")

# 커스텀 CSS: 버튼 디자인 및 레이아웃 최적화
st.markdown("""
    <style>
    div.stButton > button {
        width: 100%;
        height: 45px;
        font-weight: bold;
        font-size: 16px;
        border-radius: 8px;
        margin-bottom: 2px;
        padding: 0px;
    }
    .stNumberInput { margin-bottom: -15px; }
    </style>
""", unsafe_allow_html=True)

# --- 메인 타이틀 ---
st.title("🃏 JM HOLDEM LEGEND 03 V1")
st.error("⚠️ Unauthorized Distribution Prohibited (배포금지)")

# --- 2. 사이드바 (설정: 슬라이더 + 숫자입력 병행) ---
with st.sidebar:
    st.header("⚙️ Game Setup")
    env = st.selectbox("Environment", ["Online", "Live Pub", "Tournament"])
    
    st.markdown("---")
    st.write("**Handy (Players)**")
    h_input = st.number_input("Direct Input (Handy)", min_value=2, max_value=9, value=6, step=1, label_visibility="collapsed")
    handy = st.slider("Slider (Handy)", 2, 9, int(h_input))

    st.markdown("---")
    st.write("**Stack (BB)**")
    s_input = st.number_input("Direct Input (BB)", min_value=1, max_value=1000, value=100, step=25, label_visibility="collapsed")
    # 50~500 범위 외의 숫자 입력 대응을 위해 범위를 넓게 설정
    stack_options = list(range(25, 1001, 25))
    initial_stack = int(s_input) if int(s_input) in stack_options else 100
    stack = st.select_slider("Slider (BB)", options=stack_options, value=initial_stack)

# --- 3. 메인 화면 (상황 설정) ---
st.markdown("### 1. Situation")
pos = st.selectbox("My Position", ["UTG", "MP", "CO", "BTN", "SB", "BB"])
action = st.radio("Opponent Action", ["Unopened", "Raised"], horizontal=True)

st.markdown("---")

# --- 4. 카드 선택 (7장씩 두 줄 버튼 + 숫자 선택창) ---
st.markdown("### 2. Select Hand")

cards = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]

def card_ui_selector(label):
    st.write(f"**{label}**")
    
    # 세션 상태 초기화
    key_name = f"st_card_{label}"
    if key_name not in st.session_state:
        st.session_state[key_name] = "A"

    # 직접 숫자 입력창 (상단)
    selected_from_input = st.selectbox(f"Select or Type {label}", cards, index=cards.index(st.session_state[key_name]), key=f"input_{label}")
    st.session_state[key_name] = selected_from_input

    # 7장씩 두 줄 버튼 배치
    row1 = cards[:7]
    row2 = cards[7:]
    
    c_row1 = st.columns(7)
    for i, c in enumerate(row1):
        with c_row1[i]:
            if st.button(c, key=f"btn_{label}_{c}"):
                st.session_state[key_name] = c
                st.rerun()

    c_row2 = st.columns(7)
    for i, c in enumerate(row2):
        with c_row2[i]:
            if st.button(c, key=f"btn_{label}_{c}"):
                st.session_state[key_name] = c
                st.rerun()
                
    return st.session_state[key_name]

v1 = card_ui_selector("Card 1")
v2 = card_ui_selector("Card 2")

st.write("")
suit = st.radio("Suit Type", ["Suited(s)", "Off-suit(o)"], horizontal=True)

# --- 5. 전략 로직 ---
def get_poker_action(env, handy, stack, pos, v1, v2, suit, act):
    ranks = {"A":14, "K":13, "Q":12, "J":11, "T":10, "9":9, "8":8, "7":7, "6":6, "5":5, "4":4, "3":3, "2":2}
    r1, r2 = ranks[v1], ranks[v2]
    if r1 < r2: v1, v2 = v2, v1
    hand = f"{v1}{v2}" + ("s" if suit == "Suited(s)" and v1 != v2 else "")

    if hand in ["AA", "KK", "QQ", "AKs", "AKo"]:
        return "🔴 RAISE / 3-BET", "프리미엄 핸드입니다. 강력하게 플레이하세요."
    if stack >= 200 and v1 == v2 and r1 <= 10:
        return "🟢 CALL (SET MINE)", "딥스택 상황, 셋마이닝 배당이 좋습니다."
    if pos in ["BTN", "CO"] and act == "Unopened":
        return "🟠 OPEN RAISE", "포지션 스틸 구간입니다."
    return "🔵 FOLD", "수학적 기대값이 낮습니다."

# --- 6. 결과 출력 ---
st.divider()
res_act, res_why = get_poker_action(env, handy, stack, pos, v1, v2, suit, action)

st.subheader("🎯 Result")
if "🔴" in res_act: st.error(f"## {res_act}")
elif "🟠" in res_act: st.warning(f"## {res_act}")
elif "🟢" in res_act: st.success(f"## {res_act}")
else: st.info(f"## {res_act}")

st.info(f"💡 {res_why} (Stack: {stack}BB / Handy: {
