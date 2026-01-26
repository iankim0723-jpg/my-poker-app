import streamlit as st

# 1. 페이지 설정
st.set_page_config(page_title="Poker Master Solver", page_icon="🃏", layout="centered")

# --- 앱 타이틀 ---
st.title("🃏 Poker Master Solver")
st.caption("Position moved to main screen for better mobile access")

# --- 2. 사이드바 (환경 및 스택 설정만 유지) ---
with st.sidebar:
    st.header("⚙️ Game Settings")
    env = st.selectbox("Environment", ["Online (GTO)", "Live Pub (Loose)", "Tournament (Tight)"])
    handy = st.slider("Handy (Players)", 2, 9, 6)
    
    st.markdown("---")
    stack_mode = st.radio("Stack Input Mode", ["Select BB", "Manual Input"])
    if stack_mode == "Select BB":
        stack = st.select_slider("Stack Size (BB)", options=[25, 50, 75, 100], value=50)
    else:
        my_chips = st.number_input("My Chips", value=100000)
        bb_amount = st.number_input("Big Blind Amount", value=2000)
        stack = my_chips / bb_amount if bb_amount > 0 else 50
        st.write(f"Calculated: {stack:.1f} BB")

# --- 3. 메인 화면 (포지션 + 카드 선택) ---
st.markdown("### 1. Situation")
# 포지션 선택을 메인 화면 상단으로 배치
pos = st.selectbox("My Position", ["UTG", "MP", "CO", "BTN", "SB", "BB"])
action = st.radio("Opponent Action", ["Unopened", "Facing a Raise"], horizontal=True)

st.markdown("---")
st.markdown("### 2. My Hand")
card_icons = {"A":"🂡 A", "K":"🂮 K", "Q":"🂭 Q", "J":"🂫 J", "T":"🂪 10", "9":"9", "8":"8", "7":"7", "6":"6", "5":"5", "4":"4", "3":"3", "2":"2"}

c1, c2, c3 = st.columns(3)
with c1:
    v1 = st.selectbox("Card 1", list(card_icons.keys()), format_func=lambda x: card_icons[x])
with c2:
    v2 = st.selectbox("Card 2", list(card_icons.keys()), format_func=lambda x: card_icons[x])
with c3:
    suit = st.radio("Suit", ["Suited(s)", "Off-suit(o)"], horizontal=True)

# --- 4. 전략 로직 ---
def get_poker_action(env, handy, stack, pos, v1, v2, suit, act):
    ranks = {"A":14, "K":13, "Q":12, "J":11, "T":10, "9":9, "8":8, "7":7, "6":6, "5":5, "4":4, "3":3, "2":2}
    r1, r2 = ranks[v1], ranks[v2]
    if r1 < r2: v1, v2 = v2, v1
    hand = f"{v1}{v2}" + ("s" if suit == "Suited(s)" and v1 != v2 else "")

    if stack <= 30:
        if r1 >= 13 or (v1 == v2 and r1 >= 7): return "🔴 ALL-IN", "숏스택 전략: 현재 상황에서 올인이 가장 수익적입니다."
        return "🔵 FOLD", "숏스택 전략: 핸드를 아끼세요."

    if hand in ["AA", "KK", "QQ", "AKs", "AKo", "JJ", "TT"]:
        return "🔴 RAISE / 3-BET", "강력한 프리미엄 핸드입니다."
    
    if pos in ["BTN", "CO"] and act == "Unopened":
        return "🟠 OPEN RAISE", f"{handy}인 테이블에서 버튼 인근 포지션 스틸 구간입니다."

    if env == "Live Pub (Loose)" and "s" in hand and r1 >= 10:
        return "🟢 CALL", "라이브 펍 환경: 수딧 핸드의 포스트플랍 가치가 높습니다."

    return "🔵 FOLD", "수학적 기대값이 낮습니다."

# --- 5. 결과 및 리뷰 ---
st.divider()
res_act, res_why = get_poker_action(env, handy, stack, pos, v1, v2, suit, action)

st.subheader("🎯 Result")
if "🔴" in res_act: st.error(f"## {res_act}")
elif "🟠" in res_act: st.warning(f"## {res_act}")
elif "🟢" in res_act: st.success(f"## {res_act}")
else: st.info(f"## {res_act}")

st.info(f"**💡 전략 근거:** {res_why}")

st.markdown("---")
st.header("📝 Game Review")
with st.expander("Record this hand"):
    rev_win = st.radio("Result", ["Win 🏆", "Loss 💀"], horizontal=True)
    rev_note = st.text_area("Note", placeholder="상대 성향이나 복기 내용을 적으세요.")
    if st.button("Save"):
        st.success(f"Saved: {rev_win}")
