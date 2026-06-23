import streamlit as st
import requests
import json
import re

# 페이지 설정
st.set_page_config(page_title="로블록스 끝말잇기 도우미", page_icon="📝", layout="centered")

st.title("📝 로블록스 끝말잇기 도우미")
st.caption("단어 전체나 마지막 글자(예: '슘')만 입력해도 이어질 단어를 검색합니다.")

def get_words_via_web(target_letter):
    # 네이버 사전 검색 API 주소
    url = f"https://ko.dict.naver.com/api3/koko/search?query={target_letter}*"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://ko.dict.naver.com/",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        try:
            data = response.json()
        except json.JSONDecodeError:
            st.error("⚠️ 사전 서버에서 응답을 받지 못했습니다. 잠시 후 다시 시도해 주세요.")
            return []
            
        search_results = data.get('searchResultMap', {}).get('searchResultListMap', {}).get('WORD', {}).get('items', [])
        
        words = []
        for item in search_results:
            clean_word = item.get('handleEntry', '')
            clean_word = clean_word.replace('', '').replace('<b>', '').replace('</b>', '')
            clean_word = re.sub(r'[-^0-9]', '', clean_word).strip()
            
            meaning = ""
            if item.get('meansCollector'):
                means = item['meansCollector'][0].get('means', [])
                if means:
                    meaning = means[0].get('value', '')
                    meaning = re.sub(r'<[^>]*>', '', meaning)
            
            pos = "단어"
            if item.get('meansCollector'):
                pos = item['meansCollector'][0].get('partOfSpeech', '단어')
            
            # 검색한 글자로 시작하고 2글자 이상인 단어 필터링
            if clean_word.startswith(target_letter) and len(clean_word) >= 2:
                words.append({"단어": clean_word, "품사": pos, "뜻":
