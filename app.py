import streamlit as st
import time

# ==========================================
# 1. 페이지 설정 및 세션 상태 초기화
# ==========================================
st.set_page_config(page_title="사이버 보안 훈련장", page_icon="🛡️", layout="centered")

# 스미싱 체험용 상태 초기화
if 'action_taken' not in st.session_state:
    st.session_state.action_taken = None

def reset_action():
    st.session_state.action_taken = None

# URL 퀴즈용 상태 초기화
if 'quiz_step' not in st.session_state:
    st.session_state.quiz_step = 0
if 'quiz_score' not in st.session_state:
    st.session_state.quiz_score = 0
if 'answered' not in st.session_state:
    st.session_state.answered = False
if 'is_correct' not in st.session_state:
    st.session_state.is_correct = False

def next_question():
    st.session_state.quiz_step += 1
    st.session_state.answered = False

def restart_quiz():
    st.session_state.quiz_step = 0
    st.session_state.quiz_score = 0
    st.session_state.answered = False

# ==========================================
# 2. 데이터베이스 (스미싱 & URL 퀴즈)
# ==========================================
scenarios = {
    "📦 택배 사칭": {
        "sender": "010-8282-1234",
        "message": "[CJ대한통운] 도로명 주소 불일치로 물품 미배달. 주소지 변경 요망. 확인하기 ☞ https://cj-logis-tIck.com/abc",
        "red_flags": ["개인 휴대전화 번호(010) 사용", "교묘하게 철자를 바꾼 가짜 주소(cj-logis-tIck.com)"]
    },
    "💌 모바일 청첩장": {
        "sender": "010-1004-5678",
        "message": "[모바일청첩장] 저희 결혼합니다. 바쁘시더라도 부디 참석하시어 축복해 주시기 바랍니다. https://wedding-invite-m.com/123",
        "red_flags": ["발신자 신원 불분명", "악성 앱(APK) 다운로드 유도 전형적 패턴"]
    },
    "💰 정부 지원금 사칭": {
        "sender": "02-123-4567",
        "message": "[국민건강보험] 2024년 본인부담환급금 지급 대상자입니다. 기한 내 신청 바랍니다. https://nhis-go-kr.com/refund",
        "red_flags": ["정부 기관은 문자로 링크 클릭 요구 안함", "공식 도메인(.or.kr, .go.kr)이 아닌 .com 사용"]
    }
}

# 5대 URL 탐지 퀴즈 시나리오
quiz_data = [
    {
        "topic": "포털 사이트 (네이버)",
        "context": "메일함 용량이 초과되어 비밀번호를 변경하라는 안내 메일을 받았습니다. 다음 중 안전한 '진짜' 링크는 무엇일까요?",
        "option_a": {"url": "https://nid.naver.com/nidlogin.login", "is_real": True},
        "option_b": {"url": "https://nid.naver-security.com/login", "is_real": False},
        "explanation": "✅ 네이버의 공식 로그인 도메인은 'nid.naver.com'입니다. 해커들은 '-security'나 '-login' 등을 덧붙인 새로운 도메인(naver-security.com)을 구매하여 위장합니다."
    },
    {
        "topic": "SNS (인스타그램)",
        "context": "누군가 타지역에서 내 인스타그램에 로그인했다는 경고 문자가 왔습니다. 계정을 보호할 링크를 고르세요.",
        "option_a": {"url": "https://www.1nstagram.com/accounts/login/", "is_real": False},
        "option_b": {"url": "https://www.instagram.com/accounts/login/", "is_real": True},
        "explanation": "✅ 알파벳 'i(아이)' 대신 숫자 '1(일)'을 사용한 전형적인 타이포스쿼팅(Typosquatting) 기법입니다. 스마트폰의 작은 화면에서는 구별하기 매우 어렵습니다."
    },
    {
        "topic": "정부 기관 (정부24)",
        "context": "미납된 과태료가 있다며 납부 고지서 링크가 문자로 도착했습니다. 진짜 링크는 무엇일까요?",
        "option_a": {"url": "https://www.gov.kr/portal/main", "is_real": True},
        "option_b": {"url": "https://www.gov-kr.com/portal/main", "is_real": False},
        "explanation": "✅ 대한민국 정부 기관은 예외 없이 '.go.kr' 또는 '.kr' 도메인을 사용합니다. '.com'이나 '.net'을 사용하는 정부 기관은 100% 가짜입니다."
    },
    {
        "topic": "택배 조회 (CJ대한통운)",
        "context": "택배 배송 조회를 위해 송장 번호를 입력해야 합니다. 올바른 주소는 무엇일까요?",
        "option_a": {"url": "https://cjlogistics.delivery-track.net/ko", "is_real": False},
        "option_b": {"url": "https://www.cjlogistics.com/ko/tool/parcel/tracking", "is_real": True},
        "explanation": "✅ 가짜 링크는 'delivery-track.net' 이라는 해커의 도메인 앞에 'cjlogistics'라는 하위 도메인(Subdomain)을 붙여 교묘하게 눈속임을 한 것입니다."
    },
    {
        "topic": "은행 (KB국민은행)",
        "context": "보안 승급이 필요하다며 은행에서 링크를 보내왔습니다. 진짜 은행 링크를 찾으세요.",
        "option_a": {"url": "https://obank.kbstarr.com/quics?page=obank", "is_real": False},
        "option_b": {"url": "https://obank.kbstar.com/quics?page=obank", "is_real": True},
        "explanation": "✅ 진짜 도메인은 'kbstar.com'입니다. 가짜 링크는 알파벳 'r'을 하나 더 붙여('kbstarr') 급하게 읽는 사람들의 실수를 유도합니다."
    }
]

# ==========================================
# 3. 메인 UI (탭 구성)
# ==========================================
st.title("🚨 사이버 보안 훈련장")
st.markdown("사이버 범죄자들의 최신 수법을 모의 체험하고, 스스로를 보호하는 방법을 훈련하는 공간입니다.")

tab1, tab2 = st.tabs(["📱 스미싱 문자 체험", "🔎 진짜 vs 가짜 URL 퀴즈"])

# ==========================================
# [TAB 1] 스미싱 문자 체험
# ==========================================
with tab1:
    st.subheader("1단계: 스미싱(Smishing) 대처 훈련")
    
    selected_scenario = st.selectbox(
        "수신된 문자 메시지를 선택하세요:", 
        list(scenarios.keys()), 
        on_change=reset_action
    )
    
    scenario_data = scenarios[selected_scenario]

    # 스마트폰 메신저 UI (HTML)
    chat_html = f"""
    <div style='display: flex; justify-content: center; margin-bottom: 20px;'>
        <div style='background-color: #f1f2f6; padding: 20px; border-radius: 20px; width: 350px; font-family: "Malgun Gothic", sans-serif; box-shadow: 0 4px 8px rgba(0,0,0,0.1); border: 2px solid #ddd;'>
            <div style='text-align: center; font-size: 14px; color: #555; margin-bottom: 15px; border-bottom: 1px solid #ccc; padding-bottom: 10px;'>
                <strong>메시지</strong><br>
                <span style='font-size: 12px;'>발신: {scenario_data["sender"]}</span>
            </div>
            <div style='background-color: #fff; padding: 15px; border-radius: 15px; border: 1px solid #e1e1e1; font-size: 15px; line-height: 1.5; color: #333;'>
                {scenario_data["message"]}
            </div>
        </div>
    </div>
    """
    st.markdown(chat_html, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔗 링크 클릭하여 확인", use_container_width=True, key="btn_click"):
            st.session_state.action_taken = "click"
    with col2:
        if st.button("🔎 URL 및 번호 분석", use_container_width=True, key="btn_analyze"):
            st.session_state.action_taken = "analyze"
    with col3:
        if st.button("🛡️ 무시하고 차단", use_container_width=True, key="btn_block"):
            st.session_state.action_taken = "block"

    st.divider()

    if st.session_state.action_taken == "click":
        st.error("### 💀 아차! 악성 앱이 설치되었습니다!")
        st.write("링크를 클릭하는 순간 개인정보를 빼가는 **악성 앱(APK)이 백그라운드에 설치**되었습니다. 문자메시지의 링크는 절대 함부로 눌러서는 안 됩니다.")
    elif st.session_state.action_taken == "analyze":
        st.warning("### 🕵️‍♂️ 날카로운 눈썰미! (의심 포인트)")
        for flag in scenario_data["red_flags"]:
            st.markdown(f"- {flag}")
    elif st.session_state.action_taken == "block":
        st.success("### 🎉 훌륭합니다! 완벽한 방어입니다.")
        st.write("의심스러운 문자는 절대 링크를 누르지 않고 즉시 삭제/차단하는 것이 최고의 보안입니다.")

# ==========================================
# [TAB 2] 진짜 vs 가짜 URL 탐지 퀴즈
# ==========================================
with tab2:
    st.subheader("2단계: 실전! 가짜 URL 탐지 훈련")
    st.write("해커들은 완벽하게 똑같이 생긴 가짜 웹사이트를 만들어 여러분의 아이디와 비밀번호를 노립니다. 주소창(URL)을 분석하여 해커의 사이트를 걸러내세요!")
    
    if st.session_state.quiz_step < len(quiz_data):
        q = quiz_data[st.session_state.quiz_step]
        
        st.info(f"**Q{st.session_state.quiz_step + 1}. [{q['topic']}]** {q['context']}")
        
        # 버튼 스타일링을 위한 마크다운
        st.markdown("<br>", unsafe_allow_html=True)
        
        if not st.session_state.answered:
            # 선택지 A
            if st.button(f"🅰️ {q['option_a']['url']}", use_container_width=True):
                st.session_state.answered = True
                st.session_state.is_correct = q['option_a']['is_real']
                if st.session_state.is_correct: st.session_state.quiz_score += 1
                st.rerun()
                
            # 선택지 B
            if st.button(f"🅱️ {q['option_b']['url']}", use_container_width=True):
                st.session_state.answered = True
                st.session_state.is_correct = q['option_b']['is_real']
                if st.session_state.is_correct: st.session_state.quiz_score += 1
                st.rerun()
        
        # 정답 확인 후 결과 화면
        if st.session_state.answered:
            if st.session_state.is_correct:
                st.success("### ⭕ 정답입니다! 안전한 링크를 찾으셨네요.")
            else:
                st.error("### ❌ 해킹당했습니다! 가짜(피싱) 링크를 누르셨습니다.")
            
            # 해설 박스
            st.markdown(f"""
            <div style="background-color:#f8f9fa; padding:15px; border-left:5px solid #0052cc; border-radius:5px; margin-top:10px; margin-bottom:20px;">
                <span style="color:#0052cc; font-weight:bold;">💡 해커의 수법 분석</span><br><br>
                {q['explanation']}
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("다음 문제 ➔"):
                next_question()
                st.rerun()

    else:
        # 퀴즈 종료 화면
        st.balloons()
        st.header("🏆 훈련 종료!")
        st.subheader(f"당신의 보안 점수: {st.session_state.quiz_score} / {len(quiz_data)} 점")
        
        if st.session_state.quiz_score == len(quiz_data):
            st.success("완벽합니다! 해커들이 당신을 속이기는 불가능해 보이네요. 보안 전문가 수준의 눈썰미입니다.")
        elif st.session_state.quiz_score >= 3:
            st.warning("대체로 훌륭하지만, 방심은 금물입니다! 교묘한 오타(Typosquatting)에 속지 않도록 늘 주소창을 확인하는 습관을 들이세요.")
        else:
            st.error("위험합니다! 실생활에서 개인정보가 유출될 확률이 높습니다. '모든 링크는 가짜일 수 있다'는 의심을 먼저 하는 습관이 필요합니다.")
            
        if st.button("🔄 훈련 다시 하기"):
            restart_quiz()
            st.rerun()
