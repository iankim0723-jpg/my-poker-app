import streamlit as st

# 1. 앱 설정 (최상단 필수)
st.set_page_config(page_title="JM HOLDEM LEGEND 03 V1", page_icon="🃏", layout="centered")

# CSS: 모바일 7열 강제 고정 및 터치 최적화
st.markdown("""
    <style>
    /* 7열 배치를 강제하기 위한 컨테이너 설정 */
    [data-testid="column"] {
        padding: 0px 0.5px !important;
        flex: 1 1 0% !important;
        min-width: 0px !important;
        white-space: nowrap !important;
    }
    /* 버튼 디자인: 텍스트가 잘리지 않도록 폰트 크기 조절 */
    div.stButton > button {
        width: 100% !important;
        height: 42px !important;
        font-size: 13px !important;
        padding: 0px !important;
        border-radius: 4px !important;
        border: 1px solid #e0e0e0 !important;
        background-color: white !important;
    }
    /* 간격 최적화 */
    .stNumberInput { margin-bottom: -15px; }
    </style>
""", unsafe_allow_html=True)

# --- 타이틀 ---
st.title("🃏 JM HOLDEM LEGEND 03 V1")
st.error("⚠️ Unauthorized Distribution Prohibited (배포금지)")

# --- 2. 사이드바 (하이브리드 입력) ---
with st.sidebar:
    st.header("⚙️ Game Setup")
    env = st.selectbox("Environment", ["Online", "Live Pub", "Tournament"])
    
    st.markdown("---")
    # Handy 하이브리드
    h_input = st.number_input("Handy (Direct)", min_value=2, max_value=9, value=6)
    handy = st.slider("Handy (Slider)", 2, 9, int(h_input))

    st.markdown("---")
    # Stack 하이브리드 (25~1000)
    s_input = st.number_input("Stack BB (Direct)", min_value=1, max_value=1000, value=100)
    stack_opts = list(range(25, 1001, 25))
    def_s = int(s_input) if int(s_input) in stack_opts else 100
    stack = st.select_slider("Stack BB (Slider)", options=stack_opts, value=def_s)

# --- 3. 메인 화면 (상황 설정) ---
st.markdown("### 1. Situation")
pos = st.selectbox("My Position", ["UTG", "MP", "CO", "BTN", "SB", "BB"])
action = st.radio("Opponent Action", ["Unopened", "Raised"], horizontal=True)

st.markdown("---")

# --- 4. 카드 선택 (7x2 강제 버튼 배열) ---
st.markdown("### 2. Select Hand")
cards = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]

def card_picker(label):
    st.write(f"**{label}**")
    key_name = f"state_{label}"
    if key_name not in
