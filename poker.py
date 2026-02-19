import streamlit as st
import pandas as pd
import os

# 1. 앱 기본 설정 (반드시 최상단에 위치)
st.set_page_config(page_title="JM LEGEND 03 (Master Agent)", page_icon="📈", layout="centered")

# --- 방문자 카운트 로직 ---
counter_file = "visitor_count.txt"

# 세션에 'visited' 기록이 없으면(새로운 접속이면) 카운트 증가
if 'visited' not in st.session_state:
    st.session_state.visited = True
    if os.path.exists(counter_file):
        with open(counter_file, "r") as f:
            try:
                count = int(f.read().strip())
            except ValueError:
                count = 0
    else:
        count = 0
    
    count += 1
    # 증가된 카운트 저장
    with open(counter_file, "w") as f:
        f.write(str(count))
    st.session_state.v_count = count
else:
    # 이미 접속한 유저면 숫자만 읽어옴
    if os.path.exists(counter_file):
        with open(counter_file, "r") as f:
            try:
                count = int(f.read().strip())
            except ValueError:
                count = st.session_state.v_count
    else:
        count = st.session_state.v_count

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
    
    th { background-color: #222 !important; color: #D55E00 !important; text-align: center !important; }
    td { text-align: center !important; }
    </style>
""", unsafe_allow_html=True)

# --- 핸드레인지 순위표 팝업 (이미지 확장자 수정됨: .png) ---
@st.dialog("🏆 텍사스 홀덤 프리플랍 핸드 순위 (1~169위)")
def show_hand_rankings():
    st.markdown("요청하신 **전체 169개 핸드 순위표**입니다.")
    st.caption("🟨 포켓(Pocket) | 🟥 수딧(Suited) | 🟦 오프수딧(Off suit)")
    
    # [수정] 이미지 파일명을 깃허브에 올라간 .png로 변경
    image_path = "핸드레이지 표.png"
    if os.path.exists(image_path):
        st.image(image_path, use_container_width=True)
    else:
        st.warning(f"⚠️ 이미지를 찾을 수 없습니다. 깃허브에 '{image_path}' 파일이 제대로 올라가 있는지 확인해주세요.")
        
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

    # 사이드바 하단 방문자 카운터 UI
    st.markdown("---")
    st.markdown(f"""
    <div style='text-align: center; padding: 15px; background-color: #1e1e1e; border-radius: 8px; border: 1px solid #444; margin-bottom: 20px;'>
        <span style='color: #00ccff; font-weight: bold; font-size: 1.1em;'>👁️ 누적 방문자 수</span><br>
        <span style='font-size: 2em; font-weight: 900; color: white;'>{count:,}</span><span style='color: #888; font-size: 0.9em;'> 명</span>
    </div>
    """, unsafe_allow_html=True)

# --- 3. 메인 화면 ---
st.markdown("""
    <div class="quote-box">
        "한번 우승했다고 우쭐대지마라 그게 나락으로 가는 지름길이다"
        <span class="quote-author">- 더홀릭 우승 경험자 CBJ -</span>
    </div>
""", unsafe_allow_html=True)

st.title("🛡️ JM LEGEND 03")

# [1] Position (Hybrid) - [수정됨] "나의 포지션"으로 라벨 명확화
st.markdown('<p class="big-font">📍 나의 포지션 (My Position)</p>', unsafe_allow_html=True)
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
st.markdown('<p class="big-font">🃏 나의 핸드 (My Hand)</p>', unsafe_allow_html=True)
c1_col, c2_col, s_col = st.columns([2.5, 2.5, 1.5])
with c1_col:
    v1_slider = st.select_slider("C1", cards, value="A", label_visibility="collapsed")
    v1 = st.selectbox("C1 Box", cards, index=cards.index(v1_slider), label_visibility="collapsed")
with c2_col:
    v2_slider = st.select_slider("C2", cards, value="K", label_visibility="collapsed")
    v2 = st.selectbox("C2 Box", cards, index=cards.index(v2_slider), label_visibility="collapsed")
with s_col:
    suit_radio = st.radio("S", ["s (수딧)", "o (오프)"], horizontal=True, label_visibility="collapsed")
    if "s" in suit_radio:
        suit = "s"
    else:
        suit = "o"

# --- 4. MASTER AI EQUITY & ODDS ENGINE ---
def calculate_approx_equity(r1, r2, is_pair, is_s):
    base = (r1 + r2) * 1.5
    if is_pair:
        base = 50 + (r1 * 2.5) 
    if is_s:
        base += 5
    if r1 - r2 == 1:
        base += 3
    return min(85.0, max(25.0, base))

def run_master_analysis(mode, env, pos, v1, v2, suit, act, h_stack, e_stack, amt):
    rk = {"A":14, "K":13, "Q":12, "J":11, "T":10, "9":9, "8":8, "7":7, "6":6, "5":5, "4":4, "3":3, "2":2}
    r1, r2 = rk[v1], rk[v2]
    
    if r1 < r2:
        v1, v2 = v2, v1
        r1, r2 = r2, r1
        
    is_pair = (v1 == v2)
    is_s = (suit == "s")
    
    if is_pair:
        hand = f"{v1}{v2}"
    else:
        hand = f"{v1}{v2}{suit}"

    equity = calculate_approx_equity(r1, r2, is_pair, is_s)
    
    env_modifier = 0
    if "Live Pub" in env:
        env_modifier = -5
    elif "Competition" in env:
        env_modifier = 5

    analysis = []
    decision = "FOLD"
    
    if act == "Unopened":
        base_req = 55
        if pos in ["MP", "LJ"]:
            base_req = 50
        elif pos in ["HJ", "CO"]:
            base_req = 45
        elif pos in ["BTN", "SB"]:
            base_req = 40
        
        req_equity = base_req + env_modifier
        analysis.append(f"이 핸드의 추정 승률(Equity)은 <span class='highlight-stat'>{equity:.1f}%</span> 입니다.")
        
        if h_stack <= 15:
            if equity >= 48:
                decision = "RAISE"
                analysis.append(f"스택이 15BB 이하이므로, 오픈 대신 <b>올인(Push)</b>을 통해 폴드 에퀴티를 극대화해야 합니다.")
            else:
                decision = "FOLD"
                analysis.append("숏스택 상황에서 승부하기엔 에퀴티가 낮아 칩을 보존(Fold)해야 합니다.")
        elif equity >= req_equity:
            decision = "RAISE"
            analysis.append(f"현재 나의 포지션({pos})의 오픈 최소 요구치({req_equity}%)를 상회하므로 수익성 있는 <b>레이즈(Raise)</b> 구간입니다.")
        else:
            decision = "FOLD"
            analysis.append(f"현재 나의 포지션({pos})에서 먼저 팟을 열기에는 너무 약한 핸드(Fold)입니다.")

    elif act == "Facing All-in":
        call_amt = amt
        pot_size = amt + 1.5 
        pot_odds = (call_amt / (pot_size + call_amt)) * 100
        
        analysis.append(f"내 핸드 에퀴티: <span class='highlight-stat'>{equity:.1f}%</span> / 요구 팟 오즈: <span class='highlight-stat'>{pot_odds:.1f}%</span>")
        
        call_margin = 2
        if "Tournament" in mode:
            call_margin = 7 
        
        if equity >= (pot_odds + call_margin):
            decision = "CALL"
            analysis.append(f"내 핸드의 승률({equity:.1f}%)이 요구 배당({pot_odds:.1f}%)보다 높으므로 수학적으로 <b>장기적 수익(+EV)이 나는 콜(Call)</b>입니다.")
        else:
            decision = "FOLD"
            analysis.append(f"승률보다 요구 배당이 높아 <b>손해(-EV)를 보는 구간</b>입니다. 폴드하십시오.")
            if "Tournament" in mode:
                analysis.append("특히 토너먼트는 목숨(ICM)이 걸려있으므로 확실한 우위가 아니면 피해야 합니다.")

    elif act == "Facing Raise":
        if hand in ["AA", "KK", "QQ", "AKs", "AKo"]:
            decision = "RAISE"
            analysis.append("최상위 프리미엄 핸드입니다. 무조건 <b>3-Bet(리레이즈)</b>을 통해 팟을 키우고 상대의 밸류를 뽑아내야 합니다.")
        else:
            def_req = 48 + env_modifier
            if pos == "BB":
                def_req -= 8 
            
            if amt >= 6.0: 
                def_req += 15 
                analysis.append(f"상대가 {amt}BB의 큰 레이즈를 했습니다. 매우 강력한 레인지로 압축해야 합니다.")
                
            analysis.append(f"현재 핸드 에퀴티: <span class='highlight-stat'>{equity:.1f}%</span> / 방어 컷오프: <span class='highlight-stat'>{def_req:.1f}%</span>")
            
            if equity >= def_req + 10:
                decision = "RAISE"
                analysis.append("상대의 레이즈 레인지를 압도합니다. 주도권을 뺏는 <b>3-Bet(레이즈)</b>이 정석입니다.")
            elif equity >= def_req:
                decision = "CALL"
                if "Live Pub" in env and is_s:
                    analysis.append("라이브펍 특성상 멀티웨이 팟이 자주 나오므로 수딧/커넥터 류의 <b>배당 콜(Call)</b>이 매우 유리합니다.")
                elif "Cash" in mode and is_pair and r1 < 10 and (e_stack/amt) >= 20:
                    analysis.append("캐시게임 딥스택 <b>셋마이닝(Set Mining)</b> 조건이 성립합니다. 콜을 받고 셋을 맞추러 갑니다.")
                else:
                    analysis.append("적절한 에퀴티를 보유하여 <b>방어(Call)</b> 후 포스트플랍 운영을 추천합니다.")
            else:
                decision = "FOLD"
                analysis.append("상대의 레이즈에 도미네잇(Dominated) 당할 확률이 높습니다. <b>미련 없이 폴드(Fold)</b>하세요.")

    return decision, "<br>".join(analysis)

# --- 5. 결과 출력 ---
decision, reason_html = run_master_analysis(mode, env, final_pos, v1, v2, suit, action, my_stack, eff_stack, final_amt)

st.divider()
if decision == "RAISE":
    st.markdown(f'<div class="res-box-raise">{decision}</div>', unsafe_allow_html=True)
elif decision == "CALL":
    st.markdown(f'<div class="res-box-call">{decision}</div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div class="res-box-fold">{decision}</div>', unsafe_allow_html=True)

# 💡 상세 분석 패널
st.markdown(f"""
<div class="ai-panel">
    <div class="ai-title">🤖 AI Agent Analysis Report</div>
    <div class="ai-text">{reason_html}</div>
</div>
""", unsafe_allow_html=True)

# --- 6. 하단 GTO 고정 차트 ---
st.markdown("---")
st.markdown('<p class="chart-header">🚀 15BB Nash Equilibrium (Short Stack Push)</p>', unsafe_allow_html=True)
st.caption("※ 숏스택(소액 BB 소유) 시 포지션별 완벽한 올인 레인지입니다.")
st.table(pd.DataFrame({
    "Position": ["UTG / EP", "MP / HJ", "CO", "BTN", "SB"],
    "All-in Range": [
        "22+, A2s+, K8s+, Q9s+, J9s+, T9s, A8o+, KTo+, QJo",
        "22+, A2s+, K5s+, Q8s+, J8s+, T8s+, 98s, A5o+, KTo+, QTo+",
        "22+, A2s+, K2s+, Q5s+, J7s+, T7s+, 97s+, A2o+, K8o+, Q9o+",
        "22+, A2s+, K2s+, Q2s+, J2s+, T4s+, 95s+, 84s+, A2o+, K2o+",
        "Any Pair, Any Suited Ax/Kx, Q2s+, J2s+, Any Off-suit Ax/Kx"
    ]
}))

st.markdown('<p class="chart-header">📊 100BB GTO RFI (Standard Range)</p>', unsafe_allow_html=True)
st.caption("※ 정상 스택 포지션별 정석 오픈(Raise First In) 레인지입니다.")
tab1, tab2, tab3 = st.tabs(["Early (UTG/MP)", "Late (CO/BTN)", "Blinds (SB)"])

with tab1:
    st.table(pd.DataFrame({
        "Pos": ["UTG", "MP"],
        "Pairs": ["77+", "55+"],
        "Suited": ["ATs+, KTs+, QTs+, JTs", "A9s+, K9s+, Q9s+, J9s"],
        "Off-suit": ["AQo+", "AJo+, KQo"]
    }))
with tab2:
    st.table(pd.DataFrame({
        "Pos": ["CO", "BTN"],
        "Pairs": ["22+", "22+"],
        "Suited": ["A2s+, K5s+, Q8s+, J8s+, T8s+, 97s+", "A2s+, K2s+, Q2s+, J5s+, T6s+, 96s+"],
        "Off-suit": ["ATo+, KTo+, QJo", "A2o+, K8o+, Q9o+, J9o+, T9o"]
    }))
with tab3:
    st.table(pd.DataFrame({
        "Pos": ["SB"],
        "Pairs": ["22+"],
        "Suited": ["A2s+, K2s+, Q4s+, J6s+, T6s+, 96s+"],
        "Off-suit": ["A9o+, KTo+, QTo+, JTo"]
    }))
