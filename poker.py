import streamlit as st

# 페이지 설정
st.set_page_config(page_title="Ultimate Poker Solver & Review", page_icon="💎", layout="centered")

st.title("💎 Ultimate Poker Solver & Review")
st.caption("전략 가이드부터 게임 복기까지 한 번에")

# --- 1. 상황 설정 (Sidebar) ---
with st.sidebar:
    st.header("🎮 Table Settings")
    env = st.selectbox("Environment", ["Online (GTO)", "Live Pub (Loose)", "Tournament (Tight)"])
    handy = st.slider("Number of Players (Handy)", 2, 9, 6)
    stack = st.select_slider("Stack Size (BB)", options=[25, 50, 75, 100], value=50)
    street = st.selectbox("Current Street", ["Pre-flop", "Flop", "Turn", "River"])
    pos = st.selectbox("My Position", ["UTG", "MP", "CO", "BTN", "SB", "BB"])
    action = st.radio("Opponent Action", ["Unopened", "Facing a Raise"])

# --- 2. 카드 선택 ---
st.subheader("🎴 Card Selection")
card_icons = {"A":"🂡 A", "K":"🂮 K", "Q":"🂭 Q", "J":"🂫 J", "T":"🂪 10", "9":"9", "8":"8", "7":"7", "6":"6", "5":"5", "4":"4", "3":"3", "2":"2"}

col1, col2, col3 = st.columns(3)
with col1: v1 = st.selectbox("My Card 1", list(card_icons.keys()), format_func=lambda x: card_icons[x])
with col2: v2 = st.selectbox("My Card 2", list(card_icons.keys()), format_func=lambda x: card_icons[x])
with col3: suit = st.radio("My Suit", ["Suited(s)", "Off-suit(o)"], horizontal=True)

# 플랍 보드 카드
board = []
if street != "Pre-flop":
    st.markdown("---")
    st.subheader("🖼️ Board Cards")
    b_cols = st.columns(3)
    b1 = b_cols[0].selectbox("Board 1", list(card_icons.keys()), key="b1")
    b2 = b_cols[1].selectbox("Board 2", list(card_icons.keys()), key="b2")
    b3 = b_cols[2].selectbox("Board 3", list(card_icons.keys()), key="b3")
    board = [b1, b2, b3]

# --- 3. 전략 로직 ---
def get_strategy(env, handy, stack, street, pos, v1, v2, suit, act, board):
    ranks = {"A":14, "K":13, "Q":12, "J":11, "T":10, "9":9, "8":8, "7":7, "6":6, "5":5, "4":4, "3":3, "2":2}
    r1, r2 = ranks[v1], ranks[v2]
    hand = f"{v1}{v2}" + ("s" if suit == "Suited(s)" else "")

    if street == "Pre-flop":
        if stack <= 25 and (r1 >= 12 or v1 == v2): return "🔴 ALL-IN", "숏스택에서는 선택의 여지가 적습니다. 강력하게 미세요."
        if hand in ["AA", "KK", "QQ", "AKs", "AKo", "JJ"]: return "🔴 3-BET / RAISE", "프리미엄 핸드입니다. 밸류를 키우세요."
        if pos in ["BTN", "CO"] and act == "Unopened": return "🟠 OPEN RAISE", "포지션을 이용해 스틸하기 좋은 상황입니다."
        return "🔵 FOLD", "수학적으로 폴드가 정석입니다."
    
    else: # Flop 이후 간단 로직
        if v1 in board or v2 in board:
            return "🟢 BET / CALL (Pair Made)", "보드와 카드가 맞았습니다. 상대의 반응을 살피며 진행하세요."
        return "🔵 CHECK / FOLD", "보드와 맞지 않았습니다. 무리한 블러핑은 자제하세요."

# 결과 출력
st.divider()
res_act, res_why = get_strategy(env, handy, stack, street, pos, v1, v2, suit, action, board)
st.subheader("🎯 Result")
st.error(f"## {res_act}") if "🔴" in res_act else st.warning(f"## {res_act}") if "🟠" in res_act else st.success(f"## {res_act}") if "🟢" in res_act else st.info(f"## {res_act}")
st.info(f"**💡 전략 근거:** {res_why}")

# --- 4. 게임 리뷰 (복기) 섹션 ---
st.markdown("---")
st.header("📝 Game Review")
with st.expander("방금 판의 결과를 기록하세요"):
    result = st.radio("Result", ["Win 🏆", "Loss 💀"], horizontal=True)
    pot_size = st.number_input("Pot Size (BB)", min_value=0)
    note = st.text_area("Review Note", placeholder="예: 상대의 리레이즈에 너무 쉽게 폴드함, 플랍 셋 메이드로 크게 먹음 등")
    if st.button("Save Record"):
        st.success(f"기록 완료! [{result}] {pot_size}BB / 메모: {note}")
        # 실제 데이터 저장은 DB가 필요하지만, 화면상에서 확인 가능하도록 구성
