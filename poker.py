import streamlit as st
import pandas as pd
import os

# 1. 앱 기본 설정
st.set_page_config(page_title="JM LEGEND 03 (Master Agent)", page_icon="📈", layout="centered")

# --- 데이터 정의 ---
pos_list = ["UTG", "UTG+1", "MP", "LJ", "HJ", "CO", "BTN", "SB", "BB"]
cards = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]

# --- CSS: 적녹색약 배려 & 하이브리드 최적화 ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #111; border-right: 3px solid #D55E00; }
    .quote-box { background-color: #222; color: #fff; padding: 10px; border-radius: 8px; border: 2px solid #D55E00; text-align: center; font-weight: bold; font-size: 0.9em; margin-bottom: 10px; }
    .quote-author { color: #D55E00; font-size: 0.8em; margin-top: 5px; display: block; }
    .big-font { font-size: 1.3em; font-weight: 900; color: #fff; margin-top: 15px; margin-bottom: 5px; }
    
    .res-box-raise { background-color: #D55E00; color: white; padding: 15px; border-radius: 10px; text-align: center; font-size: 1.6em; font-weight: bold; margin: 10px 0; }
    .res-box-call { background-color: #0072B2; color: white; padding: 15px; border-radius: 10px; text-align: center; font-size: 1.6em; font-weight: bold; margin: 10px 0; }
    .res-box-fold { background-color: #333333; color: #BBBBBB; padding: 15px; border-radius: 10px; text-align: center; font-size: 1.6em; font-weight: bold; margin: 10px 0; border: 2px solid #555; }
    
    .ai-panel { background-color: #1e2630; border-left: 5px solid #00ccff; padding: 15px; border-radius: 5px; margin-top: 10px; }
    .ai-title { color: #00ccff; font-weight: bold; font-size: 1.1em; margin-bottom: 8px; }
    .ai-text { color: #d0d0d0; font-size: 0.95em; line-height: 1.5; }
    .highlight-stat { color: #ffeb3b; font-weight: bold; }
    
    div.stButton > button { width: 100%; height: 60px; font-size: 1.2em; border-radius: 10px; font-weight: bold; margin-bottom: 10px; }
    .chart-header { color: #D55E00; font-weight: bold; font-size: 1.1em; margin-top: 25px; margin-bottom: 5px; text-align: center; }
    
    /* 테이블 가독성 조정 */
    th { background-color: #222 !important; color: #D55E00 !important; text-align: center !important; }
    td { text-align: center !important; }
    </style>
""", unsafe_allow_html=True)

# --- [수정됨] 핸드레인지 순위표 팝업 (사용자 이미지 연동) ---
@st.dialog("🏆 텍사스 홀덤 프리플랍 핸드 순위 (1~169위)")
def show_hand_rankings():
    st.markdown("요청하신 **전체 169개 핸드 순위표**입니다.")
    st.caption("🟨 포켓(Pocket) | 🟥 수딧(Suited) | 🟦 오프수딧(Off suit)")
    
    # 1. 이미지 파일이 있으면 이미지 렌더링
    image_path = "핸드레이지 표.jpg"
    if os.path.exists(image_path):
        st.image(image_path, use_container_width=True)
    else:
        st.warning(f"⚠️ 이미지를 찾을 수 없습니다. '{image_path}' 파일을 이 파이썬 파일과 같은 폴더에 넣어주세요.")
    
    # 2. 혹시 모를 상황을 위한 텍스트 DB 백업 (Top 50)
    st.markdown("### 🔥 Top 50 텍스트 요약")
    df = pd.DataFrame({
        "순위": ["1~10위", "11~20위", "21~30위", "31~40위", "41~50위"],
        "핸드 리스트": [
            "AA, KK, QQ, AKs, JJ, AQs, KQs, AJs, KJs, TT",
            "AKo, ATs, QJs, KTs, QTs, JTs, 99, AQo, A9s, KQo",
            "88, K9s, T9s, A8s, Q9s, J9s, AJo, A5s, 77, A7s",
            "KJo, A4s, A3s, A6s, QJo, 66, K8s, T8s, A2s, 98s",
            "J8s, ATo, Q8s, K7s, KTo, 55, JTo, 87s, QTo, 44"
        ]
    })
    st.table(df)

# --- 2. 사이드바 (환경 및 스택 설정) ---
with st.sidebar:
    # 핸드 순위표 팝업 버튼
    if st.button("🏆 핸드 순위표 (Hand Rankings)", use_container_width=True):
        show_hand_rankings()
        
    st.header("⚙️ Game Environment")
    blind_level = st.number_input("Current Big Blind ($/Chips)", min_value=1, value=1000, step=100)
    st.caption(f"💡 현재 1BB = {blind_level:,}")
    
    st.markdown("---")
    st.header("🎯 Range Modifiers")
    env = st.selectbox("Play Environment", [
        "Live Pub (Loose/Wide) - 루즈한 방어", 
        "Online (Standard) - 표준 GTO", 
        "Competition (Tight) - 타이트한 생존"
    ], index=1)
    
    mode = st.radio("Game Type", [
        "Cash Game (Deep/Implied Odds)", 
        "Tournament (Survival/ICM)"
    ], index=1)
    
    st.markdown("---")
    st.header("💰 Stacks (BB)")
    my_stack = st.number_input("My Stack (BB)", 1.0, 1000.0, 50.0, step=1.0)
    villain_stack = st.number_input("Villain Stack (BB)", 1.0, 1000.0, 50.0, step=1.0)
    eff_stack = min(my_stack, villain_stack)
    st.metric("Effective Stack", f"{eff_stack} BB", f"약 {int(eff_stack * blind_level):,} 칩")

# --- 3. 메인 화면 ---
st.markdown("""
    <div class="quote-box">
        "한번 우승했다고 우쭐대지마라 그게 나락으로 가는 지름길이다"
        <span class="quote-author">- 더홀릭 우승 경험자 CBJ -</span>
    </div>
""", unsafe_allow_html=True)

st.title("🛡️ JM LEGEND 03")

# [1] Position (Hybrid)
st.markdown('<p class="big-font">📍 Position</p>', unsafe_allow_html=True)
c_p1, c_p2 = st.columns([3, 1.2])
with c_p1:
    pos_slider = st.select_slider("Pos Slider", options=pos_list, value="BTN", label_visibility="collapsed")
with c_p2:
    pos_box = st.selectbox("Pos Box", options=pos_list, index=pos_list.index(pos_slider), label_visibility="collapsed")
final_pos = pos_box 

# [2] Action
st.markdown('<p class="big-font">⚔️ Action</p>', unsafe_allow_html=True)
action = st.radio("Act", ["Unopened", "Facing Raise", "Facing All-in"], horizontal=True, label_visibility="collapsed")
final_amt = 0.0

if action == "Facing Raise":
    st.markdown("**상대 레이즈 (BB)**")
    c_r1, c_r2 = st.columns([2.5, 1.5])
    with c_r1:
        val_slider = st.slider("Raise Slider", 2.0, 15.0, 2.5, 0.5, label_visibility="collapsed")
    with c_r2:
        val_input = st.number_input("Raise Input", 0.0, 1000.0, val_slider, step=0.5, label_visibility="collapsed")
    final_amt = val_input

elif action == "Facing All-in":
    st.markdown("**상대 올인 (BB)**")
    max_val = float(villain_stack)
    c_a1, c_a2 = st.columns([2, 2])
    with c_a1:
        val_slider = st.slider("AI Slider", 1.0, max_val if max_val > 1 else 100.0, max_val/2, label_visibility="collapsed")
    with c_a2:
        val_input = st.number_input("AI Input", 1.0, 1000.0, val_slider, label_visibility="collapsed")
    final_amt = val_input

st.divider()

# [3] Hand
st.markdown('<p class="big-font">🃏 My Hand</p>', unsafe_allow_html=True)
c1_col, c2_col, s_col = st.columns([2.5, 2.5, 1.5])
with c1_col:
    v1_slider = st.select_slider("C1", cards, value="A", label_visibility="collapsed")
    v1 = st.selectbox("C1 Box", cards, index=cards.index(v1_slider), label_visibility="collapsed")
with c2_col:
    v2_slider = st.select_slider("C2", cards, value="K", label_visibility="collapsed")
    v2 = st.selectbox("C2 Box", cards, index=cards.index(v2_slider), label_visibility="collapsed")
with s_col:
    suit_radio = st.radio("S", ["s (수딧)", "o (오프)"], horizontal=True, label_visibility="collapsed")
    suit = "s" if "s" in suit_radio else "o"

# --- 4. MASTER AI EQUITY & ODDS ENGINE ---
def calculate_approx_equity(r1, r2, is_pair, is_s):
    base = (r1 + r2) * 1.5
    if is_pair: base = 50 + (r1 * 2.5) 
    if is_s: base += 5
    if r1 - r2 == 1: base += 3
    return min(85.0, max(25.0, base))

def run_master_analysis(mode, env, pos, v1, v2, suit, act, h_stack, e_stack, amt):
    rk = {"A":14, "K":13, "Q":12, "J":11, "T":10, "9":9, "8":8, "7":7, "6":6, "5":5, "4":4, "3":3, "2":2}
    r1, r2 = rk[v1], rk[v2]
    if r1 < r2: v1, v2, r1, r2 = v2, v1, r2, r1
    is_pair = (v1 == v2)
    is_s = (suit == "s")
    hand = f"{v1}{v2}{suit}" if not is_pair else f"{v1}{v2}"

    equity = calculate_approx_equity(r1, r2, is_pair, is_s)
    
    env_modifier = 0
    if "Live Pub" in env:

