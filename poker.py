import streamlit as st
import pandas as pd

# 1. 앱 설정
st.set_page_config(page_title="JM HOLDEM LEGEND 03 V1", page_icon="🃏", layout="centered")

# CSS: 모바일 최적화 및 표 디자인
st.markdown("""
    <style>
    div.stButton > button { width: 100%; height: 45px; font-weight: bold; border-radius: 8px; }
    .stSelectbox { margin-bottom: 5px; }
    .range-table { font-size: 12px; text-align: center; width: 100%; border-collapse: collapse; }
    .range-table th, .range-table td { border: 1px solid #ddd; padding: 4px; }
    .range-table th { background-color: #f2f2f2; }
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ JM HOLDEM LEGEND 03 V1")
st.error("⚠️ PRO DATA & RANGE CHART INTEGRATED")

# --- 2. 사이드바 (기본 설정) ---
with st.sidebar:
    st.header("⚙️ Game Setup")
    env = st.selectbox("Environment", ["Online", "Live Pub", "Tournament"])
    st.markdown("---")
    s_in = st.number_input("Stack BB", 1, 1000, 100)
    stack = st.select_slider("Adjust BB", options=list(range(10, 1001, 10)), value=int(s_in) if s_in <= 1000 else 100)

# --- 3. 메인 화면: 상황 및 포지션 (스크롤/입력) ---
st.markdown("### 1. Situation & Position")
pos_list = ["UTG", "UTG+1", "MP", "LJ", "HJ", "CO", "BTN", "SB", "BB"]
pos = st.selectbox("Select Position (Scroll/Type)", pos_list, index=6)
action = st.radio("Opponent Action", ["Unopened (RFI)", "Facing Raise"], horizontal=True)

st.markdown("---")

# --- 4. 카드 선택 (드롭다운 스크롤/입력) ---
st.markdown("### 2. Select Hand")
cards = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]

c1_col, c2_col = st.columns(2)
with c1_col:
    v1 = st.selectbox("Card 1", cards, key="v1")
with c2_col:
    v2 = st.selectbox("Card 2", cards, index=1, key="v2")

suit = st.radio("Suit", ["s", "o"], horizontal=True)

# --- 5. 프로 전략 엔진 데이터 ---
stats = {
    "UTG": {"pct": "14-15%", "pair": "77+", "ax": "ATs+, AJo+", "broad": "KQs, QJs, JTs", "memo": "가장 타이트"},
    "UTG+1": {"pct": "16-17%", "pair": "66+", "ax": "ATs+, AJo+", "broad": "KQs, QJs, JTs", "memo": "약간 확장"},
    "MP": {"pct": "18-20%", "pair": "55+", "ax": "A9s+, ATo+", "broad": "KTs+, QTs+, J9s+", "memo": "표준"},
    "LJ": {"pct": "20-22%", "pair": "44+", "ax": "A8s+, ATo+", "broad": "KTs+, QTs+, J9s+", "memo": "중후반"},
    "HJ": {"pct": "23-25%", "pair": "33+", "ax": "A7s+, A9o+", "broad": "K9s+, Q9s+, J9s+", "memo": "스틸 시작"},
    "CO": {"pct": "28-32%", "pair": "22+", "ax": "A2s+, A2o+", "broad": "K5s+, Q8s+, J8s+", "memo": "스틸 핵심"},
    "BTN": {"pct": "45-50%", "pair": "22+", "ax": "모든 Ax", "broad": "모든 수딧 K/Q", "memo": "가장 넓음"},
    "SB": {"pct": "38-42%", "pair": "22+", "ax": "A2s+, A2o+", "broad": "K2s+, Q5s+, J6s+", "memo": "믹스 선호"}
}

def get_poker_strategy(pos, v1, v2, suit, act):
    ranks = {"A":14, "K":13, "Q":12, "J":11, "T":10, "9":9, "8":8, "7":7, "6":6, "5":5, "4":4, "3":3, "2":2}
    r1, r2 = ranks[v1], ranks[v2]
    if r1 < r2: v1, v2 = v2, v1
    hand = f"{v1}{v2}{suit}"
    is_pair = (v1 == v2)

    if act == "Unopened (RFI)":
        if pos == "BB": return "⚪ CHECK/FOLD", "빅블라인드 상황입니다.", "N/A"
        p_data = stats[pos]
        
        # 기본 레이즈 로직 (간소화)
        if hand[:2] in ["AA", "KK", "QQ", "JJ", "AK"]:
            return "🔴 RAISE", "프리미엄 핸드: 밸류 빌딩 필수", p_data["pct"]
        
        if pos in ["BTN", "CO"] and (r1 >= 10 or suit == "s"):
            return "🔴 RAISE", f"{pos} 포지션: 적극적인 블라인드 스틸 구간", p_data["pct"]

        return "🔵 FOLD", "RFI 레인지 밖: 폴드 권장", p_data["pct"]

    return "🔵 FOLD", "Facing Raise: 타이트한 대응 필요", "N/A"

# --- 6. 결과 출력 ---
st.divider()
res, why, prob = get_poker_strategy(pos, v1, v2, suit, action)

if "RAISE" in res: st.error(f"## Action: {res}")
else: st.info(f"## Action: {res}")
st.write(f"📊 **포지션 오픈 확률:** {prob} | 💡 **이유:** {why}")

# --- 7. 최하단 핸드 레인지표 (이미지 데이터 기반) ---
st.markdown("---")
st.markdown("### 📊 RFI Range Reference Chart")
range_df = pd.DataFrame.from_dict(stats, orient='index')
range_df.columns = ['오픈%', '페어', '수딧/오프 Ax', '수딧 브로드웨이', '메모']
st.table(range_df)
