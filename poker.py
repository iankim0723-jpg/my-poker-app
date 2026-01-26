import streamlit as st

# 1. 페이지 설정 (최상단에 위치해야 함)
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

# --- 3. 카드 선택 (이모지 활용) ---
st.subheader("🎴 Card Selection")
card_icons = {"A":"🂡 A", "K":"🂮 K", "Q":"🂭 Q", "J":"🂫 J", "T":"🂪 10", "9":"9", "8":"8", "7":"7", "6":"6", "5":"5", "4":"4", "3":"3", "2":"2"}

col1, col2, col3 = st.columns(3)
with col1:
    v1 = st.selectbox("Card 1", list(card_icons.keys()), format_func=lambda x: card_icons[x])
with col2:
    v2 = st.selectbox("Card 2", list(card_icons.keys()), format_func=lambda x: card_icons[x])
with col3:
    suit = st.radio("Suit", ["Suited(s)", "Off-suit(o)"], horizontal=True)

# --- 4. 전략 로직 함수 ---
def get_strategy(env, handy, stack, street, pos, v1, v2, suit, act):
    ranks = {"A":14, "K":13, "Q":12, "J":11, "T":10, "9":9, "8":8, "7":7, "6":6, "5":5, "4":4, "3":3, "2":2}
    r1, r2 = ranks[v1], ranks[v2]
    if r1 < r2: v1, v2 = v2, v1
    hand = f"{v1}{v2}" + ("s" if suit == "Suited(s)" and v1 != v2 else "")

    # 숏스택(25BB) 전략
    if stack <= 25:
        if r1 >= 13 or (v1 == v2 and r1 >= 8): return "🔴 ALL-IN / JAM", "숏스택에서는 주도권을 잡고 올인하는 것이 최선입니다."
        return "🔵 FOLD", "숏스택은 살아남는 것이 우선입니다."

    # 환경 및 인원수 보정
    if hand in ["AA", "KK", "QQ", "AKs", "AKo", "JJ"]:
        return "🔴 3-BET / RAISE", "가장 강력한 핸드입니다. 큰 밸류를 노리세요."
    
    if pos in ["BTN", "CO"] and (act == "Unopened" or handy <= 4):
        return "🟠 OPEN RAISE", f"{handy}인 테이블에서는 이 핸드로 스틸이 가능합니다."

    if env == "Live Pub (Loose)" and "
