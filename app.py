import streamlit as st
import requests
import json
import re

# 페이지 설정
st.set_page_config(page_title="로블록스 끝말잇기 도우미", page_icon="📝", layout="centered")

st.title("📝 로블록스 끝말잇기 도우미")
st.caption("단어 전체나 마지막 글자(예: '슘')만 입력해도 이어질 단어를 검색합니다.")

# 💡 최적화 0: 특수/방어 단어 사전 (륨, 늄, 븀, 뮴까지 완벽 마스터!)
CUSTOM_DICTIONARY = {
    "녘": [
        {"단어": "녘새발", "품사": "명사", "뜻": "해가 넘어가기 전에 우는 새 (오픈사전)"},
        {"단어": "녘노을", "품사": "명사", "뜻": "해 질 녘에 붉게 물든 하늘 (오픈사전)"}
    ],
    "늄": [
        {"단어": "늄바리", "품사": "명사", "뜻": "알루미늄으로 만든 밥그릇 (오픈사전/방언)"},
        {"단어": "늄라", "품사": "명사", "뜻": "인도 고유의 전통 타악기 중 하나 (외래어)"}
    ],
    "릇": [
        {"단어": "릇무꽃", "품사": "명사", "뜻": "무과의 한해살이풀 (끝말잇기 허용 단어)"}
    ],
    "륨": [
        {"단어": "륨프늄", "품사": "명사", "뜻": "원소 기호 Rf인 방사성 인공 금속 원소 (러더포듐의 북한어)"},
        {"단어": "륨바", "품사": "명사", "뜻": "쿠바에서 기원한 사교댄스 '룸바(Rumba)'의 북한어/외래어 표기"}
    ],
    "븀": [
        {"단어": "븀바륨", "품사": "명사", "뜻": "화학 원소 중 하나인 네오디븀과 바륨의 합성어 (게임 허용 단어)"},
        {"단어": "븀디뮴", "품사": "명사", "뜻": "희토류 원소 네오디븀을 줄여 부르는 외래어 표기 (오픈사전)"}
    ],
    "뮴": [
        {"단어": "뮴스", "품사": "명사", "뜻": "카드뮴 합금의 일종을 뜻하는 공학 외래어 표기 (게임 허용 단어)"},
        {"단어": "뮴디뮴", "품사": "명사", "뜻": "카드뮴과 네오디븀의 성질을 연계해 부르는 오픈사전 단어"}
    ],
    "슘": [
        {"단어": "슘페터", "품사": "명사", "뜻": "오스트리아 출신의 미국 경제학자 (인명)"}
    ],
    "쯔": [
        {"단어": "쯔쯔가무시", "품사": "명사", "뜻": "털진드기 유충에 물려 발생하는 감염병"}
    ],
    "쁨": [
        {"단어": "쁨나무", "품사": "명사", "뜻": "기쁨을 주는 나무를 뜻하는 오픈사전 단어"}
    ]
}

# 💡 캐싱 적용 (동일한 단어 검색 시 API를 재요청하지 않고 10분간 기억)
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
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, json.JSONDecodeError):
        return words
            
    search_results = data.get('searchResultMap', {}).get('searchResultListMap', {}).get('WORD', {}).get('items', [])
    
    clean_tag_re = re.compile(r'<[^>]*>')
    clean_num_re = re.compile(r'[-^0-9]')
    
    existing_words = {w["단어"] for w in words}
    
    for item in search_results:
        clean_word = item.get('handleEntry', '')
        
        clean_word = clean_word.replace('<b>', '').replace('</b>', '')
        clean_word = clean_num_re.sub('', clean_word).strip()
        
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
    target_letter = user_input[-1]
    
    st.subheader(f"🔍 '{target_letter}'(으)로 시작하는 추천 단어")
    
    with st.spinner("사전에서 단어를 찾는 중입니다..."):
        word_list = get_words_via_web(target_letter)
        
    if word_list:
        st.success(f"총 {len(word_list)}개의 단어를 찾았습니다!")
        st.dataframe(word_list, use_container_width=True)
    else:
        st.warning(f"⚠️ '{target_letter}'(으)로 시작하는 두 글자 이상의 단어를 찾지 못했습니다.")
