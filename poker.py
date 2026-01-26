import streamlit as st

# 모바일 화면 최적화 설정
st.set_page_config(page_title="Holdem Solver", page_icon="♠️")

st.title("♠️ Poker Strategy")

# --- 모바일에서 잘 보이도록 메뉴를 중앙으로 배치 ---
st.markdown("### 1. Game Situation")
pos = st.selectbox("Position", ["UTG", "MP", "CO", "BTN", "SB", "BB"])
action = st.radio("Opponent Action", ["Unopened", "Facing a Raise"], horizontal=True)

st.markdown("---")
st.markdown("### 2. My Hand")
c1 = st.selectbox("Card 1", ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"])
c2 = st.selectbox("Card 2", ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"])
suit_type = st.radio("Suit", ["Suited(s)", "Off-suit(o)"], horizontal=True)

# --- 전략 로직 ---
def get_action(p, card1, card2, s_type, act):
    ranks = {"A":14, "K":13, "Q":12, "J":11, "T":10, "9":9, "8":8, "7":7, "6":6, "5":5, "4":4, "3":3, "2":2}
    v1, v2 = ranks[card1], ranks[card2]
    if v1 < v2: card1, card2 = card2, card1
    hand = f"{card1}{card2}" + ("s" if s_type == "Suited(s)" and card1 != card2 else "")

    if hand in ["AA", "KK", "QQ", "AKs", "AKo", "AQs", "JJ"]:
        return "🔴 강력한 레이즈 / 3-Bet", "프리미엄 핸드입니다. 공격적으로 플레이하세요."
    if p in ["BTN", "CO"] and act == "Unopened":
        return "🟠 오픈 레이즈 (Open Raise)", "포지션을 활용해 블라인드를 스틸하세요."
    if p in ["UTG", "MP"] and hand in ["TT", "99", "AJs", "KQs", "AQo"]:
        return "🟠 오픈 레이즈 (Open Raise)", "강한 핸드이므로 레이즈로 시작하세요."
    return "🔵 폴드 (Fold)", "수학적으로 기대값이 낮은 핸드입니다."

# --- 결과 출력 ---
st.divider()
res_action, res_reason = get_action(pos, c1, c2, suit_type, action)

st.subheader("🎯 Result")
if "🔴" in res_action:
    st.error(f"## {res_action}")
elif "🟠" in res_action:
    st.warning(f"## {res_action}")
elif "🟢" in res_action:
    st.success(f"## {res_action}")
else:
    st.info(f"## {res_action}")

st.write(f"**💡 전략 근거:** {res_reason}")
