import streamlit as st
import pandas as pd

# 1. 앱 설정
st.set_page_config(page_title="JM HOLDEM LEGEND 03 V1", page_icon="🃏", layout="centered")

# CSS: 디자인 및 가독성 (사이드바 강조 + 2단 테이블 + 명언 박스)
st.markdown("""
    <style>
    /* 사이드바 스타일 */
    [data-testid="stSidebar"] { background-color: #0e1117; border-right: 3px solid #ff4b4b; }
    
    /* 명언 박스 */
    .quote-box { 
        background-color: #1e1e1e; color: #ff4b4b; padding: 15px; border-radius: 10px; 
        border: 2px solid #ff4b4b; text-align: center; font-weight: bold; margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    /* 카드 디테일 박스 */
    .card-detail {
        background-color: #262626; border: 1px solid #444; padding: 10px; 
        border-radius: 8px; margin-bottom: 8px; color: #eee;
    }
    .pos-title { color: #ff4b4b; font-weight: bold; }
    
    /* 버튼 및 메트릭 박스 */
    div.stButton > button { width: 100%; height: 45px; font-weight: bold; border-radius: 8px; }
    .metric-box { text-align: center; border: 1px solid #555; padding: 10px; border-radius: 5px; background: #222; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

# --- 메인 상단 CBJ 명언 ---
st.markdown('<div class="quote-box">"한번 우승했다고 우쭐대지마라 그게 나락으로 가는 지름길이다"<br><small style="color: #ccc;">- 더홀릭 우승 경험자 CBJ -</small></div>', unsafe_allow_html=True)

st.title("🛡️ JM HOLDEM LEGEND 03 V1")

# --- 2. 사이드바 (설정) ---
with st.sidebar:
    st.header("📸 Card Scanner")
    st.camera_input("Scan cards", label_visibility="collapsed")
    st.markdown("---")
    
    st.header("🏆 Game Mode")
    # 캐시게임 vs 토너먼트 모드 분리
    game_mode = st.radio("Select Mode", ["Cash Game (Ring)", "Tournament (MTT)"])
    
    if game_mode == "Cash Game (Ring)":
        env = st.selectbox("Field Type", ["Online (Standard)", "Live Pub (Deep Stack)"])
    else:
        env = st.selectbox("Stage", ["Early Stage", "Middle Stage", "Bubble / ICM", "Final Table"])

    st.markdown("---")
    st.header("⚙️ Table Setup")
    h_in = st.number_input("Players", 2, 9, 9)
    handy = st.slider("Active Players", 2, 9, int(h_in))
    
    st.markdown("---")
    st.header("👤 Hero Style")
    hero_style = st.select_slider("My Image", options=["Nits", "Tight", "Standard", "Loose", "Maniac"], value="Standard")
    
    st.markdown("---")
    st.header("💰 Hero Stack")
    s_in = st.number_input("My Stack (BB)", 1, 1000, 120)
    my_stack = st.select_slider("Adjust My BB", options=list(range(5, 1001, 5)), value=int(s_in) if s_in <= 1000 else 100)

# --- 3. 상황 및 포지션 ---
st.markdown("### 1. Situation & Position")
pos_list = ["UTG", "UTG+1", "MP", "LJ", "HJ", "CO", "BTN", "SB", "BB"]
pos = st.selectbox("Position", pos_list, index=6)

action_options = ["Unopened (RFI)", "Facing Raise", "Facing All-in"]
action = st.radio("Opponent Action", action_options, horizontal=True)

# [기능] Facing All-in 선택 시 상대 스택 입력 활성화 (배당 계산용)
villain_bb = 0
if action == "Facing All-in":
    st.markdown("#### 🚨 Villain Info")
    villain_bb = st.number_input("상대방 올인 금액 (Villain All-in BB)", min_value=1, max_value=1000, value=10)
    risk_ratio = (villain_bb / my_stack) * 100
    st.caption(f"내 스택({my_stack}BB) 대비 위험 부담: **{risk_ratio:.1f}%**")

st.markdown("---")

# --- 4. 핸드 선택 ---
st.markdown("### 2. My Hand")
cards = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]
c1, c2 = st.columns(2)
with c1: v1 = st.selectbox("Card 1", cards, key="v1")
with c2: v2 = st.selectbox("Card 2", cards, index=1, key="v2")
suit = st.radio("Suit", ["s", "o"], horizontal=True)

# --- 5. ULTRA GTO ENGINE (로직 분리 및 정밀 계산) ---
def get_decision_logic(mode, pos, v1, v2, suit, act, hero, stack, env, handy, v_bb):
    rank_map = {"A":14, "K":13, "Q":12, "J":11, "T":10, "9":9, "8":8, "7":7, "6":6, "5":5, "4":4, "3":3, "2":2}
    r1, r2 = rank_map[v1], rank_map[v2]
    if r1 < r2: v1, v2, r1, r2 = v2, v1, r2, r1
    hand_key = f"{v1}{v2}"
    is_s = (suit == "s")
    is_pair = (v1 == v2)
    
    style_val = {"Nits": 3, "Tight": 1, "Standard": 0, "Loose": -2, "Maniac": -4}[hero]

    # [Situation 1: Facing All-in]
    if act == "Facing All-in":
        # 1. 절대 방어 (AA, KK)
        if hand_key in ["AA", "KK"]: return "🔴 SNAP CALL", "지구상 최강 핸드입니다. 고민 없이 콜."
        
        # 2. 배당 콜 (내 스택 대비 부담이 적을 때)
        risk_pct = (v_bb / stack) * 100
        if mode == "Tournament (MTT)" and risk_pct <= 10:
            if is_pair or r1 >= 10 or is_s: return "🟢 SNAP CALL", f"부담 {risk_pct:.1f}%: 배당이 너무 좋습니다. 무조건 콜."
        
        # 3. 코인 플립 승부 (AK, QQ, JJ, TT)
        if hand_key in ["AK", "QQ", "JJ", "TT"]:
            if mode == "Tournament (MTT)" and "Bubble" in env: return "⚔️ DECIDE (ICM)", "강한 핸드지만 버블 상황입니다. 신중하세요."
            return "🔴 CALL", "승률 50% 이상의 코인 플립 승부입니다. 콜."
        
        # 4. 상대가 숏스택(15BB 이하)일 때 방어
        if v_bb <= 15:
            if hand_key in ["99", "88", "AQ", "AJ", "KQ"]: return "🟢 CALL", "상대 숏스택 범위를 압도합니다."
            if pos == "BB" and r1 >= 10: return "🟢 DEFEND", "빅블라인드 의무 방어 구간입니다."
            
        return "🔵 FOLD", "에퀴티가 부족합니다. 다음 기회를 노리세요."

    # [Situation 2: Cash Game]
    if mode == "Cash Game (Ring)":
        if act == "Facing Raise":
            if hand_key in ["AA", "KK", "QQ", "AK"]: return "🔥 3-BET", "캐시게임은 3-Bet으로 밸류를 뽑아야 합니다."
            if is_pair and r1 >= 7: return "🟢 CALL (Set Mine)", "20배 이상 배당 시 셋마이닝 콜."
            if is_s and r1 >= 11: return "⚔️ 3-BET or FOLD", "레이크를 피하기 위해 3-Bet하거나 폴드하세요."
            return "🔵 FOLD", "타이트한 운영이 수익의 핵심입니다."
        
        if act == "Unopened (RFI)":
            threshold = 12 + style_val if "Online" in env else 10 + style_val
            if r1 >= threshold: return "🟠 OPEN", "정석 오픈 핸드."
            if is_s and r1 >= (threshold - 2): return "🟠 OPEN", "수딧 커넥터/브로드웨이 오픈."
            if is_pair and r1 >= (5 + style_val): return "🟠 OPEN", "포켓 페어 오픈."
            return "🔵 FOLD", "EV 마이너스 구간."

    # [Situation 3: Tournament (MTT)]
    elif mode == "Tournament (MTT)":
        ante_bonus = 1.5
        if act == "Unopened (RFI)":
            if hand_key in ["AA", "KK", "QQ", "AK", "JJ"]: return "🔴 RAISE", "강하게 오픈하여 칩을 쌓으세요."
            # 스틸 (Steal)
            if pos in ["BTN", "CO", "HJ"]:
                steal_threshold = 9 + style_val - ante_bonus
                if r1 >= steal_threshold: return "🟠 STEAL", "앤티 따먹기 스틸 구간입니다."
                if is_s and r1 >= 7: return "🟠 STEAL", "수딧 카드로 블라인드 스틸."
            # 숏스택 푸쉬
            if stack <= 15:
                if is_pair or r1 >= 10 or (is_s and r1 >= 8): return "🚀 JAM (ALL-IN)", "15BB 이하: 잼(All-in)으로 생존하세요."
        
        if act == "Facing Raise":
            if "Bubble" in env and stack < 30:
                if hand_key in ["AA", "KK"]: return "🔴 3-BET/CALL", "어쩔 수 없는 승부입니다."
                return "🔵 TIGHT FOLD (ICM)", "버블 생존이 우선입니다. 폴드하세요."
            if hand_key in ["AQ", "TT", "99", "KQs"]: return "🟢 CALL", "플랍을 보고 결정하세요."

    return "🔵 FOLD", "패스하세요."

# --- 6. 결과 출력 ---
st.divider()
res, why = get_decision_logic(game_mode, pos, v1, v2, suit, action, hero_style, my_stack, env, handy, villain_bb)

if "SNAP" in res or "JAM" in res or "3-BET" in res: st.error(f"## {res}")
elif "OPEN" in res or "CALL" in res or "STEAL" in res: st.warning(f"## {res}")
else: st.info(f"## {res}")

st.markdown(f"""<div class="metric-box"><strong>📊 Analysis Info</strong><br>Mode: {game_mode} ({env}) | Hero: {my_stack}BB | Style: {hero_style}</div>""", unsafe_allow_html=True)
st.write(f"💡 **Guide:** {why}")

# --- 7. 하단 차트 복구 (모든 모드에서 항상 표시) ---
st.markdown("---")

# (1) 숏스택 올인표 (항상 표시)
st.markdown("### 🚀 Short Stack Push Range (10-20BB)")
st.caption("※ 모드와 상관없이 숏스택(20BB↓) 상황 발생 시 참고하세요.")
st.table(pd.DataFrame({
    "Position": ["UTG", "HJ", "CO", "BTN", "SB"],
    "Push Range": ["77+, AJs+, AQo+", "55+, A9s+, AJo+", "22+, A2s+, A8o+", "Any Pair, Any Ax, Kx", "Any Pair, Any Ax, Q5s+"]
}))

# (2) 핸드레인지 상세표 (2단 레이아웃 복구)
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
