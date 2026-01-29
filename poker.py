import streamlit as st
import pandas as pd

# 1. 앱 설정 (최상단 필수)
st.set_page_config(page_title="JM HOLDEM LEGEND 03 V1", page_icon="🃏", layout="centered")

# CSS: 모바일 최적화 및 CBJ 명언 디자인
st.markdown("""
    <style>
    div.stButton > button { width: 100%; height: 45px; font-weight: bold; border-radius: 8px; }
    .stSelectbox { margin-bottom: 5px; }
    .quote-box { 
        background-color: #1e1e1e; 
        color: #ff4b4b; 
        padding: 15px; 
        border-radius: 10px; 
        border: 2px solid #ff4b4b;
        text-align: center;
        font-weight: bold;
        font-size: 16px;
        margin-bottom: 20px;
    }
    .stTable { font-size: 12px !important; }
    </style>
""", unsafe_allow_html=True)

# --- 메인 상단 CBJ 명언 (더홀릭 우승자의 조언) ---
st.markdown('<div class="quote-box">"한번 우승했다고 우쭐대지마라 그게 나락으로 가는 지름길이다"<br><small style="color: #ccc;">- 더홀릭 우승 경험자 CBJ -</small></div>', unsafe_allow_html=True)

st.title("🛡️ JM HOLDEM LEGEND 03 V1")
st.error("⚠️ PRO DATA & HERO STYLE INTEGRATED")

# --- 2. 사이드바 (나의 성향 및 환경 설정) ---
with st.sidebar:
    st.header("⚙️ Game Setup")
    env = st.selectbox("Environment", ["Online", "Live Pub", "Tournament"])
    
    st.markdown("---")
    st.header("👤 My Playing Style")
    # 사용자가 직접 본인의 레인지 폭을 결정
    hero_style = st.select_slider(
        "Select My Range Tightness",
        options=["Very Tight", "Tight", "Standard", "Loose", "Very Loose"],
        value="Standard"
    )
    st.caption(f"기조: **{hero_style}** (내 성향에 맞춰 레인지 자동 조절)")
    
    st.markdown("---")
    # 스택 입력 및 슬라이더 연동
    s_in = st.number_input("Stack BB", 1, 1000, 100)
    stack = st.select_slider("Adjust BB", options=list(range(10, 1001, 10)), value=int(s_in) if s_in <= 1000 else 100)

# --- 3. 메인 화면: 상황 및 포지션 (스크롤/입력 방식) ---
st.markdown("### 1. Situation & Position")
# 9인 풀링 포지션 데이터 반영
pos_list = ["UTG", "UTG+1", "MP", "LJ", "HJ", "CO", "BTN", "SB", "BB"]
pos = st.selectbox("Select Position (Scroll/Type)", pos_list, index=6) # 기본값 BTN
action = st.radio("Opponent Action", ["Unopened (RFI)", "Facing Raise", "Facing All-in"], horizontal=True)

st.markdown("---")

# --- 4. 카드 선택 (드롭다운 스크롤/입력 방식) ---
st.markdown("### 2. Select My Hand")
cards = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]

c1_col, c2_col = st.columns(2)
with c1_col:
    v1 = st.selectbox("Card 1", cards, key="v1")
with c2_col:
    v2 = st.selectbox("Card 2", cards, index=1, key="v2")

suit = st.radio("Suit", ["s", "o"], horizontal=True)

# --- 5. 프로 차트 데이터 및 레인지 엔진 ---
# 이미지 2, 7번의 포지션별 통계 반영
stats = {
    "UTG": {"pct": "14-15%", "pair": 7, "s_ax": 10},
    "UTG+1": {"pct": "16-17%", "pair": 6, "s_ax": 10},
    "MP": {"pct": "18-20%", "pair": 5, "s_ax": 9},
    "LJ": {"pct": "20-22%", "pair": 4, "s_ax": 8},
    "HJ": {"pct": "23-25%", "pair": 3, "s_ax": 7},
    "CO": {"pct": "28-32%", "pair": 2, "s_ax": 2},
    "BTN": {"pct": "45-50%", "pair": 2, "s_ax": 2},
    "SB": {"pct": "38-42%", "pair": 2, "s_ax": 2},
    "BB": {"pct": "N/A", "pair": 2, "s_ax": 2}
}

def get_pro_strategy(pos, v1, v2, suit, act, hero, stack):
    ranks = {"A":14, "K":13, "Q":12, "J":11, "T":10, "9":9, "8":8, "7":7, "6":6, "5":5, "4":4, "3":3, "2":2}
    r1, r2 = ranks[v1], ranks[v2]
    if r1 < r2: v1, v2 = v2, v1
    hand = f"{v1}{v2}{suit}"
    is_pair = (v1 == v2)
    
    # 성향 가중치
    style_map = {"Very Tight": 2, "Tight": 1, "Standard": 0, "Loose": -1, "Very Loose": -2}
    w = style_map[hero]

    # 숏스택 푸쉬 전략 (이미지 3, 4번 반영)
    if stack <= 15 and act == "Unopened (RFI)":
        if r1 >= (13 + w) or (is_pair and r1 >= (5 + w)) or (suit == 's' and r1 >= (11 + w)):
            return "🔴 ALL-IN (Push)", f"{stack}BB 숏스택 전략: 내 성향({hero})에 맞춘 푸쉬 범위입니다.", "N/A"

    if act == "Unopened (RFI)":
        if pos == "BB": return "⚪ CHECK/FOLD", "빅블라인드 상황입니다.", "N/A"
        p = stats[pos]
        # 프리미엄 핸드
        if hand[:2] in ["AA", "KK", "QQ", "JJ", "AK"]:
            return "🔴 RAISE", "Premium Hand: 적극적인 밸류 빌딩이 필요합니다.", p["pct"]
        
        # 레인지 보정 로직
        if is_pair and r1 >= (p["pair"] + w):
            return "🟠 OPEN", f"{pos} Range: 포지션 대비 포켓 페어 가치가 충분합니다.", p["pct"]
        if suit == "s" and r1 >= (p["s_ax"] + w):
            return "🟠 OPEN", f"{pos} Range: 수딧 핸드의 포스트플랍 잠재력이 높습니다.", p["pct"]

    return "🔵 FOLD", f"현재 나의 성향({hero}) 기준으로는 핸드 밸류가 낮습니다.", stats.get(pos, {}).get("pct", "N/A")

# --- 6. 결과 출력 ---
st.divider()
res, why, prob = get_pro_strategy(pos, v1, v2, suit, action, hero_style, stack)

if "RAISE" in res or "ALL-IN" in res or "OPEN" in res:
    st.error(f"## Action: {res}")
else:
    st.info(f"## Action: {res}")

st.write(f"📊 **포지션 오픈 확률:** {prob} | 💡 **가이드:** {why}")

# --- 7. 하단 핸드 레인지 및 숏스택 표 (이미지 데이터) ---
st.markdown("---")
st.markdown("### 🚀 Short Stack Push Range (10-20BB)")
# 이미지 4번의 오픈샤브 예시 반영
push_df = pd.DataFrame({
    "Position": ["UTG", "HJ", "CO", "BTN", "SB"],
    "Push Example": ["22+, A2s+, A7o+, KTs+", "22+, A2s+, A5o+, K9s+", "22+, Any Suited Ax, A2o+", "Any Ax, Any Suited Kx", "Any Ax, K2s+, Q5s+"]
})
st.table(push_df)

st.markdown("### 📊 RFI Position Statistics")
# 이미지 7번의 포지션별 오픈 확률 반영
st.table(pd.DataFrame.from_dict(stats, orient='index')[['pct', 'pair']])
