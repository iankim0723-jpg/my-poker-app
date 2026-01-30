import streamlit as st
import pandas as pd

# 1. 앱 기본 설정
st.set_page_config(page_title="JM HOLDEM LEGEND 03 V1", page_icon="🃏", layout="centered")

# CSS: 디자인 및 가독성 (고정표 스타일 포함)
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

# --- [기능 추가] 사용설명서 팝업 함수 ---
@st.dialog("📖 JM HOLDEM LEGEND 03 V1 매뉴얼")
def show_manual():
    st.markdown("""
    ### 1. 🛡️ Mental Guard (핵심 철학)
    > **"한번 우승했다고 우쭐대지마라 그게 나락으로 가는 지름길이다"**
    
    이 앱은 단순한 계산기가 아니라, **CBJ님의 우승 마인드**를 유지하는 멘탈 가드 시스템입니다. 자만심을 버리고 기계적인 판단을 내리세요.

    ---
    ### 2. 🏆 Game Mode (모드별 전략)
    **🔴 Cash Game (Deep Stack)**
    * **목표**: 빅이닝(Big Inning) & 내재 배당 극대화
    * **핵심**: 셋마이닝, 수딧 커넥터 콜, 3-Bet 위주 운영 (레이크 방어)
    
    **🔵 Tournament (Survival)**
    * **목표**: 생존(One Life) & 칩 가치(ICM) 보존
    * **핵심**: 숏스택(15BB↓) 푸쉬, 앤티 스틸, 리스크 관리(코인플립 회피)

    ---
    ### 3. ⚙️ 입력 가이드
    1.  **Effective Stack (유효 스택)**: 내 스택과 상대 스택 중 **더 적은 쪽**을 기준으로 전략을 계산합니다.
    2.  **Villain Info**: 상대가 올인했을 때, 내 스택 대비 부담(%)을 계산하여 **배당 콜(Snap Call)** 여부를 알려줍니다.
    3.  **Position**: BTN(버튼), SB, BB 등 포지션을 정확히 선택해야 GTO 차트가 작동합니다.

    ---
    ### 4. 📊 결과 해석
    * **🔴 RAISE / SNAP CALL**: GTO 필수 액션. 무조건 실행.
    * **🟠 OPEN / CALL**: 수익성 있는 구간. 실행 권장.
    * **🔵 FOLD**: 수학적으로 손해. 과감히 포기.
    
    ---
    *Developed by JM Holdem Team*
    """)

# --- 메인 상단 CBJ 명언 ---
st.markdown('<div class="quote-box">"한번 우승했다고 우쭐대지마라 그게 나락으로 가는 지름길이다"<br><small style="color: #ccc;">- 더홀릭 우승 경험자 CBJ -</small></div>', unsafe_allow_html=True)

st.title("🛡️ JM HOLDEM LEGEND 03 V1")
st.caption("⚡ Advanced Logic + Fixed GTO Charts")

# --- 2. 사이드바 (설명서 버튼 추가됨) ---
with st.sidebar:
    st.header("📸 Card Scanner")
    st.camera_input("Scan cards", label_visibility="collapsed")
    st.markdown("---")
    
    # [추가] 사용설명서 버튼
    if st.button("📖 사용설명서 (Manual)", use_container_width=True):
        show_manual()
        
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
    st.header("⚙️ Table Setup")
    h_in = st.number_input("Players", 2, 9, 9)

# --- 3. 메인 화면 (플레이어 입력 영역) ---
st.markdown("### 1. Position & Situation")

pos_list = ["UTG", "UTG+1", "MP", "LJ", "HJ", "CO", "BTN", "SB", "BB"]
pos = st.selectbox("📍 Select My Position", pos_list, index=6)

action = st.radio("⚔️ Opponent Action", ["Unopened (RFI)", "Facing Raise", "Facing All-in"], horizontal=True)

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

# --- 5. DEEP LOGIC ENGINE ---
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
        if act == "Facing Raise" and is_pair and r1 < 10: 
            call_cost = amt
            implied_odds = eff_stack / call_cost
            if implied_odds >= 20: return "🟢 CALL (Set Mine)", f"배당 {implied_odds:.1f}배 충족. 셋 맞추러 갑니다."
            else: return "🔵 FOLD", "배당 부족. 못 먹습니다."
        if act == "Facing Raise" and is_s and (r1 - r2 == 1) and r1 < 12:
            if pos in ["BTN", "CO"]: return "🟢 CALL", "IP에서 딥스택 활용."
            return "🔵 FOLD", "아웃포지션 투기 금지."

    # [LOGIC B] TOURNAMENT
    else:
        is_risk_life = (hero_stack < amt) or (act == "Facing All-in" and hero_stack <= eff_stack)
        if act == "Facing All-in":
            if is_risk_life: 
                if hand_str in ["JJ", "AQs"]: return "⚔️ CALL", "탈락 감수하고 승부."
                if hand_str in ["TT", "99", "88"]: return "🔵 TIGHT FOLD", "목숨이 하나입니다. 코인플립 회피."
            else: 
                if hand_str in ["JJ", "TT", "99", "AQ"]: return "🟢 CALL", "상대 탈락 유도 (Chip Bully)."
        
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
decision, reasoning = advanced_logic(mode, pos, v1, v2, suit, action, my_stack, eff_stack, raise_amt, int(h_in))

if "FOLD" in decision: st.info(f"## {decision}")
elif "CALL" in decision or "DEFEND" in decision: st.warning(f"## {decision}")
else: st.error(f"## {decision}")

st.markdown(f"""
<div class="metric-box">
    <strong>🧠 Deep Analysis</strong><br>
    <span class="logic-tag {'tag-cash' if 'Cash' in mode else 'tag-mtt'}">{mode}</span>
    Effective Stack: {eff_stack}BB | Position: {pos}<br>
    <em>"{reasoning}"</em>
</div>
""", unsafe_allow_html=True)

# --- 7. 하단 고정 차트 ---
st.markdown("---")
st.markdown("### 🚀 Short Stack Push Range (10-20BB)")
st.caption("※ 모드와 상관없이 숏스택(20BB↓) 상황 발생 시 참고하세요.")
st.table(pd.DataFrame({
    "Position": ["UTG", "HJ", "CO", "BTN", "SB"],
    "Push Range": ["77+, AJs+, AQo+", "55+, A9s+, AJo+", "22+, A2s+, A8o+", "Any Pair, Any Ax, Kx", "Any Pair, Any Ax, Q5s+"]
}))

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
