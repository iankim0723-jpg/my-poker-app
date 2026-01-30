import streamlit as st
import pandas as pd

# 1. 앱 설정
st.set_page_config(page_title="JM HOLDEM LEGEND 03 V1", page_icon="🃏", layout="centered")

# CSS: 디자인 및 가독성
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #0e1117; border-right: 3px solid #ff4b4b; }
    .quote-box { 
        background-color: #1e1e1e; color: #ff4b4b; padding: 15px; border-radius: 10px; 
        border: 2px solid #ff4b4b; text-align: center; font-weight: bold; margin-bottom: 20px;
    }
    .card-detail {
        background-color: #262626; border: 1px solid #444; padding: 10px; 
        border-radius: 8px; margin-bottom: 8px; color: #eee;
    }
    .pos-title { color: #ff4b4b; font-weight: bold; }
    div.stButton > button { width: 100%; height: 45px; font-weight: bold; border-radius: 8px; }
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
    st.header("⚙️ Game Setup")
    # 환경별 보정치 설정
    env = st.selectbox("Environment", ["Online (Standard GTO)", "Live Pub (Loose/Deep)", "Tournament (ICM)"])
    h_in = st.number_input("Handy (Players)", 2, 9, 6)
    handy = st.slider("Set Players", 2, 9, int(h_in))
    
    st.markdown("---")
    st.header("👤 Hero Style")
    # 스타일 가중치: GTO 기준점에서 얼마나 벗어날지 결정
    hero_style = st.select_slider("Range Width", options=["Nits (Very Tight)", "Tight", "GTO Standard", "Loose", "Lag (Maniac)"], value="GTO Standard")
    
    st.markdown("---")
    st.header("💰 Stack Size")
    s_in = st.number_input("Stack BB", 1, 1000, 100)
    stack = st.select_slider("Adjust BB", options=list(range(10, 1001, 10)), value=int(s_in) if s_in <= 1000 else 100)

# --- 3. 상황 및 포지션 ---
st.markdown("### 1. Situation & Position")
pos_list = ["UTG", "UTG+1", "MP", "LJ", "HJ", "CO", "BTN", "SB", "BB"]
pos = st.selectbox("Position", pos_list, index=6)
action = st.radio("Opponent Action", ["Unopened (RFI)", "Facing Raise", "Facing All-in"], horizontal=True)

st.markdown("---")

# --- 4. 핸드 선택 ---
st.markdown("### 2. My Hand")
cards = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]
c1, c2 = st.columns(2)
with c1: v1 = st.selectbox("Card 1", cards, key="v1")
with c2: v2 = st.selectbox("Card 2", cards, index=1, key="v2")
suit = st.radio("Suit", ["s", "o"], horizontal=True)

# --- 5. GLOBAL STANDARD GTO ENGINE (수학적 재설계) ---
def get_standard_gto_strategy(pos, v1, v2, suit, act, hero, stack, env, handy):
    # 1. 카드 파워 랭킹 시스템 (Rank Conversion)
    rank_map = {"A":14, "K":13, "Q":12, "J":11, "T":10, "9":9, "8":8, "7":7, "6":6, "5":5, "4":4, "3":3, "2":2}
    r1, r2 = rank_map[v1], rank_map[v2]
    if r1 < r2: v1, v2, r1, r2 = v2, v1, r2, r1 # r1이 항상 높은 카드
    hand_key = f"{v1}{v2}"
    is_s = (suit == "s")
    is_pair = (v1 == v2)
    
    # 2. 핸드 카테고리 분류 (GTO 티어 구분)
    tier_S = ["AA", "KK", "QQ", "AK"] # 절대적 몬스터 (어떤 상황에서도 플레이)
    tier_A = ["JJ", "TT", "AQs", "AJs", "KQs", "AQ"] # 강력한 프리미엄
    tier_B = ["99", "88", "ATs", "KJs", "QJs", "JTs", "KQ"] # 준수한 플레이어블
    
    # 3. 보정치 계산 (Adjustment Calculation)
    # 스타일 보정: 값이 낮을수록 더 루즈해짐 (기준점 낮춤)
    style_adj = {"Nits (Very Tight)": 3, "Tight": 1, "GTO Standard": 0, "Loose": -2, "Lag (Maniac)": -4}[hero]
    # 환경 보정: Live Pub은 배당 콜을 위해 커트라인 하향(-), Tournament는 생존을 위해 상향(+)
    env_adj = {"Online (Standard GTO)": 0, "Live Pub (Loose/Deep)": -2, "Tournament (ICM)": 2}[env]
    # 인원수 보정: 사람이 적을수록(숏핸디) 공격적으로 변해야 함
    handy_adj = -2 if handy <= 5 else 0
    
    total_adj = style_adj + env_adj + handy_adj

    # --- [상황별 GTO 로직] ---

    # A. Facing All-in (올인 직면)
    if act == "Facing All-in":
        # 1. 절대 방어 영역 (KK 폴드 방지)
        if hand_key in ["AA", "KK"]: 
            return "🔴 SNAP CALL", "GTO: 지구상에 이 핸드를 프리플랍에 죽이는 이론은 없습니다."
        
        # 2. 스택별 QQ/AK 처리
        if hand_key in ["QQ", "AK"]:
            if stack > 150 and "Tournament" in env: # 딥스택 토너먼트에서만 조심
                return "⚔️ CALL / DECIDE", "딥스택에서는 상대 성향을 고려하세요. 하지만 대부분 콜입니다."
            return "🔴 CALL", "표준 GTO 콜 레인지입니다."
            
        # 3. 숏스택(20BB 이하)일 때 콜 레인지 확장
        if stack <= 20:
            if hand_key in ["JJ", "TT", "99", "AQ", "AJ", "KQ"]: return "🟢 CALL", "숏스택 수학적 배당 콜입니다."
            
        return "🔵 FOLD", "상대 올인 레인지 대비 에퀴티 부족."

    # B. Facing Raise (상대방 오픈 레이즈 시)
    if act == "Facing Raise":
        if hand_key in tier_S: return "🔥 3-BET (Value)", "GTO: 밸류를 뽑기 위해 리레이즈(3-Bet) 필수입니다."
        if hand_key in tier_A: return "⚔️ 3-BET / CALL", "GTO: 방어하거나 공격해야 하는 필수 핸드입니다."
        
        # 포켓 페어 셋마이닝 (배당 콜)
        if is_pair and r1 >= (6 + total_adj//2): # 66+, 77+ 등
            return "🟢 CALL (Set Mine)", "포켓 페어는 셋마이닝 가치가 높습니다."
            
        # 수딧 브로드웨이/커넥터 (라이브 펍 보정)
        if is_s and r1 >= (10 + total_adj//2): # KTs, QJs 등
            return "🟢 CALL", "포스트플랍 잠재력이 높은 수딧 핸드입니다."
            
        return "🔵 FOLD", "레이즈에 콜하기에는 에퀴티가 부족합니다."

    # C. Unopened (RFI) - 오픈 레이즈
    if act == "Unopened (RFI)":
        if hand_key in tier_S or hand_key in tier_A: 
            return "🔴 RAISE", "전 포지션 GTO 오픈 핸드입니다."
        
        # 포지션별 오픈 기준점 (GTO Solver RFI Table 근사치)
        # 숫자가 낮을수록(BTN) 기준점이 낮아져서 더 많은 핸드로 오픈함
        pos_threshold = {
            "UTG": 12.5, "UTG+1": 12.0, "MP": 11.5, "LJ": 11.0, 
            "HJ": 10.5, "CO": 9.5, "BTN": 7.0, "SB": 8.0, "BB": 99
        }
        
        target = pos_threshold.get(pos, 12) + (total_adj * 0.5) # 보정치 적용
        
        # 1. 수딧 핸드 판단
        if is_s:
            # BTN/CO에서는 Ace, King, Queen 수딧 거의 다 오픈
            if pos in ["BTN", "CO"] and r1 >= 10: return "🟠 OPEN", "GTO: 포지션 수딧 스틸"
            # 일반적인 기준
            if r1 >= target: return "🟠 OPEN", f"{env} 환경 최적 오픈"
            # 수딧 커넥터 (98s, 87s 등) - 버튼/컷오프에서 허용
            if pos in ["BTN", "CO", "HJ"] and r1 >= 5 and (r1 - r2) == 1: 
                return "🟠 OPEN", "밸런싱을 위한 수딧 커넥터 오픈"

        # 2. 오프수딧 판단 (기준점이 더 높음)
        else:
            if r1 >= (target + 1.5): return "🟠 OPEN", f"{pos} 오프수딧 오픈"

        # 3. 포켓 페어
        if is_pair:
            # UTG는 77+, BTN은 22+ 등
            pair_limit = {"UTG": 7, "MP": 6, "HJ": 5, "CO": 3, "BTN": 2, "SB": 2}.get(pos, 5)
            if r1 >= (pair_limit + total_adj): return "🟠 OPEN", "GTO: 포켓 페어 오픈"

    return "🔵 FOLD", "EV(기대값)가 마이너스인 구간입니다."

# --- 6. 결과 출력 ---
st.divider()
res, why = get_standard_gto_strategy(pos, v1, v2, suit, action, hero_style, stack, env, handy)

if "SNAP CALL" in res or "3-BET" in res or "RAISE" in res: st.error(f"## {res}")
elif "OPEN" in res or "CALL" in res: st.warning(f"## {res}")
else: st.info(f"## {res}")

st.write(f"📊 **Engine:** World Standard GTO | **Mode:** {env}")
st.write(f"💡 **Analysis:** {why}")

# --- 7. 하단 차트 및 데이터 ---
st.markdown("---")
st.markdown("### 📊 GTO Standard Opening Frequency")
col1, col2 = st.columns(2)
stats = {"UTG":"14%", "UTG+1":"16%", "MP":"19%", "LJ":"21%", "HJ":"24%", "CO":"30%", "BTN":"48% (Wide)", "SB":"42%"}
p_keys = list(stats.keys())
with col1:
    for k in p_keys[:4]:
        st.markdown(f'<div class="card-detail"><span class="pos-title">{k} ({stats[k]})</span><br><small>GTO 정석 빈도</small></div>', unsafe_allow_html=True)
with col2:
    for k in p_keys[4:]:
        st.markdown(f'<div class="card-detail"><span class="pos-title">{k} ({stats[k]})</span><br><small>GTO 정석 빈도</small></div>', unsafe_allow_html=True)

st.markdown("### 🚀 Short Stack Push Range (GTO Nash Equilibrium)")
st.table(pd.DataFrame({
    "Position": ["UTG", "HJ", "CO", "BTN", "SB"],
    "Push (15BB)": ["77+, AJs+, AQo+", "55+, A9s+, AJo+", "22+, A2s+, A8o+", "Any Pair, Any Ax, Kx", "Any Pair, Any Ax, Q5s+"]
}))
