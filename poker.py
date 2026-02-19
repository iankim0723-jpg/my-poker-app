import streamlit as st
import pandas as pd
import os

# 1. 앱 기본 설정
st.set_page_config(page_title="JM LEGEND 03 (Review Master)", page_icon="📈", layout="centered")

# --- 양방향 동기화(Sync) 로직 & 세션 초기화 ---
sync_keys = [
    'pos', 'raise', 'ai', 'c1', 'c2', 
    'f1', 'f2', 'f3', 't', 'r', 
    'vc1', 'vc2' # 상대 패 동기화 추가
]
for k in sync_keys:
    if f'{k}_slider' not in st.session_state: st.session_state[f'{k}_slider'] = "A" if k not in ['raise', 'ai', 'pos'] else ("BTN" if k == 'pos' else 2.5 if k == 'raise' else 25.0)
    if f'{k}_box' not in st.session_state: st.session_state[f'{k}_box'] = "A" if k not in ['raise', 'ai', 'pos'] else ("BTN" if k == 'pos' else 2.5 if k == 'raise' else 25.0)

if 'start_stack_input' not in st.session_state: st.session_state.start_stack_input = 50.0
if 'show_villain' not in st.session_state: st.session_state.show_villain = False

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
cb_vc1_s2b, cb_vc1_b2s = create_sync_callbacks('vc1')
cb_vc2_s2b, cb_vc2_b2s = create_sync_callbacks('vc2')

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

# --- CSS 강제 고정 ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff !important; }
    .stApp h1, .stApp h2, .stApp h3, .stApp p, .stApp label, .stApp span { color: #111111 !important; }
    [data-testid="stSidebar"] { background-color: #111111 !important; border-right: 3px solid #D55E00 !important; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] span, [data-testid="stMetricValue"] { color: #ffffff !important; }

    .quote-box { background-color: #222222 !important; border: 2px solid #D55E00 !important; padding: 10px; border-radius: 8px; text-align: center; margin-bottom: 20px; }
    .quote-box p, .quote-box span { color: #ffffff !important; font-weight: bold !important; font-size: 0.9em !important; }
    .quote-author span { color: #D55E00 !important; font-size: 0.8em !important; margin-top: 5px; display: block; }
    
    .res-box-raise p { background-color: #D55E00 !important; color: #ffffff !important; padding: 15px; border-radius: 10px; text-align: center; font-size: 1.6em !important; font-weight: bold !important; margin: 10px 0; }
    .res-box-call p { background-color: #0072B2 !important; color: #ffffff !important; padding: 15px; border-radius: 10px; text-align: center; font-size: 1.6em !important; font-weight: bold !important; margin: 10px 0; }
    .res-box-fold p { background-color: #333333 !important; color: #BBBBBB !important; padding: 15px; border-radius: 10px; text-align: center; font-size: 1.6em !important; font-weight: bold !important; margin: 10px 0; border: 2px solid #555 !important; }
    
    .ai-panel { background-color: #1e2630 !important; border-left: 5px solid #00ccff !important; padding: 15px; border-radius: 5px; margin-top: 10px; }
    .ai-panel p, .ai-panel span { color: #d0d0d0 !important; font-size: 0.95em !important; line-height: 1.5 !important; }
    .ai-title span { color: #00ccff !important; font-weight: bold !important; font-size: 1.1em !important; margin-bottom: 8px; }
    .highlight-stat span { color: #ffeb3b !important; font-weight: bold !important; }

    div.stButton > button { width: 100%; height: 60px; font-size: 1.2em; border-radius: 10px; font-weight: bold; margin-bottom: 10px; }
    [data-testid="stSidebar"] button { background-color: #D55E00 !important; border: none !important; }
    [data-testid="stSidebar"] button p { color: #ffffff !important; }

    .big-font { font-size: 1.3em !important; font-weight: 900 !important; color: #111111 !important; margin-top: 15px; margin-bottom: 5px; }
    
    .chart-header { color: #D55E00 !important; font-weight: bold !important; font-size: 1.1em !important; margin-top: 25px; margin-bottom: 5px; text-align: center; }
    th { background-color: #222222 !important; color: #D55E00 !important; text-align: center !important; }
    td { background-color: #ffffff !important; color: #111111 !important; text-align: center !important; border: 1px solid #dddddd !important; }
    
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
        else: st.warning("⚠️ 이미지를 찾을 수 없습니다.")

    if st.button("🏆 핸드 순위표 보기" if is_kr else "🏆 View Hand Rankings", use_container_width=True): show_hand_rankings()
        
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
    st.markdown(f"<div style='text-align: center; padding: 15px; background-color: #1e1e1e; border-radius: 8px; border: 1px solid #444; margin-bottom: 20px;'><span style='color: #00ccff !important; font-weight: bold; font-size: 1.1em;'>{visitor_text}</span><br><span style='font-size: 2em; font-weight: 900; color: #ffffff !important;'>{count:,}</span><span style='color: #888888 !important; font-size: 0.9em;'> 명</span></div>", unsafe_allow_html=True)

# --- 3. 메인 화면 ---
st.title("🛡️ JM LEGEND 03")

tab_home, tab_flop, tab_turn, tab_river = st.tabs(["🏠 프리플랍 (Home)", "🃏 플랍 (Flop)", "🃏 턴 (Turn)", "🃏 리버 (River)"])

# ==========================================
# 🏠 [TAB 1] 프리플랍 (홈 화면) - 글로벌 공통 변수 셋업
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
        c_r1, c_r2 = st.columns([2.5, 1.5])
        with c_r1: st.slider("Raise Slider", 2.0, 15.0, step=0.5, key="raise_slider", on_change=cb_raise_s2b, label_visibility="collapsed")
        with c_r2: st.number_input("Raise Input", 0.0, 1000.0, step=0.5, key="raise_box", on_change=cb_raise_b2s, label_visibility="collapsed")
        final_amt = st.session_state.raise_box
    elif act_engine == "Facing All-in":
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
    with c2_col:
        st.select_slider("C2 Slider", cards, key="c2_slider", on_change=cb_c2_s2b, label_visibility="collapsed")
        st.selectbox("C2 Box", cards, key="c2_box", on_change=cb_c2_b2s, label_visibility="collapsed")
    with s_col:
        suit_idx = ["s", "o"].index("s" if "s" in st.radio("S", ["s (수딧)", "o (오프)"] if is_kr else ["s", "o"], horizontal=True, label_visibility="collapsed") else "o")
        suit_engine = "s" if suit_idx == 0 else "o"

    st.info("💡 플랍 이후의 분석(복기)을 원하시면 상단의 [플랍/턴/리버] 탭을 클릭하세요." if is_kr else "💡 Click the Flop/Turn/River tabs for Post-flop review.")

# ==========================================
# 🧠 복기 전용: 포스트플랍 GTO 분석 엔진 (오답 노트)
# ==========================================
def run_review_engine(street, pot_size, bet_size, my_made, my_draw, v_known, v_made, is_kr):
    # 1. 수학적 배당(Pot Odds) 계산
    call_amt = bet_size
    total_pot = pot_size + bet_size + call_amt
    pot_odds = (call_amt / total_pot) * 100 if total_pot > 0 else 0
    
    # 2. 내 핸드 가치 산정 (Heuristic Equity)
    outs = 0
    if "플러시" in my_draw: outs += 9
    if "양차" in my_draw: outs += 8
    if "빵꾸" in my_draw: outs += 4
    
    multiplier = 4 if street == "Flop" else 2
    draw_equity = outs * multiplier
    
    # 3. 메이드 밸류 가중치
    made_value = 0
    if my_made == "탑 페어": made_value = 60
    elif my_made == "투 페어": made_value = 75
    elif my_made == "셋 (Set) 이상": made_value = 90
    elif my_made == "미들/바텀 페어": made_value = 35

    total_equity = max(draw_equity, made_value)

    analysis = []
    decision = "FOLD"
    
    analysis.append(f"<b>[상황 진단]</b> 현재 팟: {pot_size}BB | 요구 배당(Pot Odds): <span class='highlight-stat'>{pot_odds:.1f}%</span>")
    
    # 4. 상대 핸드를 아는 경우 (복기 오답노트 모드)
    if v_known:
        v_value = 0
        if v_made == "탑 페어": v_value = 60
        elif v_made == "투 페어": v_value = 75
        elif v_made == "셋 (Set) 이상": v_value = 90
        elif v_made == "스트레이트/플러시 이상": v_value = 100
        
        analysis.append(f"<b>[결과 확인]</b> 상대는 '{v_made}' 였습니다.")
        
        # 오답 노트 생성
        if total_equity >= pot_odds:
            # GTO상 콜이 맞았음
            decision = "CALL (GTO Correct)"
            if v_value > total_equity:
                analysis.append("💡 <b>[오답 노트 - 억울한 패배]</b> 결과적으로는 상대 패가 더 높아서 졌지만, 수학적으로 당시 내 에퀴티가 배당을 충족했습니다. <b>여기서 콜을 받은 것은 잘못이 아닙니다 (GTO 정답).</b> 쿨러(Cooler)였을 뿐이니 결과에 쫄아서 다음번에 오버폴드(Over-fold) 하지 마세요!")
            else:
                analysis.append("💡 <b>[오답 노트 - 나이스 콜]</b> 결과도 이겼고, 수학적으로도 올바른 완벽한 콜(또는 밸류벳)이었습니다. 훌륭합니다!")
        else:
            # GTO상 폴드가 맞았음
            decision = "FOLD (GTO Correct)"
            if v_value < total_equity:
                analysis.append("💡 <b>[오답 노트 - 운 좋은 승리]</b> 상대가 블러핑(에어)을 쳐서 결과적으로 내가 먹었을지 모르나, 배당이 안 맞는데 콜을 한 <b>잘못된 플레이(-EV)</b>입니다. 이런 플레이가 반복되면 장기적으로 돈을 잃습니다. 다음엔 무조건 폴드하세요.")
            else:
                analysis.append("💡 <b>[오답 노트 - 굿 폴드]</b> 상대 패도 강했고 배당도 안 맞았습니다. 여기서 미련 없이 칩을 아낀(Fold) 당신의 결단력이 토너먼트 생존의 핵심입니다.")

    # 5. 상대 핸드를 모르는 경우 (일반 GTO 분석)
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
                analysis.append("드로우 아웃츠도 부족하고 메이드도 약합니다. 상대의 베팅에 미련 없이 폴드하세요.")

    return decision, "<br>".join(analysis)

# ==========================================
# 🃏 [TAB 2] 플랍 (Flop) - 복기 엔진 적용
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
    with c_m1:
        my_made = st.selectbox("현재 메이드 상태", ["노 페어 (에어)", "미들/바텀 페어", "탑 페어", "투 페어", "셋 (Set) 이상"], key="my_made_flop")
    with c_m2:
        my_draw = st.selectbox("현재 드로우 상태", ["없음", "빵꾸 (Gutshot)", "양차 (OESD)", "플러시 드로우", "플러시+양차 콤보"], key="my_draw_flop")

    st.markdown('<p class="big-font">💰 팟 & 액션</p>', unsafe_allow_html=True)
    c_p1, c_p2 = st.columns(2)
    with c_p1: pot_f = st.number_input("현재 팟 (BB)", 1.0, 1000.0, 10.0, step=1.0, key="pot_f")
    with c_p2: bet_f = st.number_input("상대 베팅 (BB) [체크=0]", 0.0, 1000.0, 3.0, step=1.0, key="bet_f")

    st.markdown("---")
    st.markdown('<p class="big-font">👿 상대방 핸드 (쇼다운 복기용)</p>', unsafe_allow_html=True)
    v_known = st.checkbox("쇼다운 결과 (상대 패) 입력하기", key="v_known_flop")
    v_made = "노 페어 (에어)"
    if v_known:
        v_made = st.selectbox("상대가 들고 있던 진짜 패는?", ["노 페어 (블러프/에어)", "미들/바텀 페어", "탑 페어", "투 페어", "셋 (Set) 이상", "스트레이트/플러시 이상"], key="v_made_flop")

    dec_f, res_f = run_review_engine("Flop", pot_f, bet_f, my_made, my_draw, v_known, v_made, is_kr)
    
    st.divider()
    if "RAISE" in dec_f or "BET" in dec_f or "CALL" in dec_f: st.markdown(f'<div class="res-box-call"><p>{dec_f}</p></div>', unsafe_allow_html=True)
    else: st.markdown(f'<div class="res-box-fold"><p>{dec_f}</p></div>', unsafe_allow_html=True)
    
    st.markdown(f'<div class="ai-panel"><div class="ai-title"><span>🤖 GTO Review & Feedback</span></div><div class="ai-text">{res_f}</div></div>', unsafe_allow_html=True)

# 턴과 리버 탭은 플랍과 구조가 완전히 동일하게 확장될 예정입니다. (현재는 플랍 탭에서 복기 엔진의 정수를 확인해보세요!)
