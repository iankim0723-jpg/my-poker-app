import streamlit as st

# 1. 페이지 설정
st.set_page_config(page_title="Ultimate Poker Solver", page_icon="🃏", layout="centered")

# --- 타이틀 ---
st.title("🃏 Pro Poker Solver")
st.caption("Customized Strategy & Game Review")

# --- 2. 설정 (Sidebar) ---
with st.sidebar:
    st.header("⚙️ Game Settings")
    env = st.selectbox("Environment", ["Online (GTO)", "Live Pub (Loose)", "Tournament (Tight)"])
    handy = st.slider("Number of Players (Handy)", 2, 9, 6)
    stack = st.select_slider("Stack Size (BB)", options=[25, 50, 75, 100], value=50)
    street = st.selectbox("Street", ["Pre-flop", "Flop", "Turn", "River"])
    pos = st.selectbox("Position", ["UTG", "MP", "CO", "BTN", "SB", "BB"])
    action = st.radio("Opponent Action", ["Unopened", "Facing a Raise"])

# --- 3. 카드 선택 ---
st.subheader("🎴 Card Selection")
card_icons = {"A":"🂡 A", "K":"🂮 K", "Q":"🂭 Q", "J":"🂫 J", "T":"🂪 10", "9":"9", "8":"8", "7":"7", "6":"6", "5":"5", "4":"4", "3":"3", "2":"2"}

col1, col2, col3 = st.columns(3)
with col1:
    v1 = st.selectbox("Card 1", list(card_icons.keys()), format_func=lambda x: card_icons[x])
with col2:
    v2 = st.selectbox("Card 2", list(card_icons.keys()), format_func=lambda x: card_icons[x])
with col3:
    suit = st.radio("Suit", ["Suited(s)", "Off-suit(o)"], horizontal=True)

# --- 4. 전략 로직 ---
def get_strategy(env, handy, stack, street, pos, v1, v2, suit, act):
    ranks = {"A":14, "K":13, "Q":12, "J":11, "T":10, "9":9, "8":8, "7":7, "6":6, "5":5, "4":4, "3":3, "2":2}
    r1, r2 = ranks[v1], ranks[v2]
    if r1 < r2: v1, v2 = v2, v1
    hand = f"{v1}{v2}" + ("s" if suit == "Suited(s)" and v1 != v2 else "")

    if stack <= 25:
        if r1 >= 13 or (v1 == v2 and r1 >= 8): 
            return "🔴 ALL-IN / JAM", "숏스택 전략: 현재 인원수와 스택 대비 올인이 가장 수익성 높습니다."
        return "🔵 FOLD", "숏스택 전략: 리스크를 최소화하고 더 강한 핸드를 기다리세요."

    if hand in ["AA", "KK", "QQ", "AKs", "AKo", "JJ"]:
        return "🔴 3-BET / RAISE", "가장 강력한 프리미엄 핸드입니다. 공격적으로 밸류를 쌓으세요."
    
    if pos in ["BTN", "CO"] and (act == "Unopened" or handy <= 4):
        return "🟠 OPEN RAISE", f"{handy}인 테이블 포지션 이점을 활용해 블라인드를 스틸하세요."

    if env == "Live Pub (Loose)" and "s" in hand:
        return "🟢 CALL", "라이브 펍 환경: 멀티웨이 가능성이 높으므로 수딧 핸드로 플랍을 봅니다."

    return "🔵 FOLD", "수학적으로 폴드하는 것이 장기적인 수익에 도움이 됩니다."

# --- 5. 결과 출력 ---
st.divider()
res_act, res_why = get_strategy(env, handy, stack, street, pos, v1, v2, suit, action)

st.markdown("### 🎯 Recommendation")
if "🔴" in res_act:
    st.error(f"## {res_act}")
elif "🟠" in res_act:
    st.warning(f"## {res_act}")
elif "🟢" in res_act:
    st.success(f"## {res_act}")
else:
    st.info(f"## {res_act}")

st.info(f"**💡 전략 근거:** {res_why}")

# --- 6. 게임 리뷰 ---
st.markdown("---")
st.header("📝 Game Review")
with st.expander("방금 판 기록하기"):
    rev_res = st.radio("결과", ["승리 🏆", "패배 💀"], horizontal=True)
    rev_note = st.text_area("복기 메모", placeholder="예: 버튼에서 레이즈 스틸 성공")
    if st.button("기록 저장"):
        st.success(f"저장되었습니다: {rev_res} / {rev_note}")
