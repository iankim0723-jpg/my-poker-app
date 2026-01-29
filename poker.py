import streamlit as st
import pandas as pd

# 1. 앱 설정
st.set_page_config(page_title="JM HOLDEM LEGEND 03 V1", page_icon="🃏", layout="centered")

# CSS: 사이드바 강조 및 모바일 UI 최적화
st.markdown("""
    <style>
    /* 사이드바 배경 및 테두리 강조 */
    [data-testid="stSidebar"] {
        background-color: #111111;
        border-right: 2px solid #ff4b4b;
    }
    [data-testid="stSidebar"] .stMarkdown h2, [data-testid="stSidebar"] .stMarkdown h1 {
        color: #ff4b4b;
        text-shadow: 1px 1px 2px black;
    }
    
    /* 버튼 및 UI 디자인 */
    div.stButton > button { width: 100%; height: 45px; font-weight: bold; border-radius: 8px; }
    .quote-box { 
        background-color: #1e1e1e; color: #ff4b4b; padding: 15px; border-radius: 10px; 
        border: 2px solid #ff4b4b; text-align: center; font-weight: bold; margin-bottom: 20px;
    }
    .card-detail {
        background-color: #262626; border: 1px solid #444; padding: 10px; 
        border-radius: 5px; margin-bottom: 8px; color: #eee;
    }
    </style>
""", unsafe_allow_html=True)

# --- 메인 상단 명언 ---
st.markdown('<div class="quote-box">"한번 우승했다고 우쭐대지마라 그게 나락으로 가는 지름길이다"<br><small style="color: #ccc;">- 더홀릭 우승 경험자 CBJ -</small></div>', unsafe_allow_html=True)

st.title("🛡️ JM HOLDEM LEGEND 03 V1")

# --- 2. 사이드바 (강조된 설정창) ---
with st.sidebar:
    st.header("📸 Card Scanner")
    st.camera_input("Scan your cards", label_visibility="collapsed")
    
    st.markdown("---")
    st.header("⚙️ Game Setup")
    env = st.selectbox("Environment", ["Online", "Live Pub", "Tournament"])
    h_in = st.number_input("Handy (Players)", 2, 9, 6)
    handy = st.slider("Set Players", 2, 9, int(h_in))
    
    st.markdown("---")
    st.header("👤 My Style")
    # 스타일별 레인지 차별화를 위한 가중치 설정
    hero_style = st.select_slider(
        "Hero Strategy", 
        options=["Very Tight", "Tight", "Standard", "Loose", "Very Loose"], 
        value="Standard"
    )
    st.info(f"Current Style: **{hero_style}**")
    
    st.markdown("---")
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

# --- 5. 상세 데이터 및 강화된 스타일 로직 ---
stats_detailed = {
    "UTG": {"pct": "14-15%", "pair": 10, "ax": 13, "broad": "KQs+"},
    "UTG+1": {"pct": "16-17%", "pair": 9, "ax": 12, "broad": "KQs+"},
    "MP": {"pct": "18-20%", "pair": 8, "ax": 11, "broad": "KTs+"},
    "LJ": {"pct": "20-22%", "pair": 7, "ax": 11, "broad": "KTs+"},
    "HJ": {"pct": "23-25%", "pair": 5, "ax": 10, "broad": "K9s+"},
    "CO": {"pct": "28-32%", "pair": 3, "ax": 8, "broad": "K5s+"},
    "BTN": {"pct": "45-50%", "pair": 2, "ax": 2, "broad": "Any K"},
    "SB": {"pct": "38-42%", "pair": 2, "ax": 4, "broad": "K2s+"}
}

def get_logic(pos, v1, v2, suit, act, hero, stack, handy):
    ranks = {"A":14, "K":13, "Q":12, "J":11, "T":10, "9":9, "8":8, "7":7, "6":6, "5":5, "4":4, "3":3, "2":2}
    r1, r2 = ranks[v1], ranks[v2]
    if r1 < r2: v1, v2 = v2, v1
    hand = f"{v1}{v2}{suit}"
    is_pair = (v1 == v2)
    
    # 스타일 가중치 강화 (스타일 간 간격을 2점차로 벌림)
    weight_map = {"Very Tight": 4, "Tight": 2, "Standard": 0, "Loose": -2, "Very Loose": -4}
    w = weight_map[hero]
    
    # 숏스택 푸쉬 (성향 대폭 반영)
    if stack <= 20 and act == "Unopened (RFI)":
        if r1 >= (13 + w) or (is_pair and r1 >= (7 + w)):
            return "🔴 ALL-IN (Push)", f"Hero Style({hero}) 기반 숏스택 최적 푸쉬"

    if act == "Unopened (RFI)":
        if pos == "BB": return "⚪ CHECK/FOLD", "빅블라인드 상황"
        p = stats_detailed.get(pos, {"pair": 10, "ax": 13})
        
        # 스타일별 오픈 결정 로직
        if hand[:2] in ["AA", "KK", "QQ", "JJ", "AK"]: return "🔴 RAISE", "Premium Value"
        if is_pair and r1 >= (p["pair"] + w): return "🟠 OPEN", f"{hero} 스타일에 적합한 오픈"
        if suit == "s" and r1 >= (p["ax"] + w): return "🟠 OPEN", f"수딧 이점 활용 오픈 ({hero})"
        if r1 >= (p["ax"] + 2 + w): return "🟠 OPEN", f"오프수딧 하이카드 오픈 ({hero})"

    return "🔵 FOLD", f"{hero} 기준 기대값 부족"

# --- 6. 결과 출력 ---
st.divider()
res, why = get_logic(pos, v1, v2, suit, action, hero_style, stack, handy)
if "RAISE" in res or "ALL-IN" in res: st.error(f"## Action: {res}")
elif "OPEN" in res: st.warning(f"## Action: {res}")
else: st.info(f"## Action: {res}")
st.write(f"📊 **Style:** {hero_style} | **Players:** {handy}인 | **Guide:** {why}")

# --- 7. 2단 핸드레인지 상세표 ---
st.markdown("---")
st.markdown("### 📊 RFI Position Range Detail")
c1, c2 = st.columns(2)
pos_keys = list(stats_detailed.keys())
with c1:
    for k in pos_keys[:4]:
        d = stats_detailed[k]
        st.markdown(f'<div class="card-detail"><strong>{k} ({d["pct"]})</strong><br><small>Pair: {d["pair"]}+ | Ax: {d["ax"]}+<br>Broad: {d["broad"]}</small></div>', unsafe_allow_html=True)
with c2:
    for k in pos_keys[4:]:
        d = stats_detailed[k]
        st.markdown(f'<div class="card-detail"><strong>{k} ({d["pct"]})</strong><br><small>Pair: {d["pair"]}+ | Ax: {d["ax"]}+<br>Broad: {d["broad"]}</small></div>', unsafe_allow_html=True)
