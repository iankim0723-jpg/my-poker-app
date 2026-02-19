import streamlit as st
import pandas as pd
import os

# 1. 앱 기본 설정
st.set_page_config(page_title="JM LEGEND 03 (Master Agent)", page_icon="📈", layout="centered")

# --- 양방향 동기화(Sync) 로직 & 세션 초기화 ---
sync_keys = [
    'pos', 'raise', 'ai', 'c1', 'c2', 
    'f1', 'f2', 'f3', 't', 'r', 
    'vc1', 'vc2'
]
for k in sync_keys:
    if f'{k}_slider' not in st.session_state: st.session_state[f'{k}_slider'] = "A" if k not in ['raise', 'ai', 'pos'] else ("BTN" if k == 'pos' else 2.5 if k == 'raise' else 25.0)
    if f'{k}_box' not in st.session_state: st.session_state[f'{k}_box'] = "A" if k not in ['raise', 'ai', 'pos'] else ("BTN" if k == 'pos' else 2.5 if k == 'raise' else 25.0)

if 'start_stack_input' not in st.session_state: st.session_state.start_stack_input = 50.0

def create_sync_callbacks(key, is_number=False):
    def s2b(): st.session_state[f'{key}_box'] = float(st.session_state[f'{key}_slider']) if is_number else st.session_state[f'{key}_slider']
    def b2s(): 
        if is_number:
            if key == 'raise': st.session_state[f'{key}_slider'] = min(max(st.session_state[f'{key}_box'], 2.0), 15.0)
            elif key == 'ai': st.session_state[f'{key}_slider'] = min(max(st.session_state[f'{key}_box'], 1.0), max(st.session_state.start_stack_input, 100.0))
        else:
            st.session_state[f'{key}_slider'] = st.session_state[f'{key}_box']
    return s2b, b2s

cb_pos_s2b, cb_pos_b2s = create_sync_callbacks('pos')
cb_raise_s2b, cb_raise_b2s = create_sync_callbacks('raise', True)
cb_ai_s2b, cb_ai_b2s = create_sync_callbacks('ai', True)
cb_c1_s2b, cb_c1_b2s = create_sync_callbacks('c1')
cb_c2_s2b, cb_c2_b2s = create_sync_callbacks('c2')
cb_f1_s2b, cb_f1_b2s = create_sync_callbacks('f1')
cb_f2_s2b, cb_f2_b2s = create_sync_callbacks('f2')
cb_f3_s2b, cb_f3_b2s = create_sync_callbacks('f3')
cb_t_s2b, cb_t_b2s = create_sync_callbacks('t')
cb_r_s2b, cb_r_b2s = create_sync_callbacks('r')

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
    /* 메인 화면: 흰 배경 + 검정 글씨 */
    .stApp { background-color: #ffffff !important; }
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp p, .stApp label, .stApp span, .stApp div[data-baseweb="base-input"] { color: #111111 !important; }

    /* 사이드바: 검정 배경 + 흰 글씨 */
    [data-testid="stSidebar"] { background-color: #111111 !important; border-right: 3px solid #D55E00 !important; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] [data-testid="stMetricValue"] { color: #ffffff !important; }

    /* 명언 박스 */
    .quote-box { background-color: #222222 !important; border: 2px solid #D55E00 !important; padding: 10px; border-radius: 8px; text-align: center; margin-bottom: 20px; }
    .quote-box, .quote-box p, .quote-box span { color: #ffffff !important; font-weight: bold !important; font-size: 0.9em !important; }
    .quote-author, .quote-author span { color: #D55E00 !important; font-size: 0.8em !important; margin-top: 5px; display: block; }
    
    /* 결과 박스 */
    .res-box-raise, .res-box-raise p { background-color: #D55E00 !important; color: #ffffff !important; padding: 15px; border-radius: 10px; text-align: center; font-size: 1.6em !important; font-weight: bold !important; margin: 10px 0; }
    .res-box-call, .res-box-call p { background-color: #0072B2 !important; color: #ffffff !important; padding: 15px; border-radius: 10px; text-align: center; font-size: 1.6em !important; font-weight: bold !important; margin: 10px 0; }
    .res-box-fold, .res-box-fold p { background-color: #333333 !important; color: #BBBBBB !important; padding: 15px; border-radius: 10px; text-align: center; font-size: 1.6em !important; font-weight: bold !important; margin: 10px 0; border: 2px solid #555 !important; }
    
    /* AI 패널 */
    .ai-panel { background-color: #1e2630 !important; border-left: 5px solid #00ccff !important; padding: 15px; border-radius: 5px; margin-top: 10px; }
    .ai-panel p, .ai-panel span { color: #d0d0d0 !important; font-size: 0.95em !important; line-height: 1.5 !important; }
    .ai-title, .ai-title span { color: #00ccff !important; font-weight: bold !important; font-size: 1.1em !important; margin-bottom: 8px; }
    .highlight-stat, .highlight-stat span { color: #ffeb3b !important; font-weight: bold !important; }

    /* 공통 버튼 & 텍스트 */
    div.stButton > button { width: 100%; height: 60px; font-size: 1.2em; border-radius: 10px; font-weight: bold; margin-bottom: 10px; }
    [data-testid="stSidebar"] button { background-color: #D55E00 !important; border: none !important; }
    [data-testid="stSidebar"] button p { color: #ffffff !important; }
    .big-font { font-size: 1.3em !important; font-weight: 900 !important; color: #111111 !important; margin-top: 15px; margin-bottom: 5px; }
    
    /* 하단 차트 */
    .chart-header { color: #D55E00 !important; font-weight: bold !important; font-size: 1.1em !important; margin-top: 25px; margin-bottom: 5px; text-align: center; }
    th { background-color: #222222 !important; color: #D55E00 !important; text-align: center !important; }
    td { background-color: #ffffff !important; color: #111111 !important; text-align: center !important; border: 1px solid #dddddd !important; }
    
    /* 탭 스타일 */
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
        if os.path.exists(image_path): st.image(image_path, use_container_width=True)
        else: st.warning("⚠️ 이미지를 찾을 수 없습니다. (Image not found)")

    if st.button("🏆 핸드 순위표 보기" if is_kr else "🏆 View Hand Rankings", use_container_width=True):
        show_hand_rankings()
        
    st.header("⚙️ 게임 환경 설정" if is_kr else "⚙️ Game Environment")
    blind_level = st.number_input("현재 빅 블라인드 ($/Chips)" if is_kr else "Current Big Blind ($/Chips)", min_value=1, value=1000, step=100)
    
    st.markdown("---")
    env_options = ["라이브펍 (루즈/와이드)", "온라인 (표준 GTO)", "대회 (타이트/생존)"] if is_kr else ["Live Pub (Loose/Wide)", "Online (Standard)", "Competition (Tight)"]
    env_idx = env_options.index(st.selectbox("플레이 환경" if is_kr else "Play Environment", env_options, index=1))
    env_engine = ["Live Pub", "Online", "Competition"][env_idx]
    
    mode_options = ["캐시 게임 (딥스택/배당 콜)", "토너먼트 (생존/ICM)"] if is_kr else ["Cash Game (Deep/Implied Odds)", "Tournament (Survival/ICM)"]
    mode_idx = mode_options.index(st.radio("게임 모드" if is_kr else "Game Type", mode_options, index=1))
    mode_engine = ["Cash Game", "Tournament"][mode_idx]
    
    st.markdown("---")
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

# --- 🧠 프리플랍 엔진 (기존 완벽 버전 고정) ---
def calculate_approx_equity(r1, r2, is_pair, is_s):
    base = (r1 + r2) * 1.5
    if is_pair: base = 50 + (r1 * 2.5) 
    if is_s: base += 5
    if r1 - r2 == 1: base += 3
    return min(85.0, max(25.0, base))

def run_preflop_analysis(mode, env, pos, v1, v2, suit, act, h_stack, e_stack, amt, is_kr):
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

# --- 🧠 복기 전용: 포스트플랍 엔진 (오답 노트) ---
def run_review_engine(street, pot_size, bet_size, my_made, my_draw, v_known, v_made, is_kr):
    call_amt = bet_size
    total_pot = pot_size + bet_size + call_amt
    pot_odds = (call_amt / total_pot) * 100 if total_pot > 0 else 0
    
    outs = 0
    if "플러시" in my_draw: outs += 9
    if "양차" in my_draw: outs += 8
    if "빵꾸" in my_draw: outs += 4
    
    multiplier = 4 if street == "Flop" else (2 if street == "Turn" else 0)
    draw_equity = outs * multiplier
    
    made_value = 0
    if my_made == "탑 페어": made_value = 60
    elif my_made == "투 페어": made_value = 75
    elif my_made == "셋 (Set) 이상": made_value = 90
    elif my_made == "미들/바텀 페어": made_value = 35

    total_equity = max(draw_equity, made_value)

    analysis = []
    decision = "FOLD"
    
    analysis.append(f"<b>[상황 진단]</b> 현재 팟: {pot_size}BB | 요구 배당(Pot Odds): <span class='highlight-stat'>{pot_odds:.1f}%</span>")
    
    if v_known:
        v_value = 0
        if v_made == "탑 페어": v_value = 60
        elif v_made == "투 페어": v_value = 75
        elif v_made == "셋 (Set) 이상": v_value = 90
        elif v_made == "스트레이트/플러시 이상": v_value = 100
        
        analysis.append(f"<b>[결과 확인]</b> 상대는 '{v_made}' 였습니다.")
        
        if total_equity >= pot_odds:
            decision = "CALL (GTO Correct)"
            if v_value > total_equity:
                analysis.append("💡 <b>[오답 노트 - 억울한 패배]</b> 수학적으로 당시 내 에퀴티가 배당을 충족했습니다. <b>여기서 콜을 받은 것은 잘못이 아닙니다 (GTO 정답).</b> 쿨러(Cooler)였을 뿐이니 결과에 쫄아서 다음번에 오버폴드 하지 마세요!")
            else:
                analysis.append("💡 <b>[오답 노트 - 나이스 콜]</b> 결과도 이겼고, 수학적으로도 올바른 완벽한 콜(또는 밸류벳)이었습니다. 훌륭합니다!")
        else:
            decision = "FOLD (GTO Correct)"
            if v_value < total_equity:
                analysis.append("💡 <b>[오답 노트 - 운 좋은 승리]</b> 상대가 블러핑을 쳐서 내가 먹었을지 모르나, 배당이 안 맞는데 콜을 한 <b>잘못된 플레이(-EV)</b>입니다. 이런 플레이가 반복되면 장기적으로 돈을 잃습니다. 폴드하세요.")
            else:
                analysis.append("💡 <b>[오답 노트 - 굿 폴드]</b> 상대 패도 강했고 배당도 안 맞았습니다. 여기서 미련 없이 칩을 아낀(Fold) 당신의 결단력이 토너먼트 생존의 핵심입니다.")
    else:
        analysis.append("상대 패를 모르는 상태(블라인드)에서의 GTO 권장 액션입니다.")
        if bet_size == 0:
            decision = "CHECK / BET"
            analysis.append("상대가 체크했습니다. 내 핸드에 따라 밸류를 뽑거나 팟 컨트롤을 하세요.")
        else:
            if total_equity >= pot_odds:
                decision = "CALL / RAISE"
                analysis.append(f"내 핸드의 추정 에퀴티(<span class='highlight-stat'>{total_equity:.1f}%</span>)가 팟 오즈보다 높습니다. 수학적으로 이득이 나는 방어 구간입니다.")
            else:
                decision = "FOLD"
                analysis.append("에퀴티나 아웃츠가 부족합니다. 상대의 베팅에 미련 없이 폴드하세요.")

    return decision, "<br>".join(analysis)


# --- 3. 메인 화면 ---
st.title("🛡️ JM LEGEND 03")

tab_home, tab_flop, tab_turn, tab_river = st.tabs([
    "🏠 홈 (프리플랍)" if is_kr else "🏠 Home", 
    "🃏 플랍 (Flop)", 
    "🃏 턴 (Turn)", 
    "🃏 리버 (River)"
])

# ==========================================
# 🏠 [TAB 1] 프리플랍 (기존 완벽 버전 영구 고정)
# ==========================================
with tab_home:
    st.markdown("""<div class="quote-box">"한번 우승했다고 우쭐대지마라 그게 나락으로 가는 지름길이다"<br><span class="quote-author">- 더홀릭 우승 경험자 CBJ -</span></div>""", unsafe_allow_html=True)
    
    st.markdown('<p class="big-font">📍 나의 포지션 (My Position)</p>', unsafe_allow_html=True)
    c_p1, c_p2 = st.columns([3, 1.2])
    with c_p1: st.select_slider("Pos Slider", options=pos_list, key="pos_slider", on_change=cb_pos_s2b, label_visibility="collapsed")
    with c_p2: st.selectbox("Pos Box", options=pos_list, key="pos_box", on_change=cb_pos_b2s, label_visibility="collapsed")
    final_pos = st.session_state.pos_box 

    st.markdown('<p class="big-font">⚔️ 상황 (Action)</p>', unsafe_allow_html=True)
    act_idx = ["오픈 전 (Unopened)", "상대 레이즈 (Facing Raise)", "상대 올인 (Facing All-in)"].index(
        st.radio("Act", ["오픈 전 (Unopened)", "상대 레이즈 (Facing Raise)", "상대 올인 (Facing All-in)"] if is_kr else ["Unopened", "Facing Raise", "Facing All-in"], horizontal=True, label_visibility="collapsed")
    )
    act_engine = ["Unopened", "Facing Raise", "Facing All-in"][act_idx]
    final_amt = 0.0

    if act_engine == "Facing Raise":
        st.markdown("**상대 레이즈 (BB)**" if is_kr else "**Opponent Raise (BB)**")
        c_r1, c_r2 = st.columns([2.5, 1.5])
        with c_r1: st.slider("Raise Slider", 2.0, 15.0, step=0.5, key="raise_slider", on_change=cb_raise_s2b, label_visibility="collapsed")
        with c_r2: st.number_input("Raise Input", 0.0, 1000.0, step=0.5, key="raise_box", on_change=cb_raise_b2s, label_visibility="collapsed")
        final_amt = st.session_state.raise_box
    elif act_engine == "Facing All-in":
        st.markdown("**상대 올인 (BB)**" if is_kr else "**Opponent All-in (BB)**")
        max_val = float(eff_stack) if eff_stack > 1 else 100.0
        c_a1, c_a2 = st.columns([2, 2])
        with c_a1: st.slider("AI Slider", 1.0, max_val, key="ai_slider", on_change=cb_ai_s2b, label_visibility="collapsed")
        with c_a2: st.number_input("AI Input", 1.0, 1000.0, key="ai_box", on_change=cb_ai_b2s, label_visibility="collapsed")
        final_amt = st.session_state.ai_box

    st.markdown('<p class="big-font">🃏 나의 핸드 (My Hand)</p>', unsafe_allow_html=True)
    c1_col, c2_col, s_col = st.columns([2.5, 2.5, 1.5])
    with c1_col:
        st.select_slider("C1 Slider", cards, key="c1_slider", on_change=cb_c1_s2b, label_visibility="collapsed")
        st.selectbox("C1 Box", cards, key="c1_box", on_change=cb_c1_b2s, label_visibility="collapsed")
        v1 = st.session_state.c1_box
    with c2_col:
        st.select_slider("C2 Slider", cards, key="c2_slider", on_change=cb_c2_s2b, label_visibility="collapsed")
        st.selectbox("C2 Box", cards, key="c2_box", on_change=cb_c2_b2s, label_visibility="collapsed")
        v2 = st.session_state.c2_box
    with s_col:
        suit_idx = ["s", "o"].index("s" if "s" in st.radio("S", ["s (수딧)", "o (오프)"] if is_kr else ["s (Suited)", "o (Off-suit)"], horizontal=True, label_visibility="collapsed") else "o")
        suit_engine = "s" if suit_idx == 0 else "o"

    # [프리플랍 결과 출력 100% 유지]
    decision, reason_html = run_preflop_analysis(mode_engine, env_engine, final_pos, v1, v2, suit_engine, act_engine, eff_stack, eff_stack, final_amt, is_kr)

    st.divider()
    if decision == "RAISE": st.markdown(f'<div class="res-box-raise"><p>{decision}</p></div>', unsafe_allow_html=True)
    elif decision == "CALL": st.markdown(f'<div class="res-box-call"><p>{decision}</p></div>', unsafe_allow_html=True)
    else: st.markdown(f'<div class="res-box-fold"><p>{decision}</p></div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="ai-panel">
        <div class="ai-title"><span>🤖 AI Agent Analysis Report</span></div>
        <div class="ai-text">{reason_html}</div>
    </div>
    """, unsafe_allow_html=True)

    # 🚨 [하단 차트 오타 수정됨 & 영구 유지]
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
# 🃏 [TAB 2] 플랍 (Flop) - 복기 모드
# ==========================================
with tab_flop:
    st.markdown('<p class="big-font">🎴 보드 카드 입력 (Flop)</p>', unsafe_allow_html=True)
    c_f1, c_f2, c_f3 = st.columns(3)
    with c_f1:
        st.select_slider("F1 Slider", cards, key="f1_slider", on_change=cb_f1_s2b, label_visibility="collapsed")
        st.selectbox("F1 Box", cards, key="f1_box", on_change=cb_f1_b2s, label_visibility="collapsed")
    with c_f2:
        st.select_slider("F2 Slider", cards, key="f2_slider", on_change=cb_f2_s2b, label_visibility="collapsed")
        st.selectbox("F2 Box", cards, key="f2_box", on_change=cb_f2_b2s, label_visibility="collapsed")
    with c_f3:
        st.select_slider("F3 Slider", cards, key="f3_slider", on_change=cb_f3_s2b, label_visibility="collapsed")
        st.selectbox("F3 Box", cards, key="f3_box", on_change=cb_f3_b2s, label_visibility="collapsed")

    st.markdown('<p class="big-font">🕵️ 나의 상황 (My Status)</p>', unsafe_allow_html=True)
    c_m1, c_m2 = st.columns(2)
    with c_m1: my_made_f = st.selectbox("현재 메이드 상태", ["노 페어 (에어)", "미들/바텀 페어", "탑 페어", "투 페어", "셋 (Set) 이상"], key="my_made_f")
    with c_m2: my_draw_f = st.selectbox("현재 드로우 상태", ["없음", "빵꾸 (Gutshot)", "양차 (OESD)", "플러시 드로우", "플러시+양차 콤보"], key="my_draw_f")

    st.markdown('<p class="big-font">💰 팟 & 액션</p>', unsafe_allow_html=True)
    c_p1, c_p2 = st.columns(2)
    with c_p1: pot_f = st.number_input("현재 팟 (BB)", 1.0, 1000.0, 10.0, step=1.0, key="pot_f")
    with c_p2: bet_f = st.number_input("상대 베팅 (BB) [체크=0]", 0.0, 1000.0, 3.0, step=1.0, key="bet_f")

    st.markdown("---")
    st.markdown('<p class="big-font">👿 상대방 핸드 (쇼다운 복기용)</p>', unsafe_allow_html=True)
    v_known_f = st.checkbox("쇼다운 결과 (상대 패) 확인 여부", key="v_known_f")
    v_made_f = "노 페어 (에어)"
    if v_known_f:
        v_made_f = st.selectbox("상대가 들고 있던 패는?", ["노 페어 (블러프/에어)", "미들/바텀 페어", "탑 페어", "투 페어", "셋 (Set) 이상", "스트레이트/플러시 이상"], key="v_made_box_f")

    dec_f, res_f = run_review_engine("Flop", pot_f, bet_f, my_made_f, my_draw_f, v_known_f, v_made_f, is_kr)
    
    st.divider()
    if "RAISE" in dec_f or "BET" in dec_f or "CALL" in dec_f: st.markdown(f'<div class="res-box-call"><p>{dec_f}</p></div>', unsafe_allow_html=True)
    else: st.markdown(f'<div class="res-box-fold"><p>{dec_f}</p></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="ai-panel"><div class="ai-title"><span>🤖 GTO Review & Feedback</span></div><div class="ai-text">{res_f}</div></div>', unsafe_allow_html=True)

# ==========================================
# 🃏 [TAB 3] 턴 (Turn) - 복기 모드
# ==========================================
with tab_turn:
    st.markdown('<p class="big-font">🎴 턴 카드 입력 (Turn)</p>', unsafe_allow_html=True)
    c_t1, c_t2 = st.columns([3, 1.2])
    with c_t1:
        st.select_slider("T Slider", cards, key="t_slider", on_change=cb_t_s2b, label_visibility="collapsed")
    with c_t2:
        st.selectbox("T Box", cards, key="t_box", on_change=cb_t_b2s, label_visibility="collapsed")

    st.markdown('<p class="big-font">🕵️ 나의 상황 (My Status)</p>', unsafe_allow_html=True)
    c_tm1, c_tm2 = st.columns(2)
    with c_tm1: my_made_t = st.selectbox("현재 메이드 상태", ["노 페어 (에어)", "미들/바텀 페어", "탑 페어", "투 페어", "셋 (Set) 이상"], key="my_made_t")
    with c_tm2: my_draw_t = st.selectbox("현재 드로우 상태", ["없음", "빵꾸 (Gutshot)", "양차 (OESD)", "플러시 드로우", "플러시+양차 콤보"], key="my_draw_t")

    st.markdown('<p class="big-font">💰 팟 & 액션</p>', unsafe_allow_html=True)
    c_tp1, c_tp2 = st.columns(2)
    with c_tp1: pot_t = st.number_input("현재 팟 (BB)", 1.0, 1000.0, 20.0, step=1.0, key="pot_t")
    with c_tp2: bet_t = st.number_input("상대 베팅 (BB) [체크=0]", 0.0, 1000.0, 10.0, step=1.0, key="bet_t")

    st.markdown("---")
    st.markdown('<p class="big-font">👿 상대방 핸드 (쇼다운 복기용)</p>', unsafe_allow_html=True)
    v_known_t = st.checkbox("쇼다운 결과 (상대 패) 확인 여부", key="v_known_t")
    v_made_t = "노 페어 (에어)"
    if v_known_t:
        v_made_t = st.selectbox("상대가 들고 있던 패는?", ["노 페어 (블러프/에어)", "미들/바텀 페어", "탑 페어", "투 페어", "셋 (Set) 이상", "스트레이트/플러시 이상"], key="v_made_box_t")

    dec_t, res_t = run_review_engine("Turn", pot_t, bet_t, my_made_t, my_draw_t, v_known_t, v_made_t, is_kr)
    
    st.divider()
    if "RAISE" in dec_t or "BET" in dec_t or "CALL" in dec_t: st.markdown(f'<div class="res-box-call"><p>{dec_t}</p></div>', unsafe_allow_html=True)
    else: st.markdown(f'<div class="res-box-fold"><p>{dec_t}</p></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="ai-panel"><div class="ai-title"><span>🤖 GTO Review & Feedback</span></div><div class="ai-text">{res_t}</div></div>', unsafe_allow_html=True)

# ==========================================
# 🃏 [TAB 4] 리버 (River) - 복기 모드
# ==========================================
with tab_river:
    st.markdown('<p class="big-font">🎴 리버 카드 입력 (River)</p>', unsafe_allow_html=True)
    c_r1, c_r2 = st.columns([3, 1.2])
    with c_r1:
        st.select_slider("R Slider", cards, key="r_slider", on_change=cb_r_s2b, label_visibility="collapsed")
    with c_r2:
        st.selectbox("R Box", cards, key="r_box", on_change=cb_r_b2s, label_visibility="collapsed")

    st.markdown('<p class="big-font">🕵️ 나의 상황 (My Status)</p>', unsafe_allow_html=True)
    my_made_r = st.selectbox("최종 메이드 상태 (리버는 드로우 없음)", ["노 페어 (에어)", "미들/바텀 페어", "탑 페어", "투 페어", "셋 (Set) 이상"], key="my_made_r")

    st.markdown('<p class="big-font">💰 팟 & 액션</p>', unsafe_allow_html=True)
    c_rp1, c_rp2 = st.columns(2)
    with c_rp1: pot_r = st.number_input("최종 팟 (BB)", 1.0, 2000.0, 50.0, step=1.0, key="pot_r")
    with c_rp2: bet_r = st.number_input("상대 베팅 (BB) [체크=0]", 0.0, 2000.0, 25.0, step=1.0, key="bet_r")

    st.markdown("---")
    st.markdown('<p class="big-font">👿 상대방 핸드 (쇼다운 복기용)</p>', unsafe_allow_html=True)
    v_known_r = st.checkbox("쇼다운 결과 (상대 패) 확인 여부", key="v_known_r")
    v_made_r = "노 페어 (에어)"
    if v_known_r:
        v_made_r = st.selectbox("상대가 들고 있던 진짜 패는?", ["노 페어 (블러프/에어)", "미들/바텀 페어", "탑 페어", "투 페어", "셋 (Set) 이상", "스트레이트/플러시 이상"], key="v_made_box_r")

    # 리버는 드로우가 없으므로 "없음"으로 고정 전달
    dec_r, res_r = run_review_engine("River", pot_r, bet_r, my_made_r, "없음", v_known_r, v_made_r, is_kr)
    
    st.divider()
    if "RAISE" in dec_r or "BET" in dec_r or "CALL" in dec_r: st.markdown(f'<div class="res-box-call"><p>{dec_r}</p></div>', unsafe_allow_html=True)
    else: st.markdown(f'<div class="res-box-fold"><p>{dec_r}</p></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="ai-panel"><div class="ai-title"><span>🤖 GTO Review & Feedback</span></div><div class="ai-text">{res_r}</div></div>', unsafe_allow_html=True)
