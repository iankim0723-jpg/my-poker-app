import streamlit as st
import pandas as pd

# 1. 앱 설정
st.set_page_config(page_title="JM HOLDEM LEGEND 03 V1", page_icon="🃏", layout="centered")

# CSS: 사이드바 강조 및 모바일 레이아웃 최적화
st.markdown("""
    <style>
    /* 사이드바 전체 강조: 어두운 배경 + 강렬한 붉은색 테두리 */
    [data-testid="stSidebar"] {
        background-color: #0e1117;
        border-right: 3px solid #ff4b4b;
        box-shadow: 5px 0px 15px rgba(255, 75, 75, 0.3);
    }
    
    /* 사이드바 내부 위젯(슬라이더, 입력창) 강조 */
    [data-testid="stSidebar"] .stMarkdown h2 {
        color: #ff4b4b;
        border-bottom: 1px solid #ff4b4b;
        padding-bottom: 5px;
    }
    
    /* 명언 박스 디자인 */
    .quote-box { 
        background-color: #1e1e1e; color: #ff4b4b; padding: 15px; border-radius: 10px; 
        border: 2px solid #ff4b4b; text-align: center; font-weight: bold; margin-bottom: 20px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.5);
    }

    /* 핸드레인지 상세 카드 디자인 */
    .card-detail {
        background-color: #262626; border: 1px solid #444; padding: 10px; 
        border-radius: 8px; margin-bottom: 8px; color: #eee;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
    }
    .pos-title { color: #ff4b4b; font-weight: bold; font-size: 1.1em; }

    /* 버튼 스타일 */
    div.stButton > button { width: 100%; height: 45px; font-weight: bold; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# --- 메인 상단 CBJ 명언 ---
st.markdown('<div class="quote-box">"한번 우승했다고 우쭐대지마라 그게 나락으로 가는 지름길이다"<br><small style="color: #ccc;">- 더홀릭 우승 경험자 CBJ -</small></div>', unsafe_allow_html=True)

st.title("🛡️ JM HOLDEM LEGEND 03 V1")

# --- 2. 사이드바 (강력 강조 버전) ---
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
    # 스타일 가중치 차별화 적용
    hero_style = st.select_slider(
        "Hero Strategy", 
        options=["Very Tight", "Tight", "Standard", "Loose", "Very Loose"], 
        value="Standard"
    )
    st.warning(f"Active Mode: **{hero_style}**")
    
    st.markdown("---")
    st.header("💰 Stack Size")
    s_in = st.number_input("Stack BB", 1, 1000, 100)
    stack = st.select_slider("Adjust BB", options=list(range(10, 1001, 10)), value=int(s_in) if s_in <= 1000 else 100)

# --- 3. 상황 및 포지션 ---
st.markdown("### 1. Situation & Position")
pos_list = ["UTG", "UTG+1", "MP", "LJ", "HJ", "CO", "BTN", "SB", "BB"]
pos = st.selectbox("Position Selection", pos_list, index=6)
action = st.radio("Opponent Action", ["Unopened (RFI)", "Facing Raise", "Facing All-in"], horizontal=True)

st.markdown("---")

# --- 4. 핸드 선택 ---
st.markdown("### 2. My Hand")
cards = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]
c1, c2 = st.columns(2)
with c1: v1 = st.selectbox("Card 1", cards, key="v1")
with c2: v2 = st.selectbox("Card 2", cards, index=1, key="v2")
suit = st.radio("Suit", ["s", "o"], horizontal=True)

# --- 5. 상세 데이터 및 스타일별 로직 ---
stats_detailed = {
    "UTG": {"pct": "14-15%", "pair": 10, "ax": 13, "broad": "KQs+", "memo": "Tightest"},
    "UTG+1": {"pct": "16-17%", "pair": 9, "ax": 12, "broad": "KQs+", "memo": "Standard Tight"},
    "MP": {"pct": "18-20%", "pair": 8, "ax": 11, "broad": "KTs+", "memo": "Balanced"},
    "LJ": {"pct": "20-22%", "pair": 7, "ax": 11, "broad": "KTs+", "memo": "Middle"},
    "HJ": {"pct": "23-25%", "pair": 5, "ax": 10, "broad": "K9s+", "memo": "Semi-Steal"},
    "CO": {"pct": "28-32%", "pair": 3, "ax": 8, "broad": "K5s+", "memo": "Steal Core"},
    "BTN": {"pct": "45-50%", "pair": 2, "ax": 2, "broad": "Any K", "memo": "Aggressive Steal"},
    "SB": {"pct": "38-42%", "pair": 2, "ax": 4, "broad": "K2s+", "memo": "Mixed Strategy"}
}

def get_logic(pos, v1, v2, suit, act, hero, stack, handy):
    ranks = {"A":14, "K":13, "Q":12, "J":11, "T":10, "9":9, "8":8, "7":7, "6":6, "5":5, "4":4, "3":3, "2":2}
    r1, r2 = ranks[v1], ranks[v2]
    if r1 < r2: v1, v2 = v2, v1
    hand = f"{v1}{v2}{suit}"
    is_pair = (v1 == v2)
    
    # 스타일 가중치 차별화 (점수차를 벌려 체감 효과 증대)
    weight_map = {"Very Tight": 4, "Tight": 2, "Standard": 0, "Loose": -2, "Very Loose": -4}
    w = weight_map[hero]
    
    # 숏스택 푸쉬 (성향 대폭 반영)
    if stack <= 15 and act == "Unopened (RFI)":
        if r1 >= (13 + w) or (is_pair and r1 >= (6 + w)):
            return "🔴 ALL-IN (Push)", f"{hero} 스타일 기준 숏스택 최적 올인"

    if act == "Unopened (RFI)":
        if pos == "BB": return "⚪ CHECK/FOLD", "빅블라인드 상황"
        p = stats_detailed.get(pos, {"pair": 10, "ax": 13})
        
        if hand[:2] in ["AA", "KK", "QQ", "JJ", "AK"]: return "🔴 RAISE", "Premium Value"
        # 스타일 가중치(w)에 따른 동적 결정
        if is_pair and r1 >= (p["pair"] + w): return "🟠 OPEN", f"{hero} 포지션 페어 오픈"
        if suit == "s" and r1 >= (p["ax"] + w): return "🟠 OPEN", f"{hero} 수딧 카드 오픈"
        if r1 >= (p["ax"] + 2 + w): return "🟠 OPEN", f"{hero} 하이카드 오픈"

    return "🔵 FOLD", f"{hero} 스타일 기준 기대값 미달"

# --- 6. 결과 출력 ---
st.divider()
res, why = get_logic(pos, v1, v2, suit, action, hero_style, stack, handy)
if "RAISE" in res or "ALL-IN" in res: st.error(f"## Action: {res}")
elif "OPEN" in res: st.warning(f"## Action: {res}")
else: st.info(f"## Action: {res}")
st.write(f"📊 **Style:** {hero_style} | **Players:** {handy}인 | **Guide:** {why}")

# --- 7. 하단 상세 데이터 (2단 상세표 + 숏스택 올인표) ---
st.markdown("---")
st.markdown("### 📊 RFI Position Range Detail (Detailed)")

col1, col2 = st.columns(2)
pos_keys = list(stats_detailed.keys())
with col1:
    for k in pos_keys[:4]:
        d = stats_detailed[k]
        st.markdown(f'''<div class="card-detail"><span class="pos-title">{k} ({d["pct"]})</span><br>
        <small>Pair: {d["pair"]}+ | Ax: {d["ax"]}+<br>Broad: {d["broad"]}<br>Note: {d["memo"]}</small></div>''', unsafe_allow_html=True)
with col2:
    for k in pos_keys[4:]:
        d = stats_detailed[k]
        st.markdown(f'''<div class="card-detail"><span class="pos-title">{k} ({d["pct"]})</span><br>
        <small>Pair: {d["pair"]}+ | Ax: {d["ax"]}+<br>Broad: {d["broad"]}<br>Note: {d["memo"]}</small></div>''', unsafe_allow_html=True)

st.markdown("---")
st.markdown("### 🚀 Short Stack Push Range (10-20BB)")
push_df = pd.DataFrame({
    "Position": ["UTG", "HJ", "CO", "BTN", "SB"],
    "Push Strategy (Range)": [
        "22+, A2s+, A7o+, KTs+", 
        "22+, A2s+, A5o+, K9s+", 
        "22+, Any Suited Ax, A2o+", 
        "Any Ax, Any Suited Kx", 
        "Any Ax, K2s+, Q5s+"
    ]
})
st.table(push_df)
