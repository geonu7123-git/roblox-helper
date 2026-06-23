import streamlit as st
import requests
import json

# 페이지 설정
st.set_page_config(page_title="로블록스 끝말잇기 도우미", page_icon="📝", layout="centered")

st.title("📝 로블록스 끝말잇기 도우미")
st.caption("네이버 국어사전 검색 결과를 바탕으로 다음 단어를 추천합니다.")

def get_words_via_web(target_letter):
    # 네이버 사전 검색 API 주소 수정 및 인코딩 안전화
    url = f"https://ko.dict.naver.com/api3/koko/search?query={target_letter}*"
    
    # 실제 브라우저와 거의 유사하게 헤더 구성 (차단 방지)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://ko.dict.naver.com/",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        # 반환된 데이터가 JSON 형태가 맞는지 먼저 확인
        try:
            data = response.json()
        except json.JSONDecodeError:
            st.error("⚠️ 사전 서버에서 올바르지 않은 응답을 보냈습니다. (잠시 후 다시 시도해 주세요)")
            # 디버깅용 (어떤 데이터가 왔는지 살짝 출력)
            with st.expander("에러 상세 내용 보기"):
                st.code(response.text[:500])
            return []
            
        search_results = data.get('searchResultMap', {}).get('searchResultListMap', {}).get('WORD', {}).get('items', [])
        
        words = []
        for item in search_results:
            # HTML 태그 제거
            clean_word = item.get('handleEntry', '')
            clean_word = clean_word.replace('', '').replace('<b>', '').replace('</b>', '')
            
            # 불필요한 기호 및 숫자 제거
            import re
            clean_word = re.sub(r'[-^0-9]', '', clean_word).strip()
            
            # 뜻 추출
            meaning = ""
            if item.get('meansCollector'):
                means = item['meansCollector'][0].get('means', [])
                if means:
                    meaning = means[0].get('value', '')
                    meaning = re.sub(r'<[^>]*>', '', meaning) # HTML 태그 제거
            
            # 품사 추출
            pos = "단어"
            if item.get('meansCollector'):
                pos = item['meansCollector'][0].get('partOfSpeech', '단어')
            
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

    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")
        return []

# --- UI 레이아웃 ---
input_word = st.text_input("상대방이 제시한 단어를 입력하세요:", placeholder="예: 기차")

if input_word:
    last_letter = input_word[-1]
    st.write(f"🔍 **'{last_letter}'**(으)로 시작하는 단어를 검색합니다.")
    
    with st.spinner("네이버 사전 실시간 검색 중..."):
        results = get_words_via_web(last_letter)
    
    if results:
        st.success(f"추천 단어를 찾았습니다!")
        st.dataframe(results, use_container_width=True)
    else:
        st.info(f"'{last_letter}'로 시작하는 단어를 찾지 못했거나 에러가 발생했습니다.")
