import streamlit as st
import pandas as pd

# 1. 앱 기본 설정
st.set_page_config(page_title="JM LEGEND 03 (Sync Fixed)", page_icon="🛡️", layout="centered")

# --- 데이터 정의 ---
pos_list = ["UTG", "UTG+1", "MP", "LJ", "HJ", "CO", "BTN", "SB", "BB"]
cards = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]

# --- Session State 초기화 (값 동기화의 핵심) ---
if 'my_pos' not in st.session_state: st.session_state.my_pos = "BTN"
if 'raise_amt' not in st.session_state: st.session_state.raise_amt = 2.5
if 'c1' not in st.session_state: st.session_state.c1 = "A"
if 'c2' not in st.session_state: st.session_state.c2 = "K"

# --- 동기화 함수들 (Callbacks) ---
def sync_pos_slider(): st.session_state.my_pos = st.session_state.pos_slider
def sync_pos_box(): st.session_state.my_pos = st.session_state.pos_box

def sync_raise_slider(): st.session_state.raise_amt = st.session_state.raise_slider
def sync_raise_box(): st.session_state.raise_amt = st.session_state.raise_box

def sync_c1_slider(): st.session_state.c1 = st.session_state.c1_slider
def sync_c1_box(): st.session_state.c1 = st.session_state.c1_box

def sync_c2_slider(): st.session_state.c2 = st.session_state.c2_slider
def sync_c2_box(): st.session_state.c2 = st.session_state.c2_box

# CSS: 적녹색약 배려 & 하이브리드 레이아웃
st.markdown("""
    <style>
    /* 배경 및 사이드바 */
    [data-testid="stSidebar"] { background-color: #111; border-right: 3px solid #D55E00; }
    
    /* 명언 박스 */
    .quote-box { 
        background-color: #222; color: #D55E00; padding: 15px; border-radius: 10px; 
        border: 2px solid #D55E00; text-align: center; font-weight: bold; font-size: 1.0em; margin-bottom: 20px;
    }
    
    /* 텍스트 크기 확대 */
    .big-font { font-size: 1.3em; font-weight: 900; color: #fff; margin-bottom: 5px; margin-top: 10px; }
    
    /* 결과 박스 스타일 (색약 배려) */
    .res-box-raise { background-color: #D55E00; color: white; padding: 20px; border-radius: 12px; text-align: center; font-size: 1.8em; font-weight: bold; margin: 10px 0; }
    .res-box-call { background-color: #0072B2; color: white; padding: 20px; border-radius: 12px; text-align: center; font-size: 1.8em; font-weight: bold; margin: 10px 0; }
    .res-box-fold { background-color: #333333; color: #BBBBBB; padding: 20px; border-radius: 12px; text-align: center; font-size: 1.8em; font-weight: bold; margin: 10px 0; border: 2px solid #555; }
    
    /* 입력 위젯 스타일 조정 */
    div.stButton > button { width: 100%; height: 60px; font-weight: bold; font-size: 1.3em; border-radius: 12px; }
    
    /* 하단 차트 */
    .chart-header { color: #D55E00; font-weight: bold; font-size: 1.2em; margin-top: 20px; }
    </style>
""", unsafe_allow_html=True)

# --- 사용설명서 팝업 ---
@st.dialog("📖 매뉴얼 (Hybrid Input)")
def show_manual():
    st.markdown("""
    ### ⚡ 하이브리드 입력 시스템
    * **동기화**: 슬라이더를 밀면 입력창이 바뀌고, 입력창을 바꾸면 슬라이더가 바뀝니다. 편한 것을 쓰세요.
    
    ### 🎨 색약 모드 (Color Safe)
    * **🟠 RAISE**: 공격 (주황)
    * **🔵 CALL**: 방어 (파랑)
    * **⚪ FOLD**: 포기 (회색)
    """)

# --- 메인 상단 ---
st.markdown('<div class="quote-box">"한번 우승했다고 우쭐대지마라<br>그게 나락으로 가는 지름길이다"</div>', unsafe_allow_html=True)
st.title("🛡️ JM LEGEND 03")
st.caption("⚡ Perfect Sync Engine")

# --- 2. 사이드바 (설정 고정) ---
with st.sidebar:
    st.header("⚙️ Game Setup")
    if st.button("📖 매뉴얼/색상안내"):
        show_manual()
        
    mode = st.radio("Game Mode", ["Cash Game", "Tournament"], index=1)
    min_p = 5 if mode == "Tournament" else 2
    env_options = ["Online", "Live Pub", "Competition"]
    env = st.selectbox("Environment", env_options, index=1)
    
    if mode == "Tournament":
        total_entries = st.number_input("Entries", 10, 10000, 100)
    else:
        total_entries = 0

    h_in = st.number_input("Players", min_p, 9, 9)
    st.markdown("---")
    st.header("💰 Stack (BB)")
    my_stack = st.number_input("My BB", 1, 1000, 50)
    villain_stack = st.number_input("Villain BB", 1, 1000, 50)
    eff_stack = min(my_stack, villain_stack)
    st.metric("Eff. Stack", f"{eff_stack} BB")

# --- 3. 메인 화면 (동기화 입력 시스템) ---

# [1] Position: Slider + Selectbox
st.markdown('<p class="big-font">📍 Position</p>', unsafe_allow_html=True)
col_p1, col_p2 = st.columns([3, 1.2])

with col_p1:
    st.select_slider("Pos Slider", options=pos_list, value=st.session_state.my_pos, 
                     key="pos_slider", label_visibility="collapsed", on_change=sync_pos_slider)
with col_p2:
    st.selectbox("Pos Box", options=pos_list, index=pos_list.index(st.session_state.my_pos), 
                 key="pos_box", label_visibility="collapsed", on_change=sync_pos_box)

# [2] Action
st.markdown('<p class="big-font">⚔️ Action</p>', unsafe_allow_html=True)
action = st.radio("Act", ["Unopened", "Facing Raise", "Facing All-in"], horizontal=True, label_visibility="collapsed")

final_raise_amt = 0.0

if action == "Facing Raise":
    st.markdown("**상대 레이즈 (BB)**")
    col_r1, col_r2 = st.columns([3, 1.2])
    
    # 레이즈 금액 동기화
    with col_r1:
        # 슬라이더는 2.0 ~ 15.0 범위만 담당 (그 외 값은 입력창에서 처리해도 에러 안나게 max 값 조정)
        slider_val = st.session_state.raise_amt if 2.0 <= st.session_state.raise_amt <= 15.0 else 2.0
        st.slider("BB Slider", 2.0, 15.0, slider_val, 0.5, key="raise_slider", label_visibility="collapsed", on_change=sync_raise_slider)
    with col_r2:
        st.number_input("BB Input", 2.0, 100.0, st.session_state.raise_amt, 0.5, key="raise_box", label_visibility="collapsed", on_change=sync_raise_box)
    
    final_raise_amt = st.session_state.raise_amt
    if final_raise_amt >= 6.0: st.caption("⚠️ Big Raise (6BB+)")

elif action == "Facing All-in":
    st.markdown("**상대 올인 (BB)**")
    max_val = float(villain_stack)
    col_a1, col_a2 = st.columns([3, 1.2])
    
    # 올인은 슬라이더 동기화가 복잡하므로 단순화 (입력창 우선)
    with col_a2:
        ai_in = st.number_input("Allin Input", 1.0, 1000.0, max_val/2, label_visibility="collapsed")
    with col_a1:
        st.slider("Allin Slider", 1.0, max_val if max_val > 1.0 else 100.0, ai_in, label_visibility="collapsed", disabled=True)
        st.caption("※ 올인은 입력창을 이용하세요")
    final_raise_amt = ai_in

st.divider()

# [3] Hand: Slider + Selectbox Sync
st.markdown('<p class="big-font">🃏 My Hand</p>', unsafe_allow_html=True)
c1_col, c2_col, s_col = st.columns([2.5, 2.5, 1.5])

with c1_col:
    st.caption("Card 1")
    st.selectbox("C1 Box", cards, index=cards.index(st.session_state.c1), key="c1_box", label_visibility="collapsed", on_change=sync_c1_box)
    st.select_slider("C1 Slider", cards, value=st.session_state.c1, key="c1_slider", label_visibility="collapsed", on_change=sync_c1_slider)

with c2_col:
    st.caption("Card 2")
    st.selectbox("C2 Box", cards, index=cards.index(st.session_state.c2), key="c2_box", label_visibility="collapsed", on_change=sync_c2_box)
    st.select_slider("C2 Slider", cards, value=st.session_state.c2, key="c2_slider", label_visibility="collapsed", on_change=sync_c2_slider)

with s_col:
    st.caption("Suit")
    suit_select = st.radio("S", ["s", "o"], horizontal=True, label_visibility="collapsed")
    suit = "s" if suit_select == "s" else "o"

# --- 5. LOGIC ENGINE (로직 100% 고정) ---
def calculate_logic(mode, env, pos, v1, v2, suit, act, hero_stack, eff_stack, amt, entries):
    rank_map = {"A":14, "K":13, "Q":12, "J":11, "T":10, "9":9, "8":8, "7":7, "6":6, "5":5, "4":4, "3":3, "2":2}
    r1, r2 = rank_map[v1], rank_map[v2]
    if r1 < r2: v1, v2, r1, r2 = v2, v1, r2, r1
    is_pair = (v1 == v2)
    is_s = (suit == "s")
    hand_str = f"{v1}{v2}{suit}" if not is_pair else f"{v1}{v2}"
    
    # [PREMIUMS]
    if hand_str in ["AA", "KK", "QQ", "AKs", "AKo"]:
        if act == "Facing All-in": return "RAISE", "🔴 SNAP CALL (최강 핸드)"
        if act == "Facing Raise": return "RAISE", "🔥 3-BET (필수 밸류)"
        return "RAISE", "🟠 RAISE (무조건 오픈)"

    # [BB DEFENSE]
    if act == "Facing Raise" and pos == "BB":
        if amt >= 6.0:
            if hand_str in ["JJ", "TT", "99", "AQs", "AJs"]: return "CALL", "⚔️ CALL (빅 오픈 방어)"
            return "FOLD", "🔵 FOLD (사이즈 너무 큼)"
        elif amt >= 4.0:
            if is_pair and r1 >= 7: return "CALL", "🔵 CALL (중간 페어)"
            if is_s and r1 >= 11: return "CALL", "🔵 CALL (수딧 브로드웨이)"
            if not is_s and r1 >= 13 and r2 >= 10: return "CALL", "🔵 CALL (AQ/KQ)"
            return "FOLD", "⚪ FOLD (타이트)"
        else:
            if is_pair or is_s: return "CALL", "🔵 DEFEND (배당 방어)"
            if r1 + r2 >= 19: return "CALL", "🔵 DEFEND (커넥터)"
            return "FOLD", "⚪ FOLD (Trash)"

    # [CASH]
    if mode == "Cash Game":
        if act == "Facing Raise":
            if is_pair and r1 < 10:
                if (eff_stack / amt) >= 20: return "CALL", "🔵 CALL (셋마이닝)"
                else: return "FOLD", "⚪ FOLD (배당 부족)"
            if "Live" in env and is_s and (r1-r2 == 1) and r1 < 12 and pos in ["BTN", "CO"]:
                return "CALL", "🔵 CALL (라이브펍 수딧)"

    # [TOURNAMENT]
    else:
        if act == "Facing All-in":
            risk_life = (hero_stack <= amt) or (hero_stack <= eff_stack)
            if risk_life:
                if hand_str in ["JJ", "AQs"]: return "CALL", "⚔️ CALL (승부)"
                if hand_str in ["TT", "99", "88"]: return "FOLD", "⚪ FOLD (생존 우선)"
            else:
                if hand_str in ["JJ", "TT", "99", "AQ"]: return "CALL", "🔵 CALL (Bully)"

        if hero_stack <= 15 and act == "Unopened":
             if is_pair or r1 >= 10 or (is_s and r1 >= 8): return "RAISE", "🚀 JAM (15BB 올인)"

    # [RFI]
    if act == "Unopened":
        if pos == "BB": return "CALL", "🎉 WALK (승리)"
        if is_pair and r1 >= 7: return "RAISE", "🟠 OPEN (정석)"
        if r1 >= 11: return "RAISE", "🟠 OPEN (하이카드)"
        if pos in ["BTN", "CO"] and is_s: return "RAISE", "🟠 OPEN (스틸)"

    return "FOLD", "⚪ FOLD (EV -)"

# --- 6. 결과 출력 ---
st.divider()
action_type, msg = calculate_logic(mode, env, st.session_state.my_pos, st.session_state.c1, st.session_state.c2, suit, action, my_stack, eff_stack, final_raise_amt, int(total_entries))

if action_type == "RAISE":
    st.markdown(f'<div class="res-box-raise">{msg}</div>', unsafe_allow_html=True)
elif action_type == "CALL":
    st.markdown(f'<div class="res-box-call">{msg}</div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div class="res-box-fold">{msg}</div>', unsafe_allow_html=True)

# --- 7. 하단 고정 차트 (유지) ---
st.markdown("---")
st.markdown('<p class="chart-header">🚀 Short Stack Push (20BB↓)</p>', unsafe_allow_html=True)
st.table(pd.DataFrame({
    "Pos": ["UTG", "HJ", "CO", "BTN", "SB"],
    "Push": ["77+, AJs+", "55+, A9s+", "22+, A8o+", "Any Pair/Ax", "Any Pair/Ax"]
}))

st.markdown('<p class="chart-header">📊 RFI Range Detail</p>', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    st.info("**Early Pos**\n\nUTG: 77+, ATs+\nMP: 55+, KJs+")
with col2:
    st.info("**Late Pos**\n\nCO: 22+, A8o+\nBTN: Any Pair, Any Suited")
