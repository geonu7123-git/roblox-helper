import streamlit as st
import requests
import json
import re

# 페이지 설정
st.set_page_config(page_title="로블록스 끝말잇기 도우미", page_icon="📝", layout="centered")

st.title("📝 로블록스 끝말잇기 도우미")
st.caption("단어 전체나 마지막 글자(예: '슘')만 입력해도 이어질 단어를 검색합니다.")

# 💡 최적화 0: 특수/방어 단어 사전 (네이버 기본 사전에 안 나오는 게임 허용 단어 추가)
CUSTOM_DICTIONARY = {
    "녘": [
        {"단어": "녘새발", "품사": "명사", "뜻": "해가 넘어가기 전에 우는 새 (오픈사전/게임 허용 단어)"},
        {"단어": "녘노을", "품사": "명사", "뜻": "해 질 녘에 붉게 물든 하늘 (오픈사전/게임 허용 단어)"}
    ]
    # 나중에 "릇", "쁨" 같은 다른 방어 단어도 여기에 계속 추가할 수 있습니다!
}

# 💡 최적화 1: 캐싱 적용 (동일한 단어 검색 시 API를 재요청하지 않고 10분간 기억)
@st.cache_data(ttl=600)
def get_words_via_web(target_letter):
    if not target_letter:
        return []
        
    words = []
    
    # ⭐ 1. 커스텀 사전(게임용 특수 단어) 먼저 결과에 추가
    if target_letter in CUSTOM_DICTIONARY:
        words.extend(CUSTOM_DICTIONARY[target_letter])
        
    # ⭐ 2. 네이버 사전 API 검색
    url = f"https://ko.dict.naver.com/api3/koko/search?query={target_letter}*"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://ko.dict.naver.com/",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    
    try:
        # 💡 최적화 2: 타임아웃(5초) 설정으로 네트워크 지연 시 무한 대기 방지
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()  # HTTP 에러 발생 시 예외 발생
        data = response.json()
    except (requests.RequestException, json.JSONDecodeError):
        # API 오류가 나더라도 커스텀 단어가 있다면 안전하게 반환하도록 예외 처리 강화
        return words
            
    search_results = data.get('searchResultMap', {}).get('searchResultListMap', {}).get('WORD', {}).get('items', [])
    
    # 💡 최적화 3: 반복문 밖에서 정규식을 미리 컴파일하여 처리 속도 향상
    clean_tag_re = re.compile(r'<[^>]*>')
    clean_num_re = re.compile(r'[-^0-9]')
    
    # ⭐ 커스텀 단어와 네이버 사전 단어가 겹치지 않게 방지하는 세트(Set)
    existing_words = {w["단어"] for w in words}
    
    for item in search_results:
        clean_word = item.get('handleEntry', '')
        
        # 💡 최적화 4: 태그 청소
        clean_word = clean_word.replace('<b>', '').replace('</b>', '')
        clean_word = clean_num_re.sub('', clean_word).strip()
        
        # 💡 최적화 5: 조기 종료 패턴 (조건에 맞지 않거나, 이미 추가된 중복 단어면 건너뜀)
        if not (clean_word.startswith(target_letter) and len(clean_word) >= 2):
            continue
            
        if clean_word in existing_words:
            continue
            
        meaning = ""
        pos = "단어"
        
        means_collector = item.get('meansCollector')
        if means_collector:
            pos = means_collector[0].get('partOfSpeech', '단어')
            means = means_collector[0].get('means', [])
            if means:
                meaning = means[0].get('value', '')
                meaning = clean_tag_re.sub('', meaning)
        
        words.append({"단어": clean_word, "품사": pos, "뜻": meaning})
        existing_words.add(clean_word)
                
    return words

# ==========================================
# 🎈 UI 및 결과 출력부
# ==========================================

user_input = st.text_input("글자 또는 단어를 입력하세요 (예: 슘, 늄, 이리듐):").strip()

if user_input:
    # 마지막 글자 추출
    target_letter = user_input[-1]
    
    st.subheader(f"🔍 '{target_letter}'(으)로 시작하는 추천 단어")
    
    with st.spinner("사전에서 단어를 찾는 중입니다..."):
        word_list = get_words_via_web(target_letter)
        
    if word_list:
        st.success(f"총 {len(word_list)}개의 단어를 찾았습니다!")
        st.dataframe(word_list, use_container_width=True)
    else:
        st.warning(f"⚠️ '{target_letter}'(으)로 시작하는 두 글자 이상의 단어를 찾지 못했습니다.")
