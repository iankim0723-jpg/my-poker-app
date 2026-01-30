import streamlit as st
import pandas as pd

# 1. 앱 기본 설정
st.set_page_config(page_title="JM HOLDEM LEGEND 03 V1", page_icon="🃏", layout="centered")

# CSS: 디자인 고정 (변동 없음)
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #0e1117; border-right: 3px solid #ff4b4b; }
    .quote-box { 
        background-color: #1e1e1e; color: #ff4b4b; padding: 15px; border-radius: 10px; 
        border: 2px solid #ff4b4b; text-align: center; font-weight: bold; margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.5);
    }
    .metric-box { 
        background: #222; border: 1px solid #444; padding: 12px; border-radius: 8px; 
        color: #eee; margin-top: 10px; text-align: center;
    }
    .card-detail {
        background-color: #262626; border: 1px solid #444; padding: 10px; 
        border-radius: 8px; margin-bottom: 8px; color: #eee;
    }
    .pos-title { color: #ff4b4b; font-weight: bold; font-size: 1.1em; }
    .logic-tag { display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; margin-right: 5px; }
    .tag-cash { background-color: #28a745; color: white; }
    .tag-mtt { background-color: #007bff; color: white; }
    div.stButton > button { width: 100%; height: 50px; font-weight: bold; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# --- 사용설명서 팝업 ---
@st.dialog("📖 JM HOLDEM LEGEND 03 V1 매뉴얼")
def show_manual():
    st.markdown("""
    ### 🛡️ Mental Guard
    > **"한번 우승했다고 우쭐대지마라 그게 나락으로 가는 지름길이다"**
    
    ### ⚙️ 로직 변경 사항 (v3.1)
    1. **BB 방어 최적화**: 상대 레이즈 사이즈(BB)에 따라 방어 범위가 달라집니다. (6BB 오픈 시 타이트하게 폴드)
    2. **환경 세분화**: 온라인 / 라이브 펍 / 대회(Competition) 환경 반영.
    3. **토너먼트 인원**: 총 참가자 수에 따라 생존 압박감(ICM) 자동 조정.
    
    ### 📊 결과 가이드
    * **🔴 RAISE / SNAP CALL**: 필수 액션.
    * **🟠 OPEN / CALL**: 수익 구간.
    * **🔵 FOLD**: EV 마이너스 구간.
    """)

# --- 메인 상단 CBJ 명언 ---
st.markdown('<div class="quote-box">"한번 우승했다고 우쭐대지마라 그게 나락으로 가는 지름길이다"<br><small style="color: #ccc;">- 더홀릭 우승 경험자 CBJ -</small></div>', unsafe_allow_html=True)

st.title("🛡️ JM HOLDEM LEGEND 03 V1")
st.caption("⚡ Advanced Logic + Dynamic BB Defense")

# --- 2. 사이드바 (환경 설정 업그레이드) ---
with st.sidebar:
    st.header("📸 Card Scanner")
    st.camera_input("Scan cards", label_visibility="collapsed")
    st.markdown("---")
    
    if st.button("📖 사용설명서 (Manual)", use_container_width=True):
        show_manual()
        
    st.markdown("---")
    
    st.header("🏆 Game Mode & Environment")
    mode = st.radio("Select Strategy", ["Cash Game (Ring)", "Tournament (MTT)"])
    
    # [수정] 환경 설정 세분화
    env_options = ["Online (Standard)", "Live Pub (Loose/Aggressive)", "Competition (Official)"]
    env = st.selectbox("Play Environment", env_options)
    
    # [추가] 토너먼트일 경우 총 참가 인원 입력
    total_entries = 0
    if mode == "Tournament (MTT)":
        total_entries = st.number_input("Total Participants (총 참가자)", 10, 10000, 100)
        st.caption(f"🏁 경기 규모: {total_entries}명")

    st.markdown("---")
    st.header("💰 Stack Dynamics")
    my_stack = st.number_input("My Stack (BB)", 1, 1000, 100)
    villain_stack = st.number_input("Villain Stack (BB)", 1, 1000, 100)
    eff_stack = min(my_stack, villain_stack)
    st.metric(label="Effective Stack (유효 스택)", value=f"{eff_stack} BB")
    
    st.markdown("---")
    st.header("⚙️ Table Setup")
    h_in = st.number_input("Players", 2, 9, 9)

# --- 3. 메인 화면 (상황 입력) ---
st.markdown("### 1. Position & Situation")

pos_list = ["UTG", "UTG+1", "MP", "LJ", "HJ", "CO", "BTN", "SB", "BB"]
pos = st.selectbox("📍 Select My Position", pos_list, index=6)

action = st.radio("⚔️ Opponent Action", ["Unopened (RFI)", "Facing Raise", "Facing All-in"], horizontal=True)

raise_amt = 0.0
# [중요] 레이즈 금액 입력 로직 강화
if action == "Facing Raise":
    raise_amt = st.number_input("Opponent Raise Amount (BB)", 2.0, 100.0, 2.5, step=0.5)
    if raise_amt >= 6.0:
        st.error(f"⚠️ Warning: 상대가 {raise_amt}BB 빅 오픈을 했습니다. 방어 범위를 극도로 좁힙니다.")
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

# --- 5. LOGIC ENGINE (BB 방어 로직 수정됨) ---
def calculate_logic(mode, env, pos, v1, v2, suit, act, hero_stack, eff_stack, amt, entries):
    rank_map = {"A":14, "K":13, "Q":12, "J":11, "T":10, "9":9, "8":8, "7":7, "6":6, "5":5, "4":4, "3":3, "2":2}
    r1, r2 = rank_map[v1], rank_map[v2]
    if r1 < r2: v1, v2, r1, r2 = v2, v1, r2, r1
    is_pair = (v1 == v2)
    is_s = (suit == "s")
    hand_str = f"{v1}{v2}{suit}" if not is_pair else f"{v1}{v2}"
    
    # [PREMIUMS] 절대 방어 (사이즈 무관)
    if hand_str in ["AA", "KK", "QQ", "AKs", "AKo"]:
        if act == "Facing All-in": return "🔴 SNAP CALL", "지구상 최강 핸드. 무조건 콜."
        if act == "Facing Raise": return "🔥 3-BET", "어떤 사이즈든 밸류 3-벳."
        return "🔴 RAISE", "무조건 오픈."

    # ----------------------------------------------------------------
    # [LOGIC FIX] BB Defense Logic (레이즈 사이즈 반영)
    # ----------------------------------------------------------------
    if act == "Facing Raise" and pos == "BB":
        # 1. 6BB 이상 빅 오픈 -> 극도로 타이트 (프리미엄만 방어)
        if amt >= 6.0:
            if hand_str in ["JJ", "TT", "99", "AQs", "AJs", "KQs"]: return "⚔️ CALL/3-BET", "빅 오픈에는 상위 레인지로만 방어."
            return "🔵 FOLD", f"상대 {amt}BB 오픈은 너무 큽니다. 배당이 안 나옵니다."
            
        # 2. 4BB ~ 5.9BB 오픈 -> 타이트 방어
        elif amt >= 4.0:
            if is_pair and r1 >= 7: return "🟢 CALL", "중간 페어 이상 방어."
            if is_s and r1 >= 11: return "🟢 CALL", "수딧 브로드웨이 방어."
            if not is_s and r1 >= 13 and r2 >= 10: return "🟢 CALL", "강한 오프수딧(AQ, KQ) 방어."
            return "🔵 FOLD", "4BB 이상 오픈에 약한 핸드 방어 금지."
            
        # 3. 2BB ~ 3.5BB (Standard) -> 넓은 GTO 방어
        else:
            if is_pair: return "🟢 DEFEND", "BB 배당 방어 (Any Pair)."
            if is_s: return "🟢 DEFEND", "BB 배당 방어 (Any Suited)."
            if r1 + r2 >= 19: return "🟢 DEFEND", "커넥터/브로드웨이 방어."
            return "🔵 FOLD", "쓰레기 핸드는 버리세요."

    # ----------------------------------------------------------------
    # [LOGIC A] CASH GAME
    # ----------------------------------------------------------------
    if "Cash" in mode:
        if act == "Facing Raise":
            # 셋마이닝 (20배 법칙)
            if is_pair and r1 < 10:
                implied_odds = eff_stack / amt
                if implied_odds >= 20: return "🟢 CALL (Set Mine)", f"배당 {implied_odds:.1f}배 충족."
                else: return "🔵 FOLD", "배당 부족."
            # 수딧 커넥터 (라이브 펍 보정: 루즈하게)
            if "Live Pub" in env and is_s and (r1-r2 == 1) and r1 < 12 and pos in ["BTN", "CO"]:
                return "🟢 CALL", "라이브 펍 특성상 멀티웨이 팟 노리기."
                
    # ----------------------------------------------------------------
    # [LOGIC B] TOURNAMENT
    # ----------------------------------------------------------------
    else: # Tournament
        # 대회(Competition) 환경 보정: 더 타이트하게
        survival_factor = 1.2 if "Competition" in env else 1.0
        
        if act == "Facing All-in":
            # 내가 칩이 적거나 비슷할 때 (탈락 위험)
            risk_life = (hero_stack <= amt) or (hero_stack <= eff_stack)
            if risk_life:
                if hand_str in ["JJ", "AQs"]: return "⚔️ CALL", "승부 볼 만한 핸드."
                if hand_str in ["TT", "99", "88"]: 
                    return "🔵 TIGHT FOLD", "대회 생존 우선. 코인플립 회피."
            else: # Bully (상대 탈락 유도)
                if hand_str in ["JJ", "TT", "99", "AQ"]: return "🟢 CALL", "칩 우위 활용."

        # 숏스택 잼 (15BB 이하)
        if hero_stack <= 15 and act == "Unopened (RFI)":
             if is_pair or r1 >= 10 or (is_s and r1 >= 8): return "🚀 JAM (ALL-IN)", "15BB 이하 승부."

    # [LOGIC C] 기본 RFI
    if act == "Unopened (RFI)":
        if pos == "BB": return "🎉 WALK", "승리"
        if is_pair and r1 >= 7: return "🟠 OPEN", "정석 오픈"
        if r1 >= 11: return "🟠 OPEN", "하이카드 오픈"
        if pos in ["BTN", "CO"] and is_s: return "🟠 OPEN", "포지션 스틸"

    return "🔵 FOLD", "EV 마이너스 구간"

# --- 6. 실행 및 출력 ---
st.divider()

# 로직 실행
decision, reasoning = calculate_logic(mode, env, pos, v1, v2, suit, action, my_stack, eff_stack, raise_amt, int(total_entries))

# 스타일링 출력
if "FOLD" in decision: st.info(f"## {decision}")
elif "CALL" in decision or "DEFEND" in decision: st.warning(f"## {decision}")
else: st.error(f"## {decision}")

# 분석 박스
st.markdown(f"""
<div class="metric-box">
    <strong>🧠 Analysis</strong><br>
    <span class="logic-tag {'tag-cash' if 'Cash' in mode else 'tag-mtt'}">{mode}</span>
    Environment: {env}<br>
    Raise Amount: {raise_amt}BB | Position: {pos}<br>
    <em>"{reasoning}"</em>
</div>
""", unsafe_allow_html=True)

# --- 7. 하단 고정 차트 ---
st.markdown("---")
st.markdown("### 🚀 Short Stack Push Range (10-20BB)")
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
