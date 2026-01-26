import streamlit as st

# 1. 앱 설정 (최상단 필수)
st.set_page_config(page_title="JM HOLDEM LEGEND 03 V1", page_icon="🃏", layout="centered")

# --- 타이틀 ---
st.title("🃏 JM HOLDEM LEGEND 03 V1")
st.error("⚠️ Unauthorized Distribution Prohibited (배포금지)")

# --- 2. 사이드바 (하이브리드 입력) ---
with st.sidebar:
    st.header("⚙️ Game Setup")
    env = st.selectbox("Env", ["Online", "Live Pub", "Tournament"])
    
    st.markdown("---")
    # Handy 하이브리드 입력
    h_in = st.number_input("Handy (Direct)", 2, 9, 6)
    handy = st.slider("Handy (Slider)", 2, 9, int(h_in))

    st.markdown("---")
    # Stack 하이브리드 입력 (25~1000)
    s_in = st.number_input("Stack BB (Direct)", 1, 1000, 100)
    s_opts = list(range(25, 1001, 25))
    def_s = int(s_in) if int(s_in) in s_opts else 100
    stack = st.select_slider("Stack BB (Slider)", options=s_opts, value=def_s)

# --- 3. 메인 화면 (상황 및 핸드 선택) ---
st.markdown("### 1. Situation")
# 포지션과 액션을 한 눈에 보이게 배치
col_pos, col_act = st.columns(2)
with col_pos:
    pos = st.selectbox("My Position", ["UTG", "MP", "CO", "BTN", "SB", "BB"])
with col_act:
    action = st.radio("Opponent Action", ["Unopened", "Raised"], horizontal=True)

st.markdown("---")

st.markdown("### 2. My Hand")
# 이미지 버튼을 없애고 깔끔한 선택창으로 통일
cards = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]

c1, c2, c3 = st.columns(3)
with c1:
    v1 = st.selectbox("Card 1", cards)
with c2:
    v2 = st.selectbox("Card 2", cards)
with c3:
    suit = st.radio("Suit Type", ["s", "o"], horizontal=True)

# --- 4. 전략 로직 ---
def get_logic(env, handy, stack, pos, v1, v2, suit, act):
    ranks = {"A":14, "K":13, "Q":12, "J":11, "T":10, "9":9, "8":8, "7":7, "6":6, "5":5, "4":4, "3":3, "2":2}
    r1, r2 = ranks[v1], ranks[v2]
    # 큰 숫자가 앞으로 오게 정렬
    if r1 < r2: v1, v2 = v2, v1
    hand = f"{v1}{v2}" + ("s" if suit == "s" and v1 != v2 else "")

    # 프리미엄 핸드 전략
    if hand in ["AA", "KK", "QQ", "AKs", "AKo", "JJ"]:
        return "🔴 RAISE / 3-BET", "가장 강력한 프리미엄 핸드입니다. 공격적으로 플레이하세요."
    
    # 딥스택(200BB+) 특수 전략
    if stack >= 200:
        if v1 == v2 and r1 <= 10:
            return "🟢 CALL (SET MINE)", "딥스택 상황입니다. 셋마이닝 배당을 노려보세요."
        if suit == "s" and abs(r1 - r2) <= 2:
            return "🟢 CALL (DRAW)", "포스트플랍 잠재력이 높은 수딧 커넥터 계열입니다."

    # 포지션 기반 스틸
    if pos in ["BTN", "CO"] and act == "Unopened":
        return "🟠 OPEN RAISE", f"{handy}인 상황, 포지션 이점을 활용해 공격하세요."

    return "🔵 FOLD", "수학적 기대값이 낮습니다. 다음 핸드를 기다리세요."

# --- 5. 결과 출력 ---
st.divider()
res, why = get_logic(env, handy, stack, pos, v1, v2, suit, action)

if "🔴" in res: st.error(f"## {res}")
elif "🟠" in res: st.warning(f"## {res}")
elif "🟢" in res: st.success(f"## {res}")
else: st.info(f"## {res}")

st.info(f"💡 **분석 결과:** {why}")

# --- 6. 복기 섹션 ---
with st.expander("📝 Quick Review"):
    rev_res = st.radio("Result", ["Win", "Loss"], horizontal=True)
    if st.button("Save Record"):
        st.success(f"저장되었습니다: {rev_res}")
