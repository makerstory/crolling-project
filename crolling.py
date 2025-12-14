import requests
from bs4 import BeautifulSoup
import time
import schedule
import json
import os

# --- 설정 구간 ---
TARGET_URL = "https://www.gbe.kr/gs/na/ntt/selectNttList.do?mi=19265&bbsId=2577"  # 크롤링 할 사이트 주소
KEYWORDS = ["채용", "모집", "공고", "늘봄"]
BOT_TOKEN = "8541608617:AAGLWW1Meg5YovqqmhQzjQ9kSH_d2YwMNlY" # 텔레그램 봇 토큰 os.environ.get('BOT_TOKEN')
CHAT_ID = 8460700603 # 본인의 챗 ID os.environ.get('CHAT_ID')
DATA_FILE = "sent_posts.json" # 중복 방지용 데이터 저장 파일

# --- 알림 발송 함수 (텔레그램) ---
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"알림 발송 실패: {e}")

# --- 기존 알림 내역 불러오기 ---
def load_sent_posts():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# --- 알림 내역 저장하기 ---
def save_sent_posts(posts):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=4)

# --- 크롤링 핵심 로직 ---
def check_new_posts():
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 사이트 점검 시작...")
    
    try:
        response = requests.get(TARGET_URL)
        # 사이트가 차단할 경우 User-Agent 헤더 추가 필요
        # headers = {'User-Agent': 'Mozilla/5.0 ...'} 
        # response = requests.get(TARGET_URL, headers=headers)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # [중요] 사이트 구조에 맞춰 수정해야 하는 부분
        # 예: 게시물 리스트가 <tr class="notice"> 혹은 <li class="item"> 인 경우
        post_elements = soup.select(".board_list tr") 

        sent_posts = load_sent_posts()
        new_posts_found = False

        for post in post_elements:
            # 제목과 링크 추출 (사이트 구조에 따라 .find() 수정 필요)
            title_tag = post.find("a")
            if not title_tag:
                continue
                
            title = title_tag.get_text(strip=True)
            link = title_tag["href"]
            
            # 상대 경로일 경우 절대 경로로 변환
            if not link.startswith("http"):
                link = "https://example.com" + link

            # 고유 ID 생성 (보통 링크를 ID로 사용)
            post_id = link 

            # 1. 키워드 검사
            if any(keyword in title for keyword in KEYWORDS):
                # 2. 중복 검사 (이미 보낸 알림인지)
                if post_id not in sent_posts:
                    msg = f"[새로운 공고 발견]\n제목: {title}\n링크: {link}"
                    print(msg)
                    send_telegram_message(msg)
                    
                    sent_posts.append(post_id)
                    new_posts_found = True
        
        # 새로운 알림이 있었다면 파일 업데이트
        if new_posts_found:
            save_sent_posts(sent_posts)
            
    except Exception as e:
        print(f"에러 발생: {e}")

# --- 스케줄링 실행 ---
# 1시간마다 실행
schedule.every(24).hours.do(check_new_posts)

# 테스트를 위해 즉시 한 번 실행
check_new_posts()

while True:
    schedule.run_pending()
    time.sleep(1)
