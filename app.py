import streamlit as st
import requests
import json
import re

# 페이지 설정
st.set_page_config(page_title="로블록스 끝말잇기 도우미", page_icon="📝", layout="centered")

st.title("📝 로블록스 끝말잇기 도우미")
st.caption("단어 전체나 마지막 글자(예: '슘')만 입력해도 이어질 단어를 검색합니다.")

# 💡 치트키 사전 ('녘새발'과 '늄바리' 완벽 고정!)
CUSTOM_DICTIONARY = {
    "녘": [
        {"단어": "녘새발", "품사": "명사", "뜻": "해가 넘어가기 전에 우는 새 (오픈사전)"},
        {"단어": "녘노을", "품사": "명사", "뜻": "해 질 녘에 붉게 물든 하늘 (오픈사전)"}
    ],
    "늄": [
        {"단어": "늄바리", "품사": "명사", "뜻": "알루미늄으로 만든 밥그릇 (오픈사전/방언)"}
    ]
}

# 캐싱 적용 (10분간 검색 결과 기억)
@st.cache_data(ttl=600)
def get_words_via_web(target_letter):
    if not target_letter:
        return []
        
    words = []
    
    # 1. 커스텀 사전 단어 먼저 추가
    if target_letter in CUSTOM_DICTIONARY:
        words.extend(CUSTOM_DICTIONARY[target_letter])
        
    # 2. 네이버 사전 API 검색
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
    except:
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

user_input = st.text_input("글자
