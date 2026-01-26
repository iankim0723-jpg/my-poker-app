import streamlit as st

# 1. 앱 설정 (최상단 필수)
st.set_page_config(page_title="Poker Master Solver", page_icon="🃏")

# --- 앱 타이틀 ---
st.title("🃏 Poker Master Solver")
st.caption("Handy, Position, Stack & Review")

# --- 2. 게임 설정 (Sidebar) ---
with st.sidebar:
    st.header("⚙️ Game Settings")
    env = st.selectbox("Environment", ["Online (GTO)", "Live Pub (Loose)", "Tournament (Tight)"])
    handy = st.slider("Handy (Players)", 2, 9, 6)
    
    st.markdown("---")
    # 스택 설정
    stack_mode = st.radio("Stack Input Mode", ["Select BB", "Manual Input"])
    if stack_mode == "Select BB":
        stack = st.select_slider("Stack Size (BB)", options=[25, 50, 75, 100], value=50)
    else:
        # 블라인드 직접 입력 (선택 사항)
        my_chips = st.number_input("My Chips", value=100000)
        bb_amount = st.number_input("Big Blind Amount", value=2000)
        stack = my_chips / bb_amount if bb_amount > 0 else 50
        st.write(f"Calculated: {stack:.1f} BB")

    st.markdown("---")
    pos = st.selectbox("Position", ["UTG", "MP", "CO", "BTN", "SB", "BB"])
    action = st.radio("Opponent Action", ["Unopened", "Facing a Raise"])

# --- 3. 카드 선택 (메인 화면) ---
st.subheader("🎴 Card Selection")
card_icons = {"A":"🂡 A", "K":"🂮 K", "Q":"🂭 Q", "J":"🂫 J", "T":"🂪 10", "9":"9", "8":"8", "7":"7", "6":"6", "5":"5", "4":"4", "3":"3", "2":"2"}

c1, c2, c3 = st.columns(3)
with c1: v1 = st.selectbox("Card 1", list(card_icons.keys()), format_func=lambda x: card_icons[x])
with c2: v2 = st.selectbox("Card 2", list(card_icons.keys()), format_func=lambda x: card_icons[x])
with c3: suit = st.radio("Suit", ["Suited(s)", "Off-suit(o)"], horizontal=True)

# --- 4. 전략 로직 ---
def get_poker_action(env, handy, stack, pos, v1, v2, suit, act):
    ranks = {"A":14, "K":13, "Q":12, "J":11, "T":10, "9":9, "8":8, "7":7, "6":6, "5":5, "4":4, "3":3, "2":2}
    r1, r2 = ranks[v1], ranks[v2]
    if r1 < r2: v1, v2 = v2, v1
    hand = f"{v1}{v2}" + ("s" if suit == "Suited(s)" and v1 != v2 else "")

    # 숏스택 전략 (25BB 이하)
    if stack <= 30:
        if r1 >= 13 or (v1 == v2 and r1 >= 7): return "🔴 ALL-IN", "숏스택입니다. 주도권을 갖고 칩을 밀어넣으세요."
        return "🔵 FOLD", "리스크를 피하고 더 확실한 기회를 기다리세요."

    # 정석 프리미엄 핸드
    if hand in ["AA", "KK", "QQ", "AKs", "AKo", "JJ", "TT"]:
        return "🔴 RAISE / 3-BET", "강력한 핸드입니다. 팟을 키워 수익을 극대화하세요."

    # 포지션 및 인원수 보정
    if pos in ["BTN", "CO"] and act == "Unopened":
        return "🟠 OPEN RAISE", f"{handy}인 테이블 포지션 이점을 활용한 스틸 구간입니다."

    if env == "Live Pub (Loose)" and "s" in hand and r1 >= 10:
        return "🟢 CALL", "라이브 펍 환경입니다. 수딧 핸드로 플랍을 볼 가치가 있습니다."

    return "🔵 FOLD", "수학적으로 기대값이 낮습니다. 다음 핸드를 기다리세요."

# --- 5. 결과 출력 ---
st.divider()
res_act, res_why = get_poker_action(env, handy, stack, pos, v1, v2, suit, action)

st.subheader("🎯 Recommended Action")
if "🔴" in res_act: st.error(f"## {res_act}")
elif "🟠" in res_act: st.warning(f"## {res_act}")
elif "🟢" in res_act: st.success(f"## {res_act}")
else: st.info(f"## {res_act}")

st.info(f"**💡 전략 근거:** {res_why} (Stack: {stack:.1f}BB / Handy: {handy}인)")

# --- 6. 복기 기능 ---
st.markdown("---")
st.header("📝 Game Review")
with st.expander("방금 판의 결과를 기록해두세요"):
    rev_win = st.radio("Result", ["Win 🏆", "Loss 💀"], horizontal=True)
    rev_note = st.text_area("Review Note", placeholder="예: 버튼 스틸 성공, 상대가 너무 루즈함 등")
    if st.button("저장하기"):
        st.success(f"기록됨: {rev_win} / {rev_note}")
