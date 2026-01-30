import streamlit as st
import pandas as pd

# 1. 앱 기본 설정
st.set_page_config(page_title="JM HOLDEM LEGEND 03 V1", page_icon="🃏", layout="centered")

# CSS: 모바일 터치 최적화 (버튼 크기 확대)
st.markdown("""
    <style>
    /* 사이드바 스타일 */
    [data-testid="stSidebar"] { background-color: #0e1117; border-right: 3px solid #ff4b4b; }
    
    /* 명언 박스 */
    .quote-box { 
        background-color: #1e1e1e; color: #ff4b4b; padding: 10px; border-radius: 10px; 
        border: 2px solid #ff4b4b; text-align: center; font-weight: bold; margin-bottom: 10px; font-size: 0.9em;
    }
    
    /* 모바일 터치 영역 확대 */
    div[data-baseweb="slider"] { margin-bottom: 15px; }
    div[role="radiogroup"] { gap: 10px; }
    div.stButton > button { width: 100%; height: 60px; font-weight: bold; font-size: 1.2em; border-radius: 12px; }
    
    /* 폰트 가독성 */
    .big-font { font-size: 1.2em; font-weight: bold; color: #eee; }
    .highlight { color: #ff4b4b; }
    
    /* 하단 차트 스타일 */
    .card-detail {
        background-color: #262626; border: 1px solid #444; padding: 5px; 
        border-radius: 5px; margin-bottom: 5px; color: #eee; font-size: 0.8em; text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# --- 사용설명서 팝업 ---
@st.dialog("📖 매뉴얼 (Mobile ver.)")
def show_manual():
    st.markdown("""
    ### ⚡ Speed Input Guide
    1. **슬라이더(Slider)**: 드롭다운 대신 슬라이더를 사용합니다. 엄지로 좌우로 밀어서 선택하세요.
    2. **입력 최소화**: 키보드 사용을 원천 차단했습니다. 터치만 하세요.
    3. **토너먼트**: 최소 인원이 5명으로 고정됩니다.
    
    ### 🛡️ Mental Guard
    > **"한번 우승했다고 우쭐대지마라"**
    """)

# --- 메인 상단 CBJ 명언 ---
st.markdown('<div class="quote-box">"한번 우승했다고 우쭐대지마라 그게 나락으로 가는 지름길이다"</div>', unsafe_allow_html=True)

st.title("🛡️ JM LEGEND 03 (Mobile)")

# --- 2. 사이드바 (설정: 게임 전 한 번만 세팅) ---
with st.sidebar:
    st.header("⚙️ Game Setup")
    if st.button("📖 매뉴얼 확인"):
        show_manual()
        
    mode = st.radio("Mode", ["Cash Game", "Tournament"], index=1)
    
    # [수정] 토너먼트 최소 인원 5인 고정
    min_p = 5 if mode == "Tournament" else 2
    
    env_options = ["Online", "Live Pub", "Competition"]
    env = st.selectbox("Env", env_options, index=1)
    
    if mode == "Tournament":
        total_entries = st.number_input("Entries", 10, 10000, 100)
    else:
        total_entries = 0

    h_in = st.number_input("Players", min_p, 9, 9) # 최소값 적용
    
    st.markdown("---")
    st.header("💰 Stack (BB)")
    my_stack = st.number_input("My BB", 1, 1000, 50)
    villain_stack = st.number_input("Villain BB", 1, 1000, 50)
    eff_stack = min(my_stack, villain_stack)
    st.metric("Eff. Stack", f"{eff_stack} BB")

# --- 3. 메인 화면 (스피드 입력 인터페이스) ---
# 드롭다운(Selectbox)을 모두 슬라이더(SelectSlider)와 라디오(Radio)로 교체

st.markdown('<p class="big-font">📍 My Position</p>', unsafe_allow_html=True)
# [Speed] 엄지로 밀어서 포지션 선택
pos_list = ["UTG", "UTG+1", "MP", "LJ", "HJ", "CO", "BTN", "SB", "BB"]
pos = st.select_slider("Position Slider", options=pos_list, value="BTN", label_visibility="collapsed")

st.markdown('<p class="big-font">⚔️ Action & Raise</p>', unsafe_allow_html=True)
# [Speed] 탭 한 번으로 상황 선택
action = st.radio("Action", ["Unopened", "Facing Raise", "Facing All-in"], horizontal=True, label_visibility="collapsed")

raise_amt = 0.0
if action == "Facing Raise":
    # [Speed] 키보드 없이 슬라이더로 금액 조절 (2BB ~ 10BB)
    raise_amt = st.slider("Opponent Raise (BB)", 2.0, 10.0, 2.5, 0.5)
    if raise_amt >= 6.0: st.caption("⚠️ Big Raise Detected")
elif action == "Facing All-in":
    # [Speed] 올인 금액도 대략적으로 슬라이더로 (세밀한건 사이드바, 급할 땐 슬라이더)
    max_val = float(villain_stack)
    raise_amt = st.slider("All-in Amount (BB)", 1.0, max_val, max_val/2)

st.divider()

st.markdown('<p class="big-font">🃏 My Hand</p>', unsafe_allow_html=True)
# [Speed] 카드 선택도 슬라이더로 (A ~ 2)
cards = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]
c1_col, c2_col, s_col = st.columns([3, 3, 2])

with c1_col:
    st.caption("Card 1")
    v1 = st.select_slider("C1", options=cards, value="A", label_visibility="collapsed")
with c2_col:
    st.caption("Card 2")
    v2 = st.select_slider("C2", options=cards, value="K", label_visibility="collapsed")
with s_col:
    st.caption("Suit")
    # [Speed] 토글 방식
    suit_select = st.radio("Suit", ["s", "o"], horizontal=True, label_visibility="collapsed")
    suit = "s" if suit_select == "s" else "o"

# --- 5. LOGIC ENGINE (로직 동일 유지) ---
def calculate_logic(mode, env, pos, v1, v2, suit, act, hero_stack, eff_stack, amt, entries):
    rank_map = {"A":14, "K":13, "Q":12, "J":11, "T":10, "9":9, "8":8, "7":7, "6":6, "5":5, "4":4, "3":3, "2":2}
    r1, r2 = rank_map[v1], rank_map[v2]
    if r1 < r2: v1, v2, r1, r2 = v2, v1, r2, r1
    is_pair = (v1 == v2)
    is_s = (suit == "s")
    hand_str = f"{v1}{v2}{suit}" if not is_pair else f"{v1}{v2}"
    
    # [PREMIUMS]
    if hand_str in ["AA", "KK", "QQ", "AKs", "AKo"]:
        if act == "Facing All-in": return "🔴 SNAP CALL", "지구상 최강. 무조건 콜."
        if act == "Facing Raise": return "🔥 3-BET", "무조건 밸류 3-벳."
        return "🔴 RAISE", "무조건 오픈."

    # [BB DEFENSE FIX]
    if act == "Facing Raise" and pos == "BB":
        if amt >= 6.0:
            if hand_str in ["JJ", "TT", "99", "AQs", "AJs"]: return "⚔️ CALL", "빅 오픈 방어."
            return "🔵 FOLD", "사이즈가 너무 큼."
        elif amt >= 4.0:
            if is_pair and r1 >= 7: return "🟢 CALL", "중간 페어 방어."
            if is_s and r1 >= 11: return "🟢 CALL", "수딧 브로드웨이."
            if not is_s and r1 >= 13 and r2 >= 10: return "🟢 CALL", "AQ/KQ 방어."
            return "🔵 FOLD", "타이트 방어."
        else:
            if is_pair or is_s: return "🟢 DEFEND", "BB 배당 방어."
            if r1 + r2 >= 19: return "🟢 DEFEND", "커넥터 방어."
            return "🔵 FOLD", "Trash Fold."

    # [CASH]
    if mode == "Cash Game":
        if act == "Facing Raise":
            if is_pair and r1 < 10:
                if (eff_stack / amt) >= 20: return "🟢 CALL (Set)", "셋마이닝 배당 충족."
                else: return "🔵 FOLD", "배당 부족."
            if "Live" in env and is_s and (r1-r2 == 1) and r1 < 12 and pos in ["BTN", "CO"]:
                return "🟢 CALL", "라이브펍 수딧 콜."

    # [TOURNAMENT]
    else:
        is_competition = (env == "Competition")
        if act == "Facing All-in":
            risk_life = (hero_stack <= amt) or (hero_stack <= eff_stack)
            if risk_life:
                if hand_str in ["JJ", "AQs"]: return "⚔️ CALL", "승부."
                if hand_str in ["TT", "99", "88"]: return "🔵 FOLD", "생존 우선."
            else:
                if hand_str in ["JJ", "TT", "99", "AQ"]: return "🟢 CALL", "Bully."

        if hero_stack <= 15 and act == "Unopened":
             if is_pair or r1 >= 10 or (is_s and r1 >= 8): return "🚀 JAM", "15BB 잼."

    # [RFI]
    if act == "Unopened":
        if pos == "BB": return "🎉 WALK", "승리"
        if is_pair and r1 >= 7: return "🟠 OPEN", "정석 오픈"
        if r1 >= 11: return "🟠 OPEN", "하이카드"
        if pos in ["BTN", "CO"] and is_s: return "🟠 OPEN", "스틸"

    return "🔵 FOLD", "EV -"

# --- 6. 결과 출력 ---
st.divider()
decision, reasoning = calculate_logic(mode, env, pos, v1, v2, suit, action, my_stack, eff_stack, raise_amt, int(total_entries))

if "FOLD" in decision: st.info(f"## {decision}")
elif "CALL" in decision or "DEFEND" in decision: st.warning(f"## {decision}")
else: st.error(f"## {decision}")

st.caption(f"💡 {reasoning}")

# --- 7. 하단 고정 차트 (모바일용 간소화) ---
st.markdown("---")
st.markdown("**🚀 Short Stack (20BB↓)**")
st.table(pd.DataFrame({
    "Pos": ["UTG", "CO", "BTN", "SB"],
    "Push": ["77+, AJs+", "22+, A8o+", "Any Pair/Ax", "Any Pair/Ax"]
}))
