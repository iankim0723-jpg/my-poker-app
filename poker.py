import streamlit as st
import pandas as pd

# 1. 앱 기본 설정
st.set_page_config(page_title="JM LEGEND 03 (Hybrid)", page_icon="🛡️", layout="centered")

# --- Session State 초기화 (슬라이더 <-> 입력창 동기화용) ---
if 'pos_idx' not in st.session_state: st.session_state.pos_idx = 6 # BTN
if 'raise_val' not in st.session_state: st.session_state.raise_val = 2.5
if 'c1_idx' not in st.session_state: st.session_state.c1_idx = 0 # A
if 'c2_idx' not in st.session_state: st.session_state.c2_idx = 1 # K

# 데이터 정의
pos_list = ["UTG", "UTG+1", "MP", "LJ", "HJ", "CO", "BTN", "SB", "BB"]
cards = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]

# CSS: 적녹색약 배려 & 모바일 가독성 & 하이브리드 레이아웃
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
    div[data-baseweb="select"] > div { font-weight: bold; }
    
    /* 하단 차트 */
    .chart-header { color: #D55E00; font-weight: bold; font-size: 1.2em; margin-top: 20px; }
    </style>
""", unsafe_allow_html=True)

# --- 사용설명서 팝업 ---
@st.dialog("📖 매뉴얼 (Hybrid Input)")
def show_manual():
    st.markdown("""
    ### ⚡ 하이브리드 입력 시스템
    * **슬라이더 & 입력창 연동**: 슬라이더를 밀어도 되고, 입력창(▼)을 눌러 직접 골라도 됩니다. 둘은 항상 같이 움직입니다.
    * **칸 표시**: 슬라이더 바에 위치가 대략적으로 표시되지만, 정확한 값은 옆의 입력창을 참고하세요.
    
    ### 🎨 색약 모드 (Color Safe)
    * **🟠 RAISE**: 공격 (주황)
    * **🔵 CALL**: 방어 (파랑)
    * **⚪ FOLD**: 포기 (회색)
    """)

# --- 메인 상단 ---
st.markdown('<div class="quote-box">"한번 우승했다고 우쭐대지마라<br>그게 나락으로 가는 지름길이다"</div>', unsafe_allow_html=True)
st.title("🛡️ JM LEGEND 03")
st.caption("⚡ Slider + Direct Input Sync")

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

def update_pos_slider():
    st.session_state.pos_idx = pos_list.index(st.session_state.pos_box)
def update_pos_box():
    # 슬라이더 값은 session_state에 자동 반영됨
    pass

with col_p1:
    # 슬라이더: options 리스트 사용
    pos = st.select_slider(
        "Pos Slider", 
        options=pos_list, 
        value=pos_list[st.session_state.pos_idx], 
        key="pos_slider",
        label_visibility="collapsed",
        on_change=update_pos_slider
    )
    # 슬라이더 변경 시 pos_idx 업데이트 (위 on_change가 먼저 호출됨, 하지만 select_slider는 인덱스가 아닌 값을 리턴하므로 역추적 필요)
    # *수정*: select_slider는 값을 리턴하므로, 값을 기준으로 box를 맞춰야 함.
    # 단순화를 위해 위 콜백 로직 대신, 렌더링 직전에 값 동기화 수행
    
with col_p2:
    # 직접 입력창
    pos_box = st.selectbox(
        "Pos Box", 
        options=pos_list, 
        index=pos_list.index(pos), # 슬라이더 값을 따름
        key="pos_box", 
        label_visibility="collapsed"
    )
    # 입력창이 바뀌면 -> 슬라이더도 바뀌어야 함. 
    # Streamlit 특성상 rerun 되면서 위 select_slider의 value가 pos_box 값이 됨.

# [2] Action: Radio (유지)
st.markdown('<p class="big-font">⚔️ Action</p>', unsafe_allow_html=True)
action = st.radio("Act", ["Unopened", "Facing Raise", "Facing All-in"], horizontal=True, label_visibility="collapsed")

raise_amt = 0.0
if action == "Facing Raise":
    st.markdown("**상대 레이즈 (BB)**")
    col_r1, col_r2 = st.columns([3, 1.2])
    
    # 동기화 로직: Number Input이 Master, Slider가 Slave 역할 겸용
    if 'raise_val' not in st.session_state: st.session_state.raise_val = 2.5
    
    with col_r2:
        num_in = st.number_input("BB Input", 2.0, 100.0, st.session_state.raise_val, step=0.5, label_visibility="collapsed", key="raise_box")
    
    with col_r1:
        # 슬라이더 범위 내에 있으면 슬라이더 값 업데이트
        slider_val = num_in if 2.0 <= num_in <= 15.0 else (15.0 if num_in > 15.0 else 2.0)
        raise_slider = st.slider("BB Slider", 2.0, 15.0, slider_val, step=0.5, label_visibility="collapsed", key="raise_slider")
    
    # 값 결정 (슬라이더가 움직였으면 슬라이더 값, 아니면 입력창 값)
    # 복잡성을 줄이기 위해: 사용자가 마지막으로 건드린 값을 사용해야 하지만,
    # 여기서는 '입력창'의 값을 최종값으로 쓰고 슬라이더는 보조 도구로 씁니다.
    # 단, 슬라이더를 움직였을 때 입력창을 갱신하려면 session state 콜백이 필요합니다.
    
    # 간단 해결책: 슬라이더 값을 최종 raise_amt로 쓰고, 입력창은 그냥 둠? 아니요 사용자가 원한건 동기화입니다.
    # -> raise_box의 on_change에서 raise_slider session state 업데이트
    # -> raise_slider의 on_change에서 raise_box session state 업데이트
    # 하지만 복잡해지므로, 이번 턴의 raise_amt는 raise_slider 값으로 하되, 
    # raise_slider 값이 raise_box와 다르면 raise_box를 업데이트하는 방식(Rerun)을 씁니다.
    
    if raise_slider != st.session_state.raise_val:
        st.session_state.raise_val = raise_slider
        st.rerun() # 슬라이더 움직이면 재실행해서 입력창 업데이트
    elif num_in != st.session_state.raise_val:
        st.session_state.raise_val = num_in
        st.rerun() # 입력창 바꾸면 재실행해서 슬라이더 업데이트

    raise_amt = st.session_state.raise_val
    if raise_amt >= 6.0: st.caption("⚠️ Big Raise (6BB+)")

elif action == "Facing All-in":
    st.markdown("**상대 올인 (BB)**")
    max_val = float(villain_stack)
    col_a1, col_a2 = st.columns([3, 1.2])
    with col_a2:
        ai_in = st.number_input("Allin Input", 1.0, 1000.0, max_val/2, label_visibility="collapsed")
    with col_a1:
        # 올인 슬라이더는 대략적인 값
        slider_max = max_val if max_val > 0 else 100.0
        ai_slider = st.slider("Allin Slider", 1.0, slider_max, ai_in, label_visibility="collapsed")
    
    raise_amt = ai_in if ai_in != (max_val/2) else ai_slider # 간이 동기화

st.divider()

# [3] Hand: Slider + Selectbox Sync
st.markdown('<p class="big-font">🃏 My Hand</p>', unsafe_allow_html=True)
c1_col, c2_col, s_col = st.columns([2.5, 2.5, 1.5])

# Card 1 Sync
with c1_col:
    st.caption("Card 1")
    # 입력창 (위)
    c1_box = st.selectbox("C1 Box", cards, index=cards.index(st.session_state.get('c1_val', 'A')), label_visibility="collapsed", key="c1_box")
    # 슬라이더 (아래)
    c1_slider = st.select_slider("C1 Slider", cards, value=c1_box, label_visibility="collapsed", key="c1_slider")
    # 값 동기화 확인
    if c1_box != st.session_state.get('c1_val', 'A'):
        st.session_state.c1_val = c1_box
        st.rerun()
    elif c1_slider != st.session_state.get('c1_val', 'A'):
        st.session_state.c1_val = c1_slider
        st.rerun()
    v1 = st.session_state.c1_val

# Card 2 Sync
with c2_col:
    st.caption("Card 2")
    c2_box = st.selectbox("C2 Box", cards, index=cards.index(st.session_state.get('c2_val', 'K')), label_visibility="collapsed", key="c2_box")
    c2_slider = st.select_slider("C2 Slider", cards, value=c2_box, label_visibility="collapsed", key="c2_slider")
    
    if c2_box != st.session_state.get('c2_val', 'K'):
        st.session_state.c2_val = c2_box
        st.rerun()
    elif c2_slider != st.session_state.get('c2_val', 'K'):
        st.session_state.c2_val = c2_slider
        st.rerun()
    v2 = st.session_state.c2_val

with s_col:
    st.caption("Suit")
    # 공간 절약을 위해 Radio 유지
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
# 마지막 선택된 값을 로직에 전달
action_type, msg = calculate_logic(mode, env, pos_box, v1, v2, suit, action, my_stack, eff_stack, raise_amt, int(total_entries))

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
