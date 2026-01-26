import streamlit as st

# Page Configuration
st.set_page_config(page_title="Holdem Strategy Solver", page_icon="♠️")

st.title("♠️ Poker Pre-flop Assistant")
st.markdown("Select your situation and hand to get the optimal strategy.")

# --- Sidebar: Position & Action ---
with st.sidebar:
    st.header("1. Situation")
    pos = st.selectbox("Position", ["UTG", "MP", "CO", "BTN", "SB", "BB"])
    action = st.radio("Opponent Action", ["Unopened", "Facing a Raise"])

# --- Main: Hand Selection ---
st.subheader("2. Hand Selection")
col1, col2, col3 = st.columns(3)

with col1:
    card1 = st.selectbox("Card 1", ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"])
with col2:
    card2 = st.selectbox("Card 2", ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"])
with col3:
    suit_type = st.radio("Suit", ["Suited(s)", "Off-suit(o)"])

# --- Logic: GTO Based ---
def get_action(p, c1, c2, s_type, act):
    # Ranking logic
    ranks = {"A":14, "K":13, "Q":12, "J":11, "T":10, "9":9, "8":8, "7":7, "6":6, "5":5, "4":4, "3":3, "2":2}
    v1, v2 = ranks[c1], ranks[c2]
    
    # Ensure c1 is higher rank
    if v1 < v2:
        c1, c2 = c2, c1
        
    hand = f"{c1}{c2}" + ("s" if s_type == "Suited(s)" and c1 != c2 else "")

    # Premium Hands
    if hand in ["AA", "KK", "QQ", "AKs", "AKo", "AQs", "JJ"]:
        return "🔴 강력한 레이즈 / 3-Bet", "현재 가장 강력한 핸드입니다. 무조건 공격적으로 플레이하세요."

    # Position based logic
    if p in ["BTN", "CO"]:
        if act == "Unopened":
            return "🟠 오픈 레이즈 (Open Raise)", "포지션이 매우 유리합니다. 넓은 핸드 범위로 블라인드를 공격하세요."
        else:
            if "s" in hand or v1 >= 11:
                return "🟢 콜 (Call)", "포지션 이점이 있으므로 플랍을 보고 판단하는 것이 수익성이 높습니다."
            
    if p in ["UTG", "MP"]:
        if hand in ["TT", "99", "AJs", "KQs", "AQo"]:
            return "🟠 오픈 레이즈 (Open Raise)", "얼리 포지션이지만 충분히 강한 핸드입니다. 레이즈로 시작하세요."
        else:
            return "🔵 폴드 (Fold)", "앞자리에서는 더 보수적으로 운영해야 합니다. 이 핸드는 버리는 것이 안전합니다."

    return "🔵 폴드 (Fold)", "수학적으로 승률이 낮은 핸드입니다. 무리한 플레이는 피하세요."

# --- Output ---
st.divider()
res_action, res_reason = get_action(pos, card1, card2, suit_type, action)

st.markdown("### 🎯 Recommended Action")
if "🔴" in res_action:
    st.error(f"## {res_action}")
elif "🟠" in res_action:
    st.warning(f"## {res_action}")
elif "🟢" in res_action:
    st.success(f"## {res_action}")
else:
    st.info(f"## {res_action}")

st.info(f"**💡 전략 근거:** {res_reason}")