import streamlit as st
import pandas as pd
import random

# 1. 앱 기본 설정
st.set_page_config(page_title="JM LEGEND 03 (AI Agent)", page_icon="🤖", layout="centered")

# --- 데이터 정의 ---
pos_list = ["UTG", "UTG+1", "MP", "LJ", "HJ", "CO", "BTN", "SB", "BB"]
cards = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]

# --- CSS: 디자인 고정 (적녹색약/모바일/하이브리드) ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #111; border-right: 3px solid #D55E00; }
    .quote-box { 
        background-color: #222; color: #fff; padding: 15px; border-radius: 10px; 
        border: 2px solid #D55E00; text-align: center; font-weight: bold; font-size: 1.0em; margin-bottom: 20px;
    }
    .quote-author { color: #D55E00; font-size: 0.8em; margin-top: 5px; display: block; }
    .big-font { font-size: 1.3em; font-weight: 900; color: #fff; margin-top: 10px; margin-bottom: 5px; }
    
    /* AI Agent Analysis Box */
    .agent-box {
        background-color: #222; border: 1px solid #444; border-left: 5px solid #007bff;
        padding: 15px; border-radius: 5px; color: #eee; margin-top: 10px;
    }
    .agent-title { font-weight: bold; color: #007bff; font-size: 1.1em; margin-bottom: 5px; }
    
    /* 결과 박스 (색약 안심) */
    .res-box-raise { background-color: #D55E00; color: white; padding: 15px; border-radius: 10px; text-align: center; font-size: 1.6em; font-weight: bold; margin: 10px 0; }
    .res-box-call { background-color: #0072B2; color: white; padding: 15px; border-radius: 10px; text-align: center; font-size: 1.6em; font-weight: bold; margin: 10px 0; }
    .res-box-fold { background-color: #333333; color: #BBBBBB; padding: 15px; border-radius: 10px; text-align: center; font-size: 1.6em; font-weight: bold; margin: 10px 0; border: 2px solid #555; }
    
    div.stButton > button { width: 100%; height: 60px; font-size: 1.2em; border-radius: 10px; font-weight: bold; }
    
    /* 하단 차트 */
    .chart-header { color: #D55E00; font-weight: bold; font-size: 1.2em; margin-top: 30px; margin-bottom: 10px; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { height: 50px; background-color: #222; border-radius: 5px; color: #fff; }
    .stTabs [aria-selected="true"] { background-color: #D55E00; color: white; }
    </style>
""", unsafe_allow_html=True)

# --- 2. 사이드바 (설정) ---
with st.sidebar:
    st.header("⚙️ Game Setup")
    mode = st.radio("Game Mode", ["Cash Game", "Tournament"], index=1)
    env = st.selectbox("Environment", ["Online", "Live Pub", "Competition"], index=1)
    
    if mode == "Tournament":
        total_entries = st.number_input("Total Entries", 2, 100000, 100, 1)
    else:
        total_entries = 0
    
    h_in = st.number_input("Active Players", 2, 20, 9, 1)
    
    st.markdown("---")
    st.header("💰 Stack (BB)")
    my_stack = st.number_input("My BB", 1, 1000, 50)
    villain_stack = st.number_input("Villain BB", 1, 1000, 50)
    eff_stack = min(my_stack, villain_stack)
    st.metric("Eff. Stack", f"{eff_stack} BB")

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

# [2] Action (Radio + Hybrid Input)
st.markdown('<p class="big-font">⚔️ Action</p>', unsafe_allow_html=True)
action = st.radio("Act", ["Unopened", "Facing Raise", "Facing All-in"], horizontal=True, label_visibility="collapsed")
final_amt = 0.0

if action == "Facing Raise":
    st.markdown("**상대 레이즈 (BB)**")
    c_r1, c_r2 = st.columns([2.5, 1.5])
    with c_r1:
        val_slider = st.slider("Raise Slider", 2.0, 10.0, 2.5, 0.5, label_visibility="collapsed")
    with c_r2:
        val_input = st.number_input("Raise Input", 0.0, 1000.0, val_slider, step=0.5, label_visibility="collapsed")
    final_amt = val_input
    if final_amt >= 6.0: st.caption(f"⚠️ Big Raise: {final_amt}BB")

elif action == "Facing All-in":
    st.markdown("**상대 올인 (BB)**")
    max_val = float(villain_stack)
    c_a1, c_a2 = st.columns([2, 2])
    with c_a1:
        val_slider = st.slider("AI Slider", 1.0, max_val, max_val/2, label_visibility="collapsed")
    with c_a2:
        val_input = st.number_input("AI Input", 1.0, 1000.0, val_slider, label_visibility="collapsed")
    final_amt = val_input

st.divider()

# [3] Hand (Hybrid)
st.markdown('<p class="big-font">🃏 My Hand</p>', unsafe_allow_html=True)
col1, col2, col3 = st.columns([2.5, 2.5, 1.5])
with col1:
    st.caption("Card 1")
    v1_slider = st.select_slider("C1", cards, value="A", label_visibility="collapsed")
    v1 = st.selectbox("C1 Box", cards, index=cards.index(v1_slider), label_visibility="collapsed")
with col2:
    st.caption("Card 2")
    v2_slider = st.select_slider("C2", cards, value="K", label_visibility="collapsed")
    v2 = st.selectbox("C2 Box", cards, index=cards.index(v2_slider), label_visibility="collapsed")
with col3:
    st.caption("Suit")
    suit_radio = st.radio("S", ["s", "o"], horizontal=True, label_visibility="collapsed")
    suit = "s" if suit_radio == "s" else "o"

# --- 4. GTO AI AGENT ENGINE (The Brain) ---
class PokerAgent:
    def __init__(self, mode, env, pos, v1, v2, suit, act, h_stack, e_stack, amt):
        self.mode = mode
        self.env = env
        self.pos = pos
        self.v1 = v1
        self.v2 = v2
        self.suit = suit
        self.act = act
        self.h_stack = h_stack
        self.e_stack = e_stack
        self.amt = amt
        
        # 랭크 파싱
        rk = {"A":14, "K":13, "Q":12, "J":11, "T":10, "9":9, "8":8, "7":7, "6":6, "5":5, "4":4, "3":3, "2":2}
        self.r1 = rk[v1]
        self.r2 = rk[v2]
        if self.r1 < self.r2: 
            self.v1, self.v2 = self.v2, self.v1
            self.r1, self.r2 = self.r2, self.r1
        self.is_pair = (self.r1 == self.r2)
        self.is_s = (self.suit == "s")
        self.hand = f"{self.v1}{self.v2}{self.suit}" if not self.is_pair else f"{self.v1}{self.v2}"

    def calculate_power_score(self):
        # 1. 기본 핸드 파워 (Chen Formula 변형)
        score = max(self.r1, self.r2) * 2
        if self.is_pair: score = max(5, self.r1 * 2 + 5) # 포켓 페어 가산점
        if self.is_s: score += 4 # 수딧 보너스
        
        # 커넥터 보너스
        gap = self.r1 - self.r2
        if gap == 1: score += 3
        elif gap == 2: score += 2
        elif gap == 0: pass
        else: score -= gap # 갭 페널티
        
        # 2. 포지션 가중치
        pos_bonus = {"BTN": 5, "CO": 4, "HJ": 3, "LJ": 2, "MP": 1, "UTG": 0, "UTG+1": 0, "SB": 1, "BB": 2}
        score += pos_bonus.get(self.pos, 0)
        
        return score

    def analyze(self):
        score = self.calculate_power_score()
        reasoning = []
        action = "FOLD"
        
        # [STEP 1] 절대 방어 (Premiums)
        if self.hand in ["AA", "KK", "QQ", "AKs", "AKo"]:
            return "RAISE", "🤖 Agent: This is a Premium Monster. Never Fold. (GTO 100%)"

        # [STEP 2] 상황별 AI 판단
        if self.act == "Unopened":
            threshold = 28 # 기본 오픈 커트라인
            if self.pos in ["BTN", "CO"]: threshold -= 6 # 스틸 구간
            if self.mode == "Tournament" and self.env == "Competition": threshold += 2 # 대회는 타이트
            
            # 숏스택 로직
            if self.h_stack <= 15:
                if score >= 25: return "RAISE", f"🤖 Agent: Stack is short ({self.h_stack}BB). Push with Score {score}."
                return "FOLD", "🤖 Agent: Save chips for a better spot."
                
            if score >= threshold:
                action = "RAISE"
                reasoning.append(f"Position ({self.pos}) advantage confirmed.")
                reasoning.append(f"Hand Power ({score}) exceeds threshold ({threshold}).")
            else:
                action = "FOLD"
                reasoning.append(f"Hand Power ({score}) is too weak for {self.pos}.")

        elif self.act == "Facing Raise":
            req_equity = 40 # 기본 요구 승률 점수
            
            # BB 방어 특수 로직
            if self.pos == "BB":
                if self.amt >= 6.0: 
                    req_equity = 60 # 빅오픈 -> 타이트
                    reasoning.append(f"Villain's Raise ({self.amt}BB) is HUGE. Tightening range.")
                elif self.amt <= 3.0: 
                    req_equity = 25 # 스몰오픈 -> 와이드
                    reasoning.append("Pot Odds are good. Widening defense range.")
                else:
                    req_equity = 35
            
            # 캐시게임 셋마이닝 체크
            if self.mode == "Cash Game" and self.is_pair and self.r1 < 10:
                implied_odds = self.e_stack / self.amt
                if implied_odds >= 20: return "CALL", f"🤖 Agent: Set Mining Valid (Implied Odds {implied_odds:.1f}x > 20x)."
                else: return "FOLD", f"🤖 Agent: Set Mining Invalid (Odds {implied_odds:.1f}x too low)."

            if score >= req_equity:
                action = "CALL"
                if score >= req_equity + 15: action = "RAISE" # 3-Bet
                reasoning.append(f"Hand Score {score} vs Required {req_equity}.")
            else:
                action = "FOLD"
                reasoning.append(f"EV is negative vs {self.amt}BB Raise.")

        elif self.act == "Facing All-in":
            risk_tolerance = "High" if self.mode == "Cash Game" else "Low"
            
            if self.mode == "Tournament":
                if self.h_stack < self.amt: # Risk of Elimination
                    if self.hand in ["JJ", "TT", "AQs", "AQo"]: return "CALL", "🤖 Agent: Critical Spot. Equity suggests CALL despite risk."
                    if self.hand in ["99", "88", "KQs"]: return "FOLD", "🤖 Agent: Too risky for Tournament Life (ICM)."
            
            # 기본 올인 콜 범위
            call_range = ["AA", "KK", "QQ", "JJ", "TT", "99", "AKs", "AKo", "AQs", "AQo"]
            if self.hand in call_range:
                return "CALL", "🤖 Agent: Hand is within profitable Call Range."
            return "FOLD", "🤖 Agent: Equity insufficient to call Shove."

        # 최종 메시지 조합
        final_reason = " ".join(reasoning) if reasoning else "Standard GTO Decision."
        return action, f"🤖 Agent Analysis: {final_reason}"

# --- 5. 실행 및 출력 ---
agent = PokerAgent(mode, env, final_pos, v1, v2, suit, action, my_stack, eff_stack, final_amt)
decision, reasoning = agent.analyze()

st.divider()

if decision == "RAISE":
    st.markdown(f'<div class="res-box-raise">{decision}</div>', unsafe_allow_html=True)
elif decision == "CALL":
    st.markdown(f'<div class="res-box-call">{decision}</div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div class="res-box-fold">{decision}</div>', unsafe_allow_html=True)

# Agent 분석 박스
st.markdown(f"""
<div class="agent-box">
    <div class="agent-title">🧠 GTO Agent Intelligence</div>
    {reasoning}
</div>
""", unsafe_allow_html=True)

# --- 6. 하단 차트 (고정) ---
st.markdown("---")
st.markdown('<p class="chart-header">🚀 Short Stack Push (20BB↓)</p>', unsafe_allow_html=True)
st.table(pd.DataFrame({
    "Pos": ["UTG", "HJ", "CO", "BTN", "SB"],
    "Push": ["77+, AJs+, AQo+", "55+, A9s+, AJo+", "22+, A2s+, A8o+", "Any Pair, Any Ax, Kx", "Any Pair, Any Ax, Q5s+"]
}))

st.markdown('<p class="chart-header">📊 Professional GTO Ranges</p>', unsafe_allow_html=True)
tab1, tab2, tab3 = st.tabs(["Early (EP/MP)", "Late (CO/BTN)", "Blinds (SB)"])
with tab1:
    st.table(pd.DataFrame({"Pos": ["UTG", "MP"], "Range": ["77+, ATs+, AQo+", "55+, KTs+, AJo+"]}))
with tab2:
    st.table(pd.DataFrame({"Pos": ["CO", "BTN"], "Range": ["22+, A8o+, Q9s+", "Any Pair, Any Suited, Any Ax"]}))
with tab3:
    st.table(pd.DataFrame({"Pos": ["SB"], "Range": ["22+, A7o+, K8s+, 98s+"]}))
