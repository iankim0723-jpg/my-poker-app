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
    .metric-box { text-align: center; border: 1px solid #555; padding: 10px; border-radius: 5px; background: #222; }
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
    # [핵심] 캐시와 토너먼트의 로직을 완전히 분리
    game_mode = st.radio("Select Mode", ["Cash Game (Ring)", "Tournament (MTT)"])
    
    if game_mode == "Cash Game (Ring)":
        env = st.selectbox("Field Type", ["Online (6-Max/9-Max)", "Live Pub (Deep Stack)"])
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
    s_in = st.number_input("My Stack (BB)", 1, 1000, 120) # 기본값 120BB
    my_stack = st.select_slider("Adjust My BB", options=list(range(5, 1001, 5)), value=int(s_in) if s_in <= 1000 else 100)

# --- 3. 상황 및 포지션 ---
st.markdown("### 1. Situation & Position")
pos_list = ["UTG", "UTG+1", "MP", "LJ", "HJ", "CO", "BTN", "SB", "BB"]
pos = st.selectbox("Position", pos_list, index=6)

# 상황 선택
action_options = ["Unopened (RFI)", "Facing Raise", "Facing All-in"]
action = st.radio("Opponent Action", action_options, horizontal=True)

# [핵심 기능] Facing All-in 선택 시 상대 스택 입력창 활성화
villain_bb = 0
if action == "Facing All-in":
    st.markdown("#### 🚨 Villain Info")
    villain_bb = st.number_input("상대방 올인 금액 (Villain All-in BB)", min_value=1, max_value=1000, value=10)
    
    # 배당 계산 프리뷰
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

# --- 5. ULTRA GTO ENGINE (Cash & Tourney Separated) ---
def get_decision_logic(mode, pos, v1, v2, suit, act, hero, stack, env, handy, v_bb):
    # 랭크 변환
    rank_map = {"A":14, "K":13, "Q":12, "J":11, "T":10, "9":9, "8":8, "7":7, "6":6, "5":5, "4":4, "3":3, "2":2}
    r1, r2 = rank_map[v1], rank_map[v2]
    if r1 < r2: v1, v2, r1, r2 = v2, v1, r2, r1
    hand_key = f"{v1}{v2}"
    is_s = (suit == "s")
    is_pair = (v1 == v2)
    
    # 스타일 보정
    style_val = {"Nits": 3, "Tight": 1, "Standard": 0, "Loose": -2, "Maniac": -4}[hero]

    # ==========================================
    # [로직 1] Facing All-in (올인 대응 정밀 계산)
    # ==========================================
    if act == "Facing All-in":
        # 1. 절대 방어 (AA, KK)
        if hand_key in ["AA", "KK"]: return "🔴 SNAP CALL", "지구상 최강 핸드. 고민 금지."

        # 2. 내 스택 대비 상대 올인이 아주 적을 때 (Big Stack Bully)
        # 예: 나 120BB, 상대 7BB -> 6% 부담
        risk_pct = (v_bb / stack) * 100
        
        if mode == "Tournament (MTT)" and risk_pct <= 10:
            # 부담이 10% 미만이면 'Any Two Card'에 가깝게 넓어짐 (배당 콜)
            if is_pair: return "🟢 SNAP CALL", f"부담 {risk_pct:.1f}%: 모든 페어는 무조건 콜입니다."
            if r1 >= 10: return "🟢 CALL", f"부담 {risk_pct:.1f}%: 하이카드로 배당 콜 충분합니다."
            if is_s: return "🟢 CALL", "저렴한 비용으로 수딧 대박 노리기 가능."
            return "🟡 LOOSE CALL?", "배당은 나오지만 너무 쓰레기 핸드면 폴드."

        # 3. 코인 플립 구간 (20BB ~ 50BB 승부)
        if hand_key in ["AK", "QQ", "JJ", "TT"]:
            if mode == "Tournament (MTT)" and "Bubble" in env:
                return "⚔️ DECIDE (ICM)", "강한 핸드지만 버블 상황입니다. 상대가 빅스택이면 조심."
            return "🔴 CALL", "코인 플립 이상(6:4 ~ 5:5)의 승부입니다. 콜."
        
        # 4. 숏스택(상대 15BB 이하) 상대로 적정 방어
        if v_bb <= 15:
            if hand_key in ["99", "88", "AQ", "AJ", "KQ"]: return "🟢 CALL", "상대 숏스택 푸쉬 레인지를 이기고 있습니다."
            if pos == "BB" and r1 >= 10: return "🟢 DEFEND", "BB에서는 넓게 방어하세요."

        return "🔵 FOLD", "상대 올인을 받기에 에퀴티가 부족합니다."

    # ==========================================
    # [로직 2] Cash Game Strategy (Max EV)
    # ==========================================
    if mode == "Cash Game (Ring)":
        # 캐시게임은 레이크 때문에 3-Bet 위주, 플랫 콜 줄이기
        if act == "Facing Raise":
            if hand_key in ["AA", "KK", "QQ", "AK"]: return "🔥 3-BET", "캐시게임은 3-Bet으로 밸류를 극대화하세요."
            if is_pair and r1 >= 7: return "🟢 CALL (Set Mine)", "20배 배당 나오면 셋마이닝 콜."
            if is_s and r1 >= 11: return "⚔️ 3-BET or FOLD", "상대가 루즈하면 3-Bet, 아니면 폴드 (레이크 회피)."
            return "🔵 FOLD", "캐시게임은 타이트하게."
            
        if act == "Unopened (RFI)":
            # 라이브 펍(Deep)은 조금 루즈하게
            threshold = 12 + style_val if "Online" in env else 10 + style_val
            if r1 >= threshold: return "🟠 OPEN", "캐시게임 정석 오픈."
            if is_s and r1 >= (threshold - 2): return "🟠 OPEN", "수딧 커넥터/브로드웨이 오픈."
            if is_pair and r1 >= (5 + style_val): return "🟠 OPEN", "포켓 페어 오픈."
            
        return "🔵 FOLD", "EV 마이너스."

    # ==========================================
    # [로직 3] Tournament Strategy (Survival & Chip Accumulation)
    # ==========================================
    elif mode == "Tournament (MTT)":
        # 토너먼트는 앤티(Ante)가 있어서 팟이 이미 깔려있음 -> 더 루즈하게
        ante_bonus = 1.5 # 랭크 보정치
        
        if act == "Unopened (RFI)":
            if hand_key in ["AA", "KK", "QQ", "AK", "JJ"]: return "🔴 RAISE", "강하게 오픈."
            
            # 포지션별 훔치기 (Steal)
            if pos in ["BTN", "CO", "HJ"]:
                steal_threshold = 9 + style_val - ante_bonus # 앤티 꿀빨기
                if r1 >= steal_threshold: return "🟠 STEAL", "앤티가 있습니다. 적극적으로 훔치세요."
                if is_s and r1 >= 7: return "🟠 STEAL", "수딧 카드로 스틸 시도."
            
            # 숏스택(15BB 이하) 푸쉬 차트
            if stack <= 15:
                if is_pair or r1 >= 10 or (is_s and r1 >= 8): 
                    return "🚀 JAM (ALL-IN)", "15BB 이하: 잼(All-in) 박아서 앤티+블라인드 획득."

        if act == "Facing Raise":
            if "Bubble" in env and stack < 30:
                # 버블일 때 숏/미들 스택은 몸사리기
                if hand_key in ["AA", "KK"]: return "🔴 3-BET/CALL", "어쩔 수 없는 승부."
                return "🔵 TIGHT FOLD (ICM)", "버블입니다. 애매한 핸드로 탈락하지 마세요."
                
            if hand_key in ["AQ", "TT", "99", "KQs"]: return "🟢 CALL", "토너먼트는 플랍을 보고 결정해도 됩니다."

    return "🔵 FOLD", "수학적 근거 부족."

# --- 6. 결과 출력 ---
st.divider()
# 로직 호출 시 villain_bb(상대 올인액) 전달
res, why = get_decision_logic(game_mode, pos, v1, v2, suit, action, hero_style, my_stack, env, handy, villain_bb)

if "SNAP" in res or "JAM" in res or "3-BET" in res: st.error(f"## {res}")
elif "OPEN" in res or "CALL" in res or "STEAL" in res: st.warning(f"## {res}")
else: st.info(f"## {res}")

# 상세 분석 박스
st.markdown(f"""
<div class="metric-box">
    <strong>📊 Analysis Info</strong><br>
    Mode: {game_mode} ({env})<br>
    Hero Stack: {my_stack}BB | Style: {hero_style}
</div>
""", unsafe_allow_html=True)

st.write(f"💡 **Pro Guide:** {why}")

# --- 7. 하단 차트 (모드별 다르게 표시) ---
st.markdown("---")
if game_mode == "Tournament (MTT)":
    st.markdown("### 🏆 Tournament Push/Fold (Short Stack)")
    st.table(pd.DataFrame({
        "Position": ["UTG", "MP", "CO", "BTN", "SB"],
        "10BB Jam": ["77+, AJo+, ATs+", "55+, A9o+, A8s+", "22+, A7o+, A2s+", "Any Pair, Any Ax", "Any Pair, Any Ax, Kx"]
    }))
else:
    st.markdown("### 💸 Cash Game RFI Range (100BB Deep)")
    st.table(pd.DataFrame({
        "Position": ["UTG", "MP", "CO", "BTN", "SB"],
        "Open Range": ["77+, ATs+, AQo+", "55+, A9s+, AJo+", "22+, A2s+, A9o+", "Any Pair, Any Ax, K9s+", "Any Pair, A5s+, ATo+"]
    }))
