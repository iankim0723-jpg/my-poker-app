import streamlit as st
import pandas as pd
import os

# 1. 앱 기본 설정 (반드시 최상단에 위치)
st.set_page_config(page_title="JM LEGEND 03 (Master Agent)", page_icon="📈", layout="centered")

# --- 양방향 동기화(Sync) 로직 & 세션 초기화 ---
if 'pos_slider' not in st.session_state: st.session_state.pos_slider = "BTN"
if 'pos_box' not in st.session_state: st.session_state.pos_box = "BTN"
if 'raise_slider' not in st.session_state: st.session_state.raise_slider = 2.5
if 'raise_box' not in st.session_state: st.session_state.raise_box = 2.5
if 'ai_slider' not in st.session_state: st.session_state.ai_slider = 25.0
if 'ai_box' not in st.session_state: st.session_state.ai_box = 25.0
if 'c1_slider' not in st.session_state: st.session_state.c1_slider = "A"
if 'c1_box' not in st.session_state: st.session_state.c1_box = "A"
if 'c2_slider' not in st.session_state: st.session_state.c2_slider = "K"
if 'c2_box' not in st.session_state: st.session_state.c2_box = "K"
if 'start_stack_input' not in st.session_state: st.session_state.start_stack_input = 50.0

def sync_pos_s2b(): st.session_state.pos_box = st.session_state.pos_slider
def sync_pos_b2s(): st.session_state.pos_slider = st.session_state.pos_box
def sync_raise_s2b(): st.session_state.raise_box = float(st.session_state.raise_slider)
def sync_raise_b2s(): st.session_state.raise_slider = min(max(st.session_state.raise_box, 2.0), 15.0)
def sync_ai_s2b(): st.session_state.ai_box = float(st.session_state.ai_slider)
def sync_ai_b2s():
    v_stack = st.session_state.start_stack_input
    max_val = float(v_stack) if v_stack > 1 else 100.0
    st.session_state.ai_slider = min(max(st.session_state.ai_box, 1.0), max_val)
def sync_c1_s2b(): st.session_state.c1_box = st.session_state.c1_slider
def sync_c1_b2s(): st.session_state.c1_slider = st.session_state.c1_box
def sync_c2_s2b(): st.session_state.c2_box = st.session_state.c2_slider
def sync_c2_b2s(): st.session_state.c2_slider = st.session_state.c2_box

# --- 방문자 카운트 로직 ---
counter_file = "visitor_count.txt"
if 'visited' not in st.session_state:
    st.session_state.visited = True
    if os.path.exists(counter_file):
        with open(counter_file, "r") as f:
            try: count = int(f.read().strip())
            except ValueError: count = 0
    else: count = 0
    count += 1
    with open(counter_file, "w") as f: f.write(str(count))
    st.session_state.v_count = count
else:
    if os.path.exists(counter_file):
        with open(counter_file, "r") as f:
            try: count = int(f.read().strip())
            except ValueError: count = st.session_state.v_count
    else: count = st.session_state.v_count

# --- 데이터 정의 ---
pos_list = ["UTG", "UTG+1", "MP", "LJ", "HJ", "CO", "BTN", "SB", "BB"]
cards = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]

# --- 🚨 글씨색/배경색 절대 강제 고정 CSS ---
st.markdown("""
    <style>
    /* 메인 화면(라이트 모드 강제): 흰 배경 + 검정 글씨 */
    .stApp { background-color: #ffffff !important; }
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp p, .stApp label, .stApp span { color: #111111 !important; }

    /* 사이드바(다크 모드 강제): 검정 배경 + 흰 글씨 */
    [data-testid="stSidebar"] { background-color: #111111 !important; border-right: 3px solid #D55E00 !important; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] [data-testid="stMetricValue"] { color: #ffffff !important; }

    /* 예외 1: 명언 박스 */
    .quote-box { background-color: #222222 !important; border: 2px solid #D55E00 !important; padding: 10px; border-radius: 8px; text-align: center; margin-bottom: 20px; }
    .quote-box, .quote-box p, .quote-box span { color: #ffffff !important; font-weight: bold !important; font-size: 0.9em !important; }
    .quote-author, .quote-author span { color: #D55E00 !important; font-size: 0.8em !important; margin-top: 5px; display: block; }
    
    /* 예외 2: 결과 액션 박스 */
    .res-box-raise, .res-box-raise p { background-color: #D55E00 !important; color: #ffffff !important; padding: 15px; border-radius: 10px; text-align: center; font-size: 1.6em !important; font-weight: bold !important; margin: 10px 0; }
    .res-box-call, .res-box-call p { background-color: #0072B2 !important; color: #ffffff !important; padding: 15px; border-radius: 10px; text-align: center; font-size: 1.6em !important; font-weight: bold !important; margin: 10px 0; }
    .res-box-fold, .res-box-fold p { background-color: #333333 !important; color: #BBBBBB !important; padding: 15px; border-radius: 10px; text-align: center; font-size: 1.6em !important; font-weight: bold !important; margin: 10px 0; border: 2px solid #555 !important; }
    
    /* 예외 3: AI 분석 리포트 박스 */
    .ai-panel { background-color: #1e2630 !important; border-left: 5px solid #00ccff !important; padding: 15px; border-radius: 5px; margin-top: 10px; }
    .ai-panel p, .ai-panel span { color: #d0d0d0 !important; font-size: 0.95em !important; line-height: 1.5 !important; }
    .ai-title, .ai-title span { color: #00ccff !important; font-weight: bold !important; font-size: 1.1em !important; margin-bottom: 8px; }
    .highlight-stat, .highlight-stat span { color: #ffeb3b !important; font-weight: bold !important; }

    /* 버튼 스타일 */
    div.stButton > button { width: 100%; height: 60px; font-size: 1.2em; border-radius: 10px; font-weight: bold; margin-bottom: 10px; }
    [data-testid="stSidebar"] button { background-color: #D55E00 !important; border: none !important; }
    [data-testid="stSidebar"] button p { color: #ffffff !important; }

    /* 메인 타이틀 */
    .big-font { font-size: 1.3em !important; font-weight: 900 !important; color: #111111 !important; margin-top: 15px; margin-bottom: 5px; }
    
    /* 테이블 스타일 */
    .chart-header { color: #D55E00 !important; font-weight: bold !important; font-size: 1.1em !important; margin-top: 25px; margin-bottom: 5px; text-align: center; }
    th { background-color: #222222 !important; color: #D55E00 !important; text-align: center !important; }
    td { background-color: #ffffff !important; color: #111111 !important; text-align: center !important; border: 1px solid #dddddd !important; }
    
    /* 🔥 상단 네비게이션 탭 (버튼 형식으로 디자인) */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: transparent !important; margin-bottom: 15px; }
    .stTabs [data-baseweb="tab"] { background-color: #e0e0e0 !important; border-radius: 8px !important; padding: 10px 20px !important; height: auto !important; }
    .stTabs [data-baseweb="tab"] p, .stTabs [data-baseweb="tab"] span { color: #555555 !important; font-weight: bold !important; font-size: 1.1em !important; }
    .stTabs [aria-selected="true"] { background-color: #111111 !important; border: 2px solid #D55E00 !important; }
    .stTabs [aria-selected="true"] p, .stTabs [aria-selected="true"] span { color: #ffffff !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. 사이드바 ---
with st.sidebar:
    st.markdown("### 🌐 Language / 언어")
    lang = st.radio("Language", ["한국어", "English"], horizontal=True, label_visibility="collapsed")
    is_kr = (lang == "한국어")
    
    st.markdown("---")
    
    @st.dialog("🏆 텍사스 홀덤 프리플랍 핸드 순위" if is_kr else "🏆 Texas Hold'em Pre-flop Hand Rankings")
    def show_hand_rankings():
        st.markdown("요청하신 **전체 169개 핸드 순위표**입니다." if is_kr else "Here is the **Top 169 Hand Rankings**.")
        st.caption("🟨 포켓(Pocket) | 🟥 수딧(Suited) | 🟦 오프수딧(Off suit)")
        image_path = "핸드레이지 표.png"
        if os.path.exists(image_path):
            st.image(image_path, use_container_width=True)
        else:
            st.warning("⚠️ 이미지를 찾을 수 없습니다. (Image not found)")

    if st.button("🏆 핸드 순위표 보기" if is_kr else "🏆 View Hand Rankings", use_container_width=True):
        show_hand_rankings()
        
    st.header("⚙️ 게임 환경 설정" if is_kr else "⚙️ Game Environment")
    blind_level = st.number_input("현재 빅 블라인드 ($/Chips)" if is_kr else "Current Big Blind ($/Chips)", min_value=1, value=1000, step=100)
    st.caption(f"💡 1BB = {blind_level:,}")
    
    st.markdown("---")
    st.header("🎯 레인지(범위) 설정" if is_kr else "🎯 Range Modifiers")
    
    env_options = ["라이브펍 (루즈/와이드)", "온라인 (표준 GTO)", "대회 (타이트/생존)"] if is_kr else ["Live Pub (Loose/Wide)", "Online (Standard)", "Competition (Tight)"]
    env_idx = env_options.index(st.selectbox("플레이 환경" if is_kr else "Play Environment", env_options, index=1))
    env_engine = ["Live Pub", "Online", "Competition"][env_idx]
    
    mode_options = ["캐시 게임 (딥스택/배당 콜)", "토너먼트 (생존/ICM)"] if is_kr else ["Cash Game (Deep/Implied Odds)", "Tournament (Survival/ICM)"]
    mode_idx = mode_options.index(st.radio("게임 모드" if is_kr else "Game Type", mode_options, index=1))
    mode_engine = ["Cash Game", "Tournament"][mode_idx]
    
    st.markdown("---")
    st.header("💰 시작 스택 설정" if is_kr else "💰 Start Stack Setup")
    start_stack = st.number_input("시작 스택 (BB)" if is_kr else "Start Stack (BB)", 1.0, 1000.0, 50.0, step=1.0, key="start_stack_input")
    eff_stack = start_stack 
    
    st.metric("유효 스택" if is_kr else "Effective Stack", f"{eff_stack} BB", f"약 {int(eff_stack * blind_level):,} 칩" if is_kr else f"~ {int(eff_stack * blind_level):,} Chips")

    st.markdown("---")
    visitor_text = "👁️ 누적 방문자 수" if is_kr else "👁️ Total Visitors"
    st.markdown(f"""
    <div style='text-align: center; padding: 15px; background-color: #1e1e1e; border-radius: 8px; border: 1px solid #444; margin-bottom: 20px;'>
        <span style='color: #00ccff !important; font-weight: bold; font-size: 1.1em;'>{visitor_text}</span><br>
        <span style='font-size: 2em; font-weight: 900; color: #ffffff !important;'>{count:,}</span><span style='color: #888888 !important; font-size: 0.9em;'> 명</span>
    </div>
    """, unsafe_allow_html=True)

# --- 3. 메인 화면 헤더 ---
st.title("🛡️ JM LEGEND 03")

# --- 🚀 핵심: 상단 네비게이션 탭 (홈 / 플랍 / 턴 / 리버) ---
tab_home, tab_flop, tab_turn, tab_river = st.tabs([
    "🏠 홈 (프리플랍)" if is_kr else "🏠 Home (Pre-flop)", 
    "🃏 포스트플랍 (플랍)" if is_kr else "🃏 Flop", 
    "🃏 턴 (Turn)", 
    "🃏 리버 (River)"
])

# ==========================================
# 🏠 [TAB 1] 프리플랍 (홈 화면) - 기존 로직 유지
# ==========================================
with tab_home:
    st.markdown("""
        <div class="quote-box">
            "한번 우승했다고 우쭐대지마라 그게 나락으로 가는 지름길이다"<br>
            <span class="quote-author">- 더홀릭 우승 경험자 CBJ -</span>
        </div>
    """, unsafe_allow_html=True)

    # [1] Position
    st.markdown(f'<p class="big-font">📍 {"나의 포지션" if is_kr else "My Position"}</p>', unsafe_allow_html=True)
    c_p1, c_p2 = st.columns([3, 1.2])
    with c_p1:
        st.select_slider("Pos Slider", options=pos_list, key="pos_slider", on_change=sync_pos_s2b, label_visibility="collapsed")
    with c_p2:
        st.selectbox("Pos Box", options=pos_list, key="pos_box", on_change=sync_pos_b2s, label_visibility="collapsed")
    final_pos = st.session_state.pos_box 

    # [2] Action
    st.markdown(f'<p class="big-font">⚔️ {"상황 (Action)" if is_kr else "Action"}</p>', unsafe_allow_html=True)
    act_options = ["오픈 전 (Unopened)", "상대 레이즈 (Facing Raise)", "상대 올인 (Facing All-in)"] if is_kr else ["Unopened", "Facing Raise", "Facing All-in"]
    act_idx = act_options.index(st.radio("Act", act_options, horizontal=True, label_visibility="collapsed"))
    act_engine = ["Unopened", "Facing Raise", "Facing All-in"][act_idx]

    final_amt = 0.0

    if act_engine == "Facing Raise":
        st.markdown(f"**{'상대 레이즈 (BB)' if is_kr else 'Opponent Raise (BB)'}**")
        c_r1, c_r2 = st.columns([2.5, 1.5])
        with c_r1:
            st.slider("Raise Slider", 2.0, 15.0, step=0.5, key="raise_slider", on_change=sync_raise_s2b, label_visibility="collapsed")
        with c_r2:
            st.number_input("Raise Input", 0.0, 1000.0, step=0.5, key="raise_box", on_change=sync_raise_b2s, label_visibility="collapsed")
        final_amt = st.session_state.raise_box

    elif act_engine == "Facing All-in":
        st.markdown(f"**{'상대 올인 (BB)' if is_kr else 'Opponent All-in (BB)'}**")
        max_val = float(eff_stack) if eff_stack > 1 else 100.0
        if st.session_state.ai_slider > max_val: st.session_state.ai_slider = max_val
        if st.session_state.ai_box > max_val: st.session_state.ai_box = max_val

        c_a1, c_a2 = st.columns([2, 2])
        with c_a1:
            st.slider("AI Slider", 1.0, max_val, key="ai_slider", on_change=sync_ai_s2b, label_visibility="collapsed")
        with c_a2:
            st.number_input("AI Input", 1.0, 1000.0, key="ai_box", on_change=sync_ai_b2s, label_visibility="collapsed")
        final_amt = st.session_state.ai_box

    st.divider()

    # [3] Hand
    st.markdown(f'<p class="big-font">🃏 {"나의 핸드 (My Hand)" if is_kr else "My Hand"}</p>', unsafe_allow_html=True)
    c1_col, c2_col, s_col = st.columns([2.5, 2.5, 1.5])
    with c1_col:
        st.select_slider("C1 Slider", cards, key="c1_slider", on_change=sync_c1_s2b, label_visibility="collapsed")
        st.selectbox("C1 Box", cards, key="c1_box", on_change=sync_c1_b2s, label_visibility="collapsed")
        v1 = st.session_state.c1_box
    with c2_col:
        st.select_slider("C2 Slider", cards, key="c2_slider", on_change=sync_c2_s2b, label_visibility="collapsed")
        st.selectbox("C2 Box", cards, key="c2_box", on_change=sync_c2_b2s, label_visibility="collapsed")
        v2 = st.session_state.c2_box
    with s_col:
        suit_options = ["s (수딧)", "o (오프)"] if is_kr else ["s (Suited)", "o (Off-suit)"]
        suit_idx = suit_options.index(st.radio("S", suit_options, horizontal=True, label_visibility="collapsed"))
        suit_engine = "s" if suit_idx == 0 else "o"

    # --- 4. MASTER AI EQUITY & ODDS ENGINE ---
    def calculate_approx_equity(r1, r2, is_pair, is_s):
        base = (r1 + r2) * 1.5
        if is_pair: base = 50 + (r1 * 2.5) 
        if is_s: base += 5
        if r1 - r2 == 1: base += 3
        return min(85.0, max(25.0, base))

    def run_master_analysis(mode, env, pos, v1, v2, suit, act, h_stack, e_stack, amt, is_kr):
        rk = {"A":14, "K":13, "Q":12, "J":11, "T":10, "9":9, "8":8, "7":7, "6":6, "5":5, "4":4, "3":3, "2":2}
        r1, r2 = rk[v1], rk[v2]
        if r1 < r2: v1, v2, r1, r2 = v2, v1, r2, r1
        is_pair = (v1 == v2)
        is_s = (suit == "s")
        hand = f"{v1}{v2}" if is_pair else f"{v1}{v2}{suit}"

        equity = calculate_approx_equity(r1, r2, is_pair, is_s)
        env_modifier = -5 if env == "Live Pub" else (5 if env == "Competition" else 0)

        analysis = []
        decision = "FOLD"
        
        if act == "Unopened":
            base_req = {"MP": 50, "LJ": 50, "HJ": 45, "CO": 45, "BTN": 40, "SB": 40}.get(pos, 55)
            req_equity = base_req + env_modifier
            
            if is_kr: analysis.append(f"이 핸드의 추정 승률(Equity)은 <span class='highlight-stat'>{equity:.1f}%</span> 입니다.")
            else: analysis.append(f"Estimated Equity of this hand is <span class='highlight-stat'>{equity:.1f}%</span>.")
            
            if h_stack <= 15:
                if equity >= 48:
                    decision = "RAISE"
                    analysis.append("스택이 15BB 이하이므로, 오픈 대신 <b>올인(Push)</b>을 통해 폴드 에퀴티를 극대화해야 합니다." if is_kr else "Stack is under 15BB. Maximize fold equity by pushing <b>All-in</b>.")
                else:
                    decision = "FOLD"
                    analysis.append("숏스택 상황에서 승부하기엔 에퀴티가 낮아 칩을 보존(Fold)해야 합니다." if is_kr else "Equity is too low for a short-stack shove. Fold and preserve chips.")
            elif equity >= req_equity:
                decision = "RAISE"
                analysis.append(f"현재 포지션({pos})의 오픈 최소 요구치({req_equity}%)를 상회하므로 수익성 있는 <b>레이즈(Raise)</b> 구간입니다." if is_kr else f"Exceeds minimum equity requirement ({req_equity}%) for {pos}. Profitable <b>Raise</b> spot.")
            else:
                decision = "FOLD"
                analysis.append(f"현재 포지션({pos})에서 먼저 팟을 열기에는 너무 약한 핸드(Fold)입니다." if is_kr else f"Hand is too weak to open from {pos}. Fold.")

        elif act == "Facing All-in":
            pot_odds = (amt / (amt + 1.5 + amt)) * 100
            
            if is_kr: analysis.append(f"내 핸드 에퀴티: <span class='highlight-stat'>{equity:.1f}%</span> / 요구 팟 오즈: <span class='highlight-stat'>{pot_odds:.1f}%</span>")
            else: analysis.append(f"Hand Equity: <span class='highlight-stat'>{equity:.1f}%</span> / Required Pot Odds: <span class='highlight-stat'>{pot_odds:.1f}%</span>")
            
            call_margin = 7 if mode == "Tournament" else 2
            
            if equity >= (pot_odds + call_margin):
                decision = "CALL"
                analysis.append(f"수학적으로 <b>장기적 수익(+EV)이 나는 콜(Call)</b>입니다." if is_kr else "Mathematically a <b>profitable (+EV) Call</b> in the long run.")
            else:
                decision = "FOLD"
                analysis.append(f"요구 배당이 더 높아 <b>손해(-EV)를 보는 구간</b>입니다. 폴드하십시오." if is_kr else "Required odds are higher than equity. This is a <b>-EV Spot</b>. Fold.")
                if mode == "Tournament":
                    analysis.append("특히 토너먼트는 목숨(ICM)이 걸려있으므로 확실한 우위가 아니면 피해야 합니다." if is_kr else "In tournaments, preserve your tournament life (ICM) unless holding a clear advantage.")

        elif act == "Facing Raise":
            if hand in ["AA", "KK", "QQ", "AKs", "AKo"]:
                decision = "RAISE"
                analysis.append("최상위 프리미엄 핸드입니다. 무조건 <b>3-Bet(리레이즈)</b>을 통해 판을 키우세요." if is_kr else "Absolute Premium Hand. Must <b>3-Bet (Re-raise)</b> to build the pot.")
            else:
                def_req = 48 + env_modifier
                if pos == "BB": def_req -= 8 
                if amt >= 6.0: 
                    def_req += 15 
                    analysis.append(f"상대가 {amt}BB의 큰 레이즈를 했습니다. 매우 강력한 레인지로 압축해야 합니다." if is_kr else f"Opponent made a huge raise ({amt}BB). Narrow down to a very strong range.")
                    
                if is_kr: analysis.append(f"현재 에퀴티: <span class='highlight-stat'>{equity:.1f}%</span> / 방어 컷오프: <span class='highlight-stat'>{def_req:.1f}%</span>")
                else: analysis.append(f"Current Equity: <span class='highlight-stat'>{equity:.1f}%</span> / Defense Cutoff: <span class='highlight-stat'>{def_req:.1f}%</span>")
                
                if equity >= def_req + 10:
                    decision = "RAISE"
                    analysis.append("상대의 레이즈 레인지를 압도합니다. 주도권을 뺏는 <b>3-Bet(레이즈)</b>이 정석입니다." if is_kr else "Dominates opponent's raising range. <b>3-Bet</b> to take the initiative.")
                elif equity >= def_req:
                    decision = "CALL"
                    if env == "Live Pub" and is_s:
                        analysis.append("라이브펍 특성상 멀티웨이 팟이 자주 나오므로 수딧/커넥터 류의 <b>배당 콜(Call)</b>이 매우 유리합니다." if is_kr else "Live Pubs feature multi-way pots. <b>Calling</b> with suited/connectors is highly profitable.")
                    elif mode == "Cash Game" and is_pair and r1 < 10 and (e_stack/amt) >= 20:
                        analysis.append("캐시게임 딥스택 <b>셋마이닝(Set Mining)</b> 조건이 성립합니다. 콜을 받고 셋을 맞추러 갑니다." if is_kr else "Deep stack <b>Set Mining</b> conditions met. Call to hit a set.")
                    else:
                        analysis.append("적절한 에퀴티를 보유하여 <b>방어(Call)</b> 후 포스트플랍 운영을 추천합니다." if is_kr else "Adequate equity to <b>Defend (Call)</b>. Proceed to post-flop.")
                else:
                    decision = "FOLD"
                    analysis.append("상대의 레이즈에 도미네잇(Dominated) 당할 확률이 높습니다. <b>폴드(Fold)</b>하세요." if is_kr else "High chance of being dominated. <b>Fold</b> immediately.")

        return decision, "<br>".join(analysis)

    # 결과 출력
    decision, reason_html = run_master_analysis(mode_engine, env_engine, final_pos, v1, v2, suit_engine, act_engine, eff_stack, eff_stack, final_amt, is_kr)

    st.divider()
    if decision == "RAISE":
        st.markdown(f'<div class="res-box-raise">{decision}</div>', unsafe_allow_html=True)
    elif decision == "CALL":
        st.markdown(f'<div class="res-box-call">{decision}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="res-box-fold">{decision}</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="ai-panel">
        <div class="ai-title">🤖 AI Agent Analysis Report</div>
        <div class="ai-text">{reason_html}</div>
    </div>
    """, unsafe_allow_html=True)

    # 하단 GTO 고정 차트
    st.markdown("---")
    st.markdown(f'<p class="chart-header">🚀 15BB Nash Equilibrium (Short Stack Push)</p>', unsafe_allow_html=True)
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

    st.markdown(f'<p class="chart-header">📊 100BB GTO RFI (Standard Range)</p>', unsafe_allow_html=True)
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

# ==========================================
# 🃏 [TAB 2] 플랍 (Flop) - 포스트플랍 준비 뼈대
# ==========================================
with tab_flop:
    st.markdown(f'<p class="big-font">🎴 보드 카드 입력 (Flop Board)</p>', unsafe_allow_html=True)
    st.info("💡 홈 화면(프리플랍)에서 입력한 내 핸드와 포지션 데이터가 자동으로 연동됩니다.")
    
    # 내 핸드 정보 표시 (홈 화면 데이터 연동)
    st.markdown(f"**현재 내 포지션:** `{st.session_state.pos_box}` | **내 핸드:** `{st.session_state.c1_box}` `{st.session_state.c2_box}` ({suit_engine})")
    
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        st.selectbox("Flop 1", cards, key="f1_card")
    with col_f2:
        st.selectbox("Flop 2", cards, key="f2_card")
    with col_f3:
        st.selectbox("Flop 3", cards, key="f3_card")
        
    st.divider()
    st.markdown(f'<p class="big-font">💰 팟 사이즈 및 액션 (Pot & Action)</p>', unsafe_allow_html=True)
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.number_input("현재 팟 크기 (BB)", min_value=1.0, value=10.0, step=1.0)
    with col_p2:
        st.selectbox("상대의 액션", ["Check (체크)", "Bet 1/3 Pot", "Bet 1/2 Pot", "Bet Full Pot", "All-in"])
        
    st.markdown(f"""
    <div class="ai-panel" style="border-left: 5px solid #D55E00;">
        <div class="ai-title" style="color: #D55E00;">🚧 포스트플랍 엔진 개발 준비 중...</div>
        <div class="ai-text">보드 텍스쳐 분석 및 팟 오즈 기반 GTO 액션(C-bet, Check-Raise 등) 모듈이 이곳에 탑재될 예정입니다.</div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 🃏 [TAB 3] 턴 (Turn)
# ==========================================
with tab_turn:
    st.markdown(f'<p class="big-font">🎴 턴 카드 입력 (Turn Card)</p>', unsafe_allow_html=True)
    st.selectbox("Turn", cards, key="t_card")
    
    st.markdown(f"""
    <div class="ai-panel" style="border-left: 5px solid #D55E00;">
        <div class="ai-title" style="color: #D55E00;">🚧 턴 런아웃 분석 엔진 개발 준비 중...</div>
        <div class="ai-text">에퀴티 변화(드로우 발전 등)에 따른 다이내믹 전략이 이곳에 탑재될 예정입니다.</div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 🃏 [TAB 4] 리버 (River)
# ==========================================
with tab_river:
    st.markdown(f'<p class="big-font">🎴 리버 카드 입력 (River Card)</p>', unsafe_allow_html=True)
    st.selectbox("River", cards, key="r_card")
    
    st.markdown(f"""
    <div class="ai-panel" style="border-left: 5px solid #D55E00;">
        <div class="ai-title" style="color: #D55E00;">🚧 리버 최종 쇼다운 엔진 개발 준비 중...</div>
        <div class="ai-text">넛(Nut) 어드밴티지 계산 및 블러프/밸류 벳 비율(MDF) 최적화 로직이 이곳에 탑재될 예정입니다.</div>
    </div>
    """, unsafe_allow_html=True)
