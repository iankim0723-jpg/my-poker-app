import streamlit as st
import pandas as pd

# 1. 앱 설정 (최상단 필수)
st.set_page_config(page_title="JM HOLDEM LEGEND 03 V1", page_icon="🃏", layout="centered")

# CSS: 모바일 2단 테이블 및 UI 최적화
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
    /* 모바일 테이블 가독성 강화 */
    .detail-table {
        font-size: 11px !important;
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 10px;
    }
    .detail-table th { background-color: #333; color: white; padding: 6px; }
    .detail-table td { border: 1px solid #444; padding: 6px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# --- 메인 상단 CBJ 명언 ---
st.markdown('<div class="quote-box">"한번 우승했다고 우쭐대지마라 그게 나락으로 가는 지름길이다"<br><small style="color: #ccc;">- 더홀릭 우승 경험자 CBJ -</small></div>', unsafe_allow_html=True)

st.title("🛡️ JM HOLDEM LEGEND 03 V1")

# --- 2. 사이드바 (카메라, 플레이어 수, 성향, 스택 설정) ---
with st.sidebar:
    st.header("📸 Scan My Hand")
    captured_image = st.camera_input("Take a photo of your cards")
    
    st.markdown("---")
    st.header("⚙️ Game Setup")
    env = st.selectbox("Environment", ["Online", "Live Pub", "Tournament"])
    h_in = st.number_input("Handy (Player Count)", 2, 9, 6)
    handy = st.slider("Adjust Handy", 2, 9, int(h_in))
    
    st.markdown("---")
    st.header("👤 My Playing Style")
    hero_style = st.select_slider("My Range Tightness", options=["Very Tight", "Tight", "Standard", "Loose", "Very Loose"], value="Standard")
    
    st.markdown("---")
    s_in = st.number_input("Stack BB", 1, 1000, 100)
    stack = st.select_slider("Adjust BB", options=list(range(10, 1001, 10)), value=int(s_in) if s_in <= 1000 else 100)

# --- 3. 메인 화면: 상황 및 포지션 ---
st.markdown("### 1. Situation & Position")
pos_list = ["UTG", "UTG+1", "MP", "LJ", "HJ", "CO", "BTN", "SB", "BB"]
pos = st.selectbox("Select Position (Scroll/Type)", pos_list, index=6)
action = st.radio("Opponent Action", ["Unopened (RFI)", "Facing Raise", "Facing All-in"], horizontal=True)

st.markdown("---")

# --- 4. 카드 선택 ---
st.markdown("### 2. Select My Hand")
cards = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]

c1_col, c2_col = st.columns(2)
with c1_col:
    v1 = st.selectbox("Card 1", cards, key="v1")
with c2_col:
    v2 = st.selectbox("Card 2", cards, index=1, key="v2")

suit = st.radio("Suit", ["s", "o"], horizontal=True)

# --- 5. 상세 데이터베이스 (이미지 데이터 기반) ---
stats_detailed = {
    "UTG": {"pct": "14-15%", "pair": "77+", "ax": "ATs+, AJo+", "broad": "KQs, QJs, JTs", "memo": "가장 타이트"},
    "UTG+1": {"pct": "16-17%", "pair": "66+", "ax": "ATs+, AJo+", "broad": "KQs, QJs, JTs", "memo": "약간 확장"},
    "MP": {"pct": "18-20%", "pair": "55+", "ax": "A9s+, ATo+", "broad": "KTs+, QTs+", "memo": "표준"},
    "LJ": {"pct": "20-22%", "pair": "44+", "ax": "A8s+, ATo+", "broad": "KTs+, QTs+", "memo": "중후반"},
    "HJ": {"pct": "23-25%", "pair": "33+", "ax": "A7s+, A9o+", "broad": "K9s+, Q9s+", "memo": "스틸 시작"},
    "CO": {"pct": "28-32%", "pair": "22+", "ax": "A2s+, A2o+", "broad": "K5s+, Q8s+", "memo": "스틸 핵심"},
    "BTN": {"pct": "45-50%", "pair": "22+", "ax": "Any Ax", "broad": "Any Suited K", "memo": "가장 넓음"},
    "SB": {"pct": "38-42%", "pair": "22+", "ax": "A2s+, A2o+", "broad": "K2s+, Q5s+", "memo": "믹스 선호"}
}

# --- 6. 전략 로직 ---
def get_poker_strategy(pos, v1, v2, suit, act, hero, stack, handy):
    ranks = {"A":14, "K":13, "Q":12, "J":11, "T":10, "9":9, "8":8, "7":7, "6":6, "5":5, "4":4, "3":3, "2":2}
    r1, r2 = ranks[v1], ranks[v2]
    if r1 < r2: v1, v2 = v2, v1
    hand = f"{v1}{v2}{suit}"
    is_pair = (v1 == v2)
    
    style_map = {"Very Tight": 2, "Tight": 1, "Standard": 0, "Loose": -1, "Very Loose": -2}
    w = style_map[hero]
    handy_adj = 0 if handy >= 6 else -1

    if stack <= 15 and act == "Unopened (RFI)":
        if r1 >= (13 + w + handy_adj) or (is_pair and r1 >= (5 + w)):
            return "🔴 ALL-IN (Push)", f"{stack}BB 숏스택 최적 푸쉬 범위입니다."

    if act == "Unopened (RFI)":
        if pos == "BB": return "⚪ CHECK/FOLD", "빅블라인드입니다."
        p = stats_detailed.get(pos, {"pct": "N/A"})
        if hand[:2] in ["AA", "KK", "QQ", "JJ", "AK"]:
            return "🔴 RAISE", "프리미엄 밸류 레이즈 필수."
        if r1 >= 10 or suit == "s":
            return "🟠 OPEN", f"{pos} 포지션의 수익성 있는 오픈 구간입니다."

    return "🔵 FOLD", "수학적으로 기대값이 낮습니다."

# --- 7. 결과 및 상세 레인지표 (2줄 레이아웃) ---
st.divider()
res, why = get_poker_strategy(pos, v1, v2, suit, action, hero_style, stack, handy)
if "RAISE" in res or "ALL-IN" in res: st.error(f"## Action: {res}")
else: st.info(f"## Action: {res}")

st.write(f"👤 **스타일:** {hero_style} | 👥 **Handy:** {handy}인 | 📊 **오픈 확률:** {stats_detailed.get(pos, {}).get('pct', 'N/A')}")

st.markdown("---")
st.markdown("### 📊 RFI Position Range Detail (2-Row View)")

# 상단 4개 포지션과 하단 4개 포지션으로 나누어 가독성 극대화
col1, col2 = st.columns(2)
positions = list(stats_detailed.keys())

with col1:
    for p in positions[:4]:
        data = stats_detailed[p]
        st.markdown(f"""
        <div style="border: 1px solid #444; padding: 10px; border-radius: 5px; margin-bottom: 5px;">
            <strong style="color: #ff4b4b;">{p} ({data['pct']})</strong><br>
            <small>Pairs: {data['pair']} | Ax: {data['ax']}</small><br>
            <small>Broad: {data['broad']}</small>
        </div>
        """, unsafe_allow_html=True)

with col2:
    for p in positions[4:]:
        data = stats_detailed[p]
        st.markdown(f"""
        <div style="border: 1px solid #444; padding: 10px; border-radius: 5px; margin-bottom: 5px;">
            <strong style="color: #ff4b4b;">{p} ({data['pct']})</strong><br>
            <small>Pairs: {data['pair']} | Ax: {data['ax']}</small><br>
            <small>Broad: {data['broad']}</small>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("### 🚀 Short Stack Push Range (10-20BB)")
push_df = pd.DataFrame({
    "Position": ["UTG", "HJ", "CO", "BTN", "SB"],
    "Push Details": ["22+, A2s+, A7o+, KTs+", "22+, A2s+, A5o+, K9s+", "22+, Any Suited Ax, A2o+", "Any Ax, Any Suited Kx", "Any Ax, K2s+, Q5s+"]
})
st.table(push_df)
