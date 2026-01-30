import streamlit as st
import pandas as pd

# 1. 앱 기본 설정
st.set_page_config(page_title="JM LEGEND 03 (Pro Charts)", page_icon="🛡️", layout="centered")

# --- 데이터 정의 ---
pos_list = ["UTG", "UTG+1", "MP", "LJ", "HJ", "CO", "BTN", "SB", "BB"]
cards = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]

# --- CSS: 적녹색약 배려 & 차트 스타일링 ---
st.markdown("""
    <style>
    /* 전체 배경 및 사이드바 */
    [data-testid="stSidebar"] { background-color: #111; border-right: 3px solid #D55E00; }
    
    /* 명언 박스 */
    .quote-box { 
        background-color: #222; color: #fff; padding: 15px; border-radius: 10px; 
        border: 2px solid #D55E00; text-align: center; font-weight: bold; font-size: 1.0em; margin-bottom: 20px;
    }
    .quote-author { color: #D55E00; font-size: 0.8em; margin-top: 5px; display: block; }
    
    /* 텍스트 가독성 */
    .big-font { font-size: 1.3em; font-weight: 900; color: #fff; margin-top: 10px; margin-bottom: 5px; }
    
    /* 결과 박스 (색약 안심) */
    .res-box-raise { background-color: #D55E00; color: white; padding: 15px; border-radius: 10px; text-align: center; font-size: 1.6em; font-weight: bold; margin: 10px 0; }
    .res-box-call { background-color: #0072B2; color: white; padding: 15px; border-radius: 10px; text-align: center; font-size: 1.6em; font-weight: bold; margin: 10px 0; }
    .res-box-fold { background-color: #333333; color: #BBBBBB; padding: 15px; border-radius: 10px; text-align: center; font-size: 1.6em; font-weight: bold; margin: 10px 0; border: 2px solid #555; }
    
    /* 위젯 크기 확대 (터치 최적화) */
    div.stButton > button { width: 100%; height: 60px; font-size: 1.2em; border-radius: 10px; font-weight: bold; }
    
    /* 하단 차트 스타일 */
    .chart-header { color: #D55E00; font-weight: bold; font-size: 1.2em; margin-top: 30px; margin-bottom: 10px; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #222; border-radius: 5px; color: #fff; }
    .stTabs [aria-selected="true"] { background-color: #D55E00; color: white; }
    </style>
""", unsafe_allow_html=True)

# --- 2. 사이드바 (설정) ---
with st.sidebar:
    st.header("⚙️ Game Setup")
    mode = st.radio("Game Mode", ["Cash Game", "Tournament"], index=1)
    
    env = st.selectbox("Environment", ["Online", "Live Pub", "Competition"], index=1)
    
    if mode == "Tournament":
        total_entries = st.number_input("Total Entries", min_value=2, max_value=100000, value=100, step=1)
    else:
        total_entries = 0
    
    h_in = st.number_input("Active Players", min_value=2, max_value=20, value=9, step=1)
    
    st.markdown("---")
    st.header("💰 Stack (BB)")
    my_stack = st.number_input("My BB", 1, 1000, 50)
    villain_stack = st.number_input("Villain BB", 1, 1000, 50)
    eff_stack = min(my_stack, villain_stack)
    st.metric("Eff. Stack", f"{eff_stack} BB")

# --- 3. 메인 화면 ---
st.markdown("""
    <div class="quote-box">
        "한번 우승했다고 우쭐대지마라 그게 나락으로 가는 지름길이다"
        <span class="quote-author">- 더홀릭 우승 경험자 CBJ -</span>
    </div>
""", unsafe_allow_html=True)

st.title("🛡️ JM LEGEND 03")

# [1] Position
st.markdown('<p class="big-font">📍 Position</p>', unsafe_allow_html=True)
col_p1, col_p2 = st.columns([3, 1.2])

with col_p1:
    pos_slider = st.select_slider("Pos Slider", options=pos_list, value="BTN", label_visibility="collapsed")
with col_p2:
    pos_box = st.selectbox("Pos Box", options=pos_list, index=pos_list.index(pos_slider), label_visibility="collapsed")

final_pos = pos_box 

# [2] Action
st.markdown('<p class="big-font">⚔️ Action</p>', unsafe_allow_html=True)
action = st.radio("Act", ["Unopened", "Facing Raise", "Facing All-in"], horizontal=True, label_visibility="collapsed")

final_amt = 0.0

if action == "Facing Raise":
    st.markdown("**상대 레이즈 (BB)**")
    col_r1, col_r2 = st.columns([2.5, 1.5])
    with col_r1:
        val_slider = st.slider("Raise Slider", 2.0, 10.0, 2.5, 0.5, label_visibility="collapsed")
    with col_r2:
        val_input = st.number_input("Raise Input", 0.0, 1000.0, val_slider, step=0.5, label_visibility="collapsed")
    final_amt = val_input
    if final_amt >= 6.0: st.caption(f"⚠️ Big Raise: {final_amt}BB")

elif action == "Facing All-in":
    st.markdown("**상대 올인 (BB)**")
    max_val = float(villain_stack)
    col_a1, col_a2 = st.columns([2, 2])
    with col_a1:
        val_slider = st.slider("AI Slider", 1.0, max_val, max_val/2, label_visibility="collapsed")
    with col_a2:
        val_input = st.number_input("AI Input", 1.0, 1000.0, val_slider, label_visibility="collapsed")
    final_amt = val_input

st.divider()

# [3] Hand
st.markdown('<p class="big-font">🃏 My Hand</p>', unsafe_allow_html=True)
c1_col, c2_col, s_col = st.columns([2.5, 2.5, 1.5])

with c1_col:
    st.caption("Card 1")
    v1_slider = st.select_slider("C1", options=cards, value="A", label_visibility="collapsed")
    v1_box = st.selectbox("C1 Box", cards, index=cards.index(v1_slider), label_visibility="collapsed")
    v1 = v1_box

with c2_col:
    st.caption("Card 2")
    v2_slider = st.select_slider("C2", options=cards, value="K", label_visibility="collapsed")
    v2_box = st.selectbox("C2 Box", cards, index=cards.index(v2_slider), label_visibility="collapsed")
    v2 = v2_box

with s_col:
    st.caption("Suit")
    suit_radio = st.radio("S", ["s", "o"], horizontal=True, label_visibility="collapsed")
    suit = "s" if suit_radio == "s" else "o"

# --- 4. Logic Engine ---
def get_decision(mode, env, pos, v1, v2, suit, act, h_stack, e_stack, amt):
    rk = {"A":14, "K":13, "Q":12, "J":11, "T":10, "9":9, "8":8, "7":7, "6":6, "5":5, "4":4, "3":3, "2":2}
    r1, r2 = rk[v1], rk[v2]
    if r1 < r2: v1, v2, r1, r2 = v2, v1, r2, r1
    is_pair = (v1 == v2)
    is_s = (suit == "s")
    hand = f"{v1}{v2}{suit}" if not is_pair else f"{v1}{v2}"

    if hand in ["AA", "KK", "QQ", "AKs", "AKo"]:
        if act == "Facing All-in": return "RAISE", "🔴 SNAP CALL (최강 핸드)"
        if act == "Facing Raise": return "RAISE", "🔥 3-BET (필수 밸류)"
        return "RAISE", "🟠 RAISE (무조건 오픈)"

    if act == "Facing Raise" and pos == "BB":
        if amt >= 6.0:
            if hand in ["JJ", "TT", "99", "AQs", "AJs"]: return "CALL", "⚔️ CALL (빅 오픈 방어)"
            return "FOLD", "🔵 FOLD (사이즈 큼)"
        elif amt >= 4.0:
            if is_pair and r1 >= 7: return "CALL", "🔵 CALL (중간 페어)"
            if is_s and r1 >= 11: return "CALL", "🔵 CALL (수딧 브로드웨이)"
            return "FOLD", "⚪ FOLD (타이트)"
        else:
            if is_pair or is_s: return "CALL", "🔵 DEFEND (배당)"
            if r1+r2 >= 19: return "CALL", "🔵 DEFEND (커넥터)"
            return "FOLD", "⚪ FOLD (Trash)"

    if mode == "Cash Game":
        if act == "Facing Raise":
            if is_pair and r1 < 10:
                if (e_stack/amt) >= 20: return "CALL", "🔵 CALL (셋마이닝)"
                return "FOLD", "⚪ FOLD (배당 부족)"
            if "Live" in env and is_s and (r1-r2==1) and r1 < 12 and pos in ["BTN", "CO"]:
                return "CALL", "🔵 CALL (라이브 수딧)"

    else:
        if act == "Facing All-in":
            risk_life = (h_stack <= amt) or (h_stack <= e_stack)
            if risk_life:
                if hand in ["JJ", "AQs"]: return "CALL", "⚔️ CALL (승부)"
                if hand in ["TT", "99", "88"]: return "FOLD", "⚪ FOLD (생존)"
            else:
                if hand in ["JJ", "TT", "99", "AQ"]: return "CALL", "🔵 CALL (Bully)"
        
        if h_stack <= 15 and act == "Unopened":
            if is_pair or r1 >= 10 or (is_s and r1 >= 8): return "RAISE", "🚀 JAM (15BB)"

    if act == "Unopened":
        if pos == "BB": return "CALL", "🎉 WALK"
        if is_pair and r1 >= 7: return "RAISE", "🟠 OPEN (정석)"
        if r1 >= 11: return "RAISE", "🟠 OPEN (하이)"
        if pos in ["BTN", "CO"] and is_s: return "RAISE", "🟠 OPEN (스틸)"

    return "FOLD", "⚪ FOLD (EV -)"

# --- 5. 결과 출력 ---
decision, msg = get_decision(mode, env, final_pos, v1, v2, suit, action, my_stack, eff_stack, final_amt)

st.divider()
if decision == "RAISE":
    st.markdown(f'<div class="res-box-raise">{msg}</div>', unsafe_allow_html=True)
elif decision == "CALL":
    st.markdown(f'<div class="res-box-call">{msg}</div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div class="res-box-fold">{msg}</div>', unsafe_allow_html=True)

# --- 6. 하단 고정 차트 (심화 버전) ---
st.markdown("---")
st.markdown('<p class="chart-header">🚀 Short Stack Push (20BB↓)</p>', unsafe_allow_html=True)
st.table(pd.DataFrame({
    "Pos": ["UTG", "HJ", "CO", "BTN", "SB"],
    "Push": ["77+, AJs+, AQo+", "55+, A9s+, AJo+", "22+, A2s+, A8o+", "Any Pair, Any Ax, Kx", "Any Pair, Any Ax, Q5s+"]
}))

# [심화] GTO 정밀 핸드레인지 (탭 방식)
st.markdown('<p class="chart-header">📊 Professional GTO RFI Ranges</p>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Early (EP/MP)", "Late (CO/BTN)", "Blinds (SB)"])

with tab1:
    st.caption("※ 초기 포지션은 타이트하게 운영하세요.")
    st.table(pd.DataFrame({
        "Position": ["UTG (9-Max)", "UTG+1", "MP (Middle)"],
        "Pairs": ["77+, 66+(Mix)", "66+", "55+"],
        "Suited": ["ATs+, KTs+, QJs", "A9s+, K9s+, QTs+", "A5s+, K9s+, Q9s+"],
        "Off-suit": ["AQo+", "AJo+", "ATo+, KJo+"]
    }))

with tab2:
    st.caption("※ 칩을 불리기 위해 레인지를 넓히는 구간입니다.")
    st.table(pd.DataFrame({
        "Position": ["CO (Cut-off)", "BTN (Button)"],
        "Pairs": ["22+ (All Pairs)", "22+ (All Pairs)"],
        "Suited": ["A2s+, K8s+, Q9s+, 87s+", "Any Suited Ax/Kx, Q5s+, 54s+"],
        "Off-suit": ["ATo+, KTo+, QTo+", "A2o+, K8o+, Q9o+, J9o+"]
    }))

with tab3:
    st.caption("※ SB는 레이크나 림프 전략에 따라 달라지지만, RFI 기준입니다.")
    st.table(pd.DataFrame({
        "Position": ["SB (Small Blind)"],
        "Pairs": ["22+ (All Pairs)"],
        "Suited": ["A2s+, K5s+, Q8s+, J8s+, T8s+, 98s"],
        "Off-suit": ["A7o+, K9o+, Q9o+, J9o+"]
    }))
