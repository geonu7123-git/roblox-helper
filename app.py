import streamlit as st

# 페이지 설정
st.set_page_config(page_title="로블록스 끝말잇기 도우미", page_icon="📝")

st.title("📝 로블록스 끝말잇기 치트키 도우미")
st.caption("사라진 입력창을 살리기 위한 초안정화 버전입니다.")

# 💡 마의 글자 방어 단어 사전
CHITKEY = {
    "녘": ["녘새발 (해가 넘어가기 전에 우는 새)", "녘노을 (해 질 녘의 붉은 노을)"],
    "늄": ["늄바리 (알루미늄으로 만든 밥그릇)", "늄라 (인도 전통 타악기)"],
    "릇": ["릇무꽃 (무과의 한해살이풀)"],
    "륨": ["륨프늄 (방사성 인공 금속 원소)", "륨바 (쿠바 기원의 사교댄스)"],
    "븀": ["븀바륨 (네오디븀과 바륨의 합성어)", "븀디뮴 (네오디븀의 외래어 표기)"],
    "뮴": ["뮴스 (카드뮴 합금의 일종)", "뮴디뮴 (카드뮴 관련 오픈사전 단어)"],
    "슘": ["슘페터 (경제학자 이름)"],
    "쯔": ["쯔쯔가무시 (감염병 이름)"],
    "쁨": ["쁨나무 (기쁨을 주는 나무)"]
}

# 🎈 단어 입력창 (무조건 뜹니다!)
user_input = st.text_input("글자나 단어를 입력하세요 (예: 슘, 늄, 이리듐):", key="safe_input").strip()

if user_input:
    # 마지막 글자 추출
    last_letter = user_input[-1]
    st.subheader(f"🔍 '{last_letter}'(으)로 시작하는 추천 방어 단어")
    
    if last_letter in CHITKEY:
        st.success(f"🔥 한방 단어 방어 성공!")
        for word in CHITKEY[last_letter]:
            st.write(f"✨ **{word}**")
    else:
        st.warning(f"⚠️ '{last_letter}'는 일반 글자이므로 마음대로 이어가셔도 됩니다!")
