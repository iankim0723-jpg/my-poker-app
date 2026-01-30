import streamlit as st
import pandas as pd

# 1. 앱 기본 설정
st.set_page_config(page_title="JM HOLDEM LEGEND 03 V1", page_icon="🃏", layout="centered")

# CSS: UI 디자인 고정 (변동 없음)
st.markdown("""
    <style>
    /* 사이드바 스타일 */
    [data-testid="stSidebar"] { background-color: #0e1117; border-right: 3px solid #ff4b4b; }
    
    /* 명언 박스 */
    .quote-box { 
        background-color: #1e1e1e; color: #ff4b4b; padding: 15px; border-radius: 10px; 
        border: 2px solid #ff4b4b; text-align: center; font-weight: bold; margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.5);
    }
    
    /* 메트릭 박스 */
    .metric-box { 
        background: #222; border: 1px solid #444; padding: 12px; border-radius: 8px; 
        color: #eee; margin-top: 10px; text-align: center;
    }
    
    /* 핸드레인지 상세 카드 (2단 레이아웃용) */
    .card-detail {
        background-color: #262626; border: 1px solid #444; padding: 10px; 
        border-radius: 8px; margin-bottom: 8px; color: #eee;
    }
    .pos-title { color: #ff4b4b; font-weight: bold; font-size: 1.1em; }
    
    /* 태그 스타일 */
    .logic-tag { display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; margin-right: 5px; }
    .tag-cash { background-color: #28a745; color: white; }
    .tag-mtt { background-color: #007bff; color: white; }
    
    div.stButton > button { width: 100%; height: 50px; font-weight: bold; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# --- 메인 상단 CBJ 명언 ---
st.markdown('<div class="quote-box">"한번 우승했다고 우쭐대지마라 그게 나락으로 가는 지름길이다"<br><small style="color: #ccc;">- 더홀릭 우승 경험자 CBJ -</small></div>', unsafe_allow_html=True)

st.title("🛡️ JM HOLDEM LEGEND 03 V1")
st.caption("⚡ Advanced Logic + Fixed GTO Charts")

# --- 2. 사이드바 (설정 UI 고정) ---
with st.sidebar:
    st.header("📸 Card Scanner")
    st.camera_input("Scan cards", label_visibility="collapsed")
    st.markdown("---")
    
    st.header("🏆 Game Mode Strategy")
    mode = st.radio("Select Strategy", ["Cash Game (Deep Stack)", "Tournament (Survival)"])
    
    if "Cash" in mode:
        st.info("💡 **Cash:** 내재 배당 & 빅이닝 중심. 리바이 가능.")
    else:
        st.info("💡 **Tourney:** 생존(One Life) & ICM 중심.")

    st.markdown("---")
    st.header("💰 Stack Dynamics")
    my_stack = st.number_input("My Stack (BB)", 1, 1000, 100)
    villain_stack = st.number_input("Villain Stack (BB)", 1, 1000, 100)
    eff_stack = min(my_stack, villain_stack)
    st.metric(label="Effective Stack (유효 스택)", value=f"{eff_stack} BB")
    
    st.markdown("---")
    st.header("⚙️ Setup")
    pos_list = ["UTG", "UTG+1", "MP", "LJ", "HJ", "CO", "BTN", "SB", "BB"]
    pos = st.selectbox("My Position", pos_list, index=6)
    h_in = st.number_input("Players", 2, 9, 9)

# --- 3. 상황 입력 ---
st.markdown("### 1. Action Context")
action = st.radio("Current Situation", ["Unopened (RFI)", "Facing Raise", "Facing All-in"], horizontal=True)

raise_amt = 0
if action == "Facing Raise":
    raise_amt = st.number_input("Opponent Raise Amount (BB)", 2.0, 100.0, 2.5)
elif action == "Facing All-in":
    raise_amt = st.number_input("Opponent All-in Amount (BB)", 1.0, 1000.0, float(villain_stack))

st.markdown("---")

# --- 4. 핸드 선택 ---
st.markdown("### 2. My Hand")
cards = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]
c1, c2 = st.columns(2)
with c1: v1 = st.selectbox("Card 1", cards, key="v1")
with c2: v2 = st.selectbox("Card 2", cards, index=1, key="v2")
suit = st.radio("Suit", ["s", "o"], horizontal=True)

# --- 5. DEEP LOGIC ENGINE (심화 로직) ---
def advanced_logic(mode, pos, v1, v2, suit, act, hero_stack, eff_stack, amt, players):
    rank_map = {"A":14, "K":13, "Q":12, "J":11, "T":10, "9":9, "8":8, "7":7, "6":6, "5":5, "4":4, "3":3, "2":2}
    r1, r2 = rank_map[v1], rank_map[v2]
    if r1 < r2: v1, v2, r1, r2 = v2, v1, r2, r1
    is_pair = (v1 == v2)
    is_s = (suit == "s")
    hand_str = f"{v1}{v2}{suit}" if not is_pair else f"{v1}{v2}"
    
    # [공통] 절대 방어 (PREMIUMS)
    if hand_str in ["AA", "KK", "QQ", "AKs", "AKo"]:
        if act == "Facing All-in": return "🔴 SNAP CALL", "지구상 최강 핸드. 무조건 콜."
        if act == "Facing Raise": return "🔥 3-BET", "무조건 밸류 3-벳."
        return "🔴 RAISE", "무조건 오픈."

    # [LOGIC A] CASH GAME
    if "Cash" in mode:
        if act == "Facing Raise" and is_pair and r1 < 10: # 셋마이닝
            call_cost = amt
            implied_odds = eff_stack / call_cost
            if implied_odds >= 20: return "🟢 CALL (Set Mine)", f"배당 {implied_odds:.1f}배 충족. 셋 맞추러 갑니다."
            else: return "🔵 FOLD", "배당 부족. 못 먹습니다."
        if act == "Facing Raise" and is_s and (r1 - r2 == 1) and r1 < 12: # 수딧 커넥터
            if pos in ["BTN", "CO"]: return "🟢 CALL", "IP에서 딥스택 활용."
            return "🔵 FOLD", "아웃포지션 투기 금지."

    # [LOGIC B] TOURNAMENT
    else:
        is_risk_life = (hero_stack < amt) or (act == "Facing All-in" and hero_stack <= eff_stack)
        if act == "Facing All-in":
            # 칩 깡패 모드 vs 생존 모드
            if is_risk_life: # 지면 탈락
                if hand_str in ["JJ", "AQs"]: return "⚔️ CALL", "탈락 감수하고 승부."
                if hand_str in ["TT", "99", "88"]: return "🔵 TIGHT FOLD", "목숨이 하나입니다. 코인플립 회피."
            else: # 내가 칩이 더 많음 (Bully)
                if hand_str in ["JJ", "TT", "99", "AQ"]: return "🟢 CALL", "상대 탈락 유도 (Chip Bully)."
        
        # 숏스택 잼 (15BB 이하)
        if hero_stack <= 15 and act == "Unopened (RFI)":
            if is_pair or r1 >= 10 or (is_s and r1 >= 8): return "🚀 JAM (ALL-IN)", "15BB 이하: 앉아서 죽지 말고 승부."
    
    # [LOGIC C] 기본 GTO Fallback
    if act == "Unopened (RFI)":
        if pos == "BB": return "🎉 WALK", "블라인드 획득"
        if is_pair and r1 >= 7: return "🟠 OPEN", "정석 오픈"
        if r1 >= 11: return "🟠 OPEN", "하이카드 오픈"
        if pos in ["BTN", "CO"] and is_s: return "🟠 OPEN", "포지션 스틸"
    
    if act == "Facing Raise":
        if pos == "BB": 
            if is_pair or is_s or r1 >= 10: return "🟢 DEFEND", "BB 방어 의무"
        if hand_str in ["JJ", "TT", "AQs", "AJs"]: return "⚔️ CALL/3-BET", "상황에 따라 운영"

    return "🔵 FOLD", "EV 마이너스"

# --- 6. 실행 및 출력 ---
st.divider()

# 로직 실행
decision, reasoning = advanced_logic(mode, pos, v1, v2, suit, action, my_stack, eff_stack, raise_amt, int(h_in))

# 스타일링 출력
if "FOLD" in decision: st.info(f"## {decision}")
elif "CALL" in decision or "DEFEND" in decision: st.warning(f"## {decision}")
else: st.error(f"## {decision}")

# 심화 분석 박스
st.markdown(f"""
<div class="metric-box">
    <strong>🧠 Deep Analysis</strong><br>
    <span class="logic-tag {'tag-cash' if 'Cash' in mode else 'tag-mtt'}">{mode}</span>
    Effective Stack: {eff_stack}BB | Position: {pos}<br>
    <em>"{reasoning}"</em>
</div>
""", unsafe_allow_html=True)

# --- 7. 하단 고정 차트 (무조건 표시) ---
st.markdown("---")
# [1] 숏스택 올인표
st.markdown("### 🚀 Short Stack Push Range (10-20BB)")
st.caption("※ 모드와 상관없이 숏스택(20BB↓) 상황 발생 시 참고하세요.")
st.table(pd.DataFrame({
    "Position": ["UTG", "HJ", "CO", "BTN", "SB"],
    "Push Range": ["77+, AJs+, AQo+", "55+, A9s+, AJo+", "22+, A2s+, A8o+", "Any Pair, Any Ax, Kx", "Any Pair, Any Ax, Q5s+"]
}))

# [2] 핸드레인지 상세표 (2단)
st.markdown("### 📊 RFI Position Range Detail")
col1, col2 = st.columns(2)
stats_detail = {"UTG":"14%", "UTG+1":"16%", "MP":"19%", "LJ":"21%", "HJ":"24%", "CO":"30%", "BTN":"48%", "SB":"42%"}
p_keys = list(stats_detail.keys())

with col1:
    for k in p_keys[:4]:
        st.markdown(f'<div class="card-detail"><span class="pos-title">{k} ({stats_detail[k]})</span><br><small>Standard Open</small></div>', unsafe_allow_html=True)
with col2:
    for k in p_keys[4:]:
        st.markdown(f'<div class="card-detail"><span class="pos-title">{k} ({stats_detail[k]})</span><br><small>Standard Open</small></div>', unsafe_allow_html=True)
