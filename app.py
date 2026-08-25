import streamlit as st
import time

# ==========================================
# 1. 페이지 설정 및 세션 상태 초기화
# ==========================================
st.set_page_config(page_title="스미싱 모의 체험장", page_icon="📱", layout="centered")

# 시나리오가 변경될 때 결과를 초기화하는 콜백 함수
def reset_action():
    st.session_state.action_taken = None

if 'action_taken' not in st.session_state:
    st.session_state.action_taken = None

# ==========================================
# 2. 스미싱 시나리오 데이터베이스
# ==========================================
scenarios = {
    "📦 택배 사칭": {
        "sender": "010-8282-1234",
        "message": "[CJ대한통운] 도로명 주소 불일치로 물품 미배달. 주소지 변경 요망. 확인하기 ☞ https://cj-logis-tIck.com/abc",
        "red_flags": [
            "공공기관/기업 공식 번호(1588 등)가 아닌 **개인 휴대전화 번호(010)**로 발송되었습니다.",
            "URL을 자세히 보면 공식 주소가 아닌 교묘하게 철자를 바꾼 **가짜 주소(cj-logis-tIck.com)**입니다.",
            "사용자의 불안감(미배달)을 조성하여 클릭을 유도합니다."
        ]
    },
    "💌 모바일 청첩장": {
        "sender": "010-1004-5678",
        "message": "[모바일청첩장] 저희 결혼합니다. 바쁘시더라도 부디 참석하시어 축복해 주시기 바랍니다. https://wedding-invite-m.com/123",
        "red_flags": [
            "누구의 청첩장인지 **이름이나 소속이 명시되어 있지 않습니다**.",
            "평소 연락하지 않던 번호이거나, 지인의 번호가 도용되었을 수 있습니다.",
            "링크 클릭 시 악성 앱(APK)이 자동으로 다운로드될 확률이 매우 높습니다."
        ]
    },
    "💰 정부 지원금 사칭": {
        "sender": "02-123-4567",
        "message": "[국민건강보험] 2024년 본인부담환급금 지급 대상자입니다. 기한 내 신청 바랍니다. https://nhis-go-kr.com/refund",
        "red_flags": [
            "정부 기관이나 은행은 **절대로 문자메시지로 링크(URL) 클릭을 요구하지 않습니다**.",
            "가짜 도메인(`nhis-go-kr.com`)을 사용하여 실제 정부 사이트(`nhis.or.kr`)인 것처럼 위장했습니다."
        ]
    }
}

# ==========================================
# 3. 메인 UI 화면
# ==========================================
st.title("🚨 스미싱(Smishing) 모의 체험장")
st.markdown("스미싱이란 문자메시지(SMS)와 피싱(Phishing)의 합성어로, 악성 앱 주소가 포함된 휴대폰 문자를 대량 전송하여 개인정보를 탈취하는 수법입니다. **아래 상황에서 당신의 선택은?**")

st.divider()

# 시나리오 선택
selected_scenario = st.selectbox(
    "체험할 시나리오를 선택하세요:", 
    list(scenarios.keys()), 
    on_change=reset_action
)

scenario_data = scenarios[selected_scenario]

# 스마트폰 메신저 UI 구현 (HTML/CSS)
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

# ==========================================
# 4. 사용자 상호작용 (버튼)
# ==========================================
st.markdown("<h4 style='text-align: center;'>당신은 어떻게 대처하시겠습니까?</h4>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔗 링크 클릭하여 확인", use_container_width=True):
        st.session_state.action_taken = "click"
with col2:
    if st.button("🔎 URL 및 번호 분석", use_container_width=True):
        st.session_state.action_taken = "analyze"
with col3:
    if st.button("🛡️ 무시하고 삭제/차단", use_container_width=True):
        st.session_state.action_taken = "block"

# ==========================================
# 5. 결과 피드백 화면
# ==========================================
st.divider()

if st.session_state.action_taken == "click":
    st.error("### 💀 아차! 해킹되었습니다!")
    st.write("링크를 클릭하는 순간 **악성 앱(APK)이 백그라운드에 설치**되었거나, 정교하게 꾸며진 **가짜 로그인 페이지**로 이동하여 개인정보와 금융 정보가 탈취되었습니다.")
    with st.expander("👉 만약 실제로 클릭했다면 어떻게 해야 할까요?"):
        st.markdown("""
        1. **스마트폰 비행기 모드 전환**: 통신망을 차단하여 정보 유출 및 악성 앱의 서버 통신을 막습니다.
        2. **지인들에게 알림**: 내 번호로 스미싱 문자가 발송될 수 있으므로 지인들에게 링크 클릭 금지를 알립니다.
        3. **경찰청(112) 또는 KISA(118) 신고**: 피해 사실을 알리고 대처 방법을 안내받습니다.
        4. **스마트폰 초기화**: 백업을 수행한 후, 서비스 센터를 방문하거나 직접 공장 초기화를 진행합니다.
        """)

elif st.session_state.action_taken == "analyze":
    st.warning("### 🕵️‍♂️ 날카로운 눈썰미! 분석 결과입니다.")
    st.write("해당 메시지가 스미싱인 이유는 다음과 같습니다.")
    for flag in scenario_data["red_flags"]:
        st.markdown(f"- {flag}")
    st.info("이처럼 링크를 누르기 전에 **발신자 번호**와 **URL 주소**를 꼼꼼히 확인하는 습관이 중요합니다.")

elif st.session_state.action_taken == "block":
    st.success("### 🎉 훌륭합니다! 완벽한 대처입니다.")
    st.write("의심스러운 문자는 **절대 링크를 누르지 않고 즉시 삭제하거나 번호를 차단**하는 것이 최고의 예방책입니다. 또한 안드로이드폰의 경우 스팸 신고 기능을 활용하면 다른 사람들의 피해도 막을 수 있습니다.")

# ==========================================
# 6. 교육 자료 마무리
# ==========================================
if st.session_state.action_taken:
    st.markdown("---")
    st.subheader("💡 잊지 마세요! 스미싱 예방 3수칙")
    st.markdown("""
    1. **출처가 불분명한 문자메시지의 링크(URL)는 절대 클릭하지 않기**
    2. **알 수 없는 출처의 앱 설치 허용 끄기** (안드로이드 보안 설정)
    3. **정부 지원금, 택배, 지인 사칭 문자는 반드시 공식 앱이나 전화로 직접 확인하기**
    """)
