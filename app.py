import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

# 페이지 설정
st.set_page_config(page_title="로블록스 끝말잇기 도우미 (무설치 버전)", page_icon="📝", layout="centered")

st.title("📝 로블록스 끝말잇기 도우미")
st.caption("API 없이 네이버 국어사전 검색 결과를 바탕으로 다음 단어를 추천합니다.")

# 끝말잇기 크롤링 로직 함수
def get_words_via_web(target_letter):
    # 네이버 국어사전에서 'X로 시작하는 단어' 검색 URL
    # 정렬 기준을 위해 단어 시작 패턴 검색 활용
    url = f"https://ko.dict.naver.com/api3/koko/search?query={target_letter}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        # 네이버 사전 내부 검색 API (인증 불필요한 공개 주소) 활용
        search_url = f"https://ko.dict.naver.com/api3/koko/search?query={target_letter}*"
        response = requests.get(search_url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            search_results = data.get('searchResultMap', {}).get('searchResultListMap', {}).get('WORD', {}).get('items', [])
            
            words = []
            for item in search_results:
                # HTML 태그 제거하고 순수 단어만 추출
                clean_word = re.sub(r'<[^>]*>', '', item.get('handleEntry', ''))
                # 숫로나 기호 제거 (예: 바나나-다 -> 바나나다)
                clean_word = re.sub(r'[-^0-9]', '', clean_word).strip()
                
                # 품사 정보 가져오기
                pos = item.get('meansCollector', [{}])[0].get('partOfSpeech', '단어') if item.get('meansCollector') else '단어'
                # 뜻 요약
                meaning = item.get('meansCollector', [{}])[0].get('means', [{}])[0].get('value', '') if item.get('meansCollector') else ''
                meaning = re.sub(r'<[^>]*>', '', meaning)
                
                # 입력한 글자로 시작하고 2글자 이상인 단어만 필터링
                if clean_word.startswith(target_letter) and len(clean_word) >= 2:
                    words.append({"단어": clean_word, "품사": pos, "뜻": meaning})
            
            # 중복 단어 제거
            seen = set()
            unique_words = []
            for w in words:
                if w['단어'] not in seen:
                    seen.add(w['단어'])
                    unique_words.append(w)
                    
            return unique_words
        else:
            st.error("사전 데이터를 가져오지 못했습니다.")
            return []
    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")
        return []

# --- UI 레이아웃 ---
input_word = st.text_input("상대방이 제시한 단어를 입력하세요:", placeholder="예: 자동차")

if input_word:
    # 마지막 글자 추출
    last_letter = input_word[-1]
    st.write(f"🔍 **'{last_letter}'**(으)로 시작하는 단어를 실시간으로 검색합니다.")
    
    with st.spinner("네이버 사전 검색 중..."):
        results = get_words_via_web(last_letter)
    
    if results:
        st.success(f"다음 단어로 쓸 수 있는 추천 단어입니다!")
        # 테이블 형태로 출력
        st.dataframe(results, use_container_width=True)
    else:
        st.info(f"'{last_letter}'로 시작하는 적당한 단어를 찾지 못했습니다.")
