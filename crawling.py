import requests
from bs4 import BeautifulSoup
import time
#import schedule
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
    
    # 이 부분은 주소 수정이 필요 없으므로 기존대로 유지
    TARGET_URL = "https://www.gbe.kr/gs/na/ntt/selectNttList.do?mi=19265&bbsId=2577" 
    
    try:
        response = requests.get(TARGET_URL)
        response.encoding = 'utf-8' # 인코딩 명시적 지정
        soup = BeautifulSoup(response.text, 'html.parser')

        # [게시물 리스트 선택] 게시물 전체 리스트 (tr 태그들의 리스트)를 가져옵니다.
        post_elements = soup.select(".BD_list tr")
        sent_posts = load_sent_posts()
        new_posts_found = False

        for post in post_elements:
            # post (tr 태그) 안에서 모든 td 태그를 리스트로 추출합니다.
            td_elements = post.find_all("td")
            # td 태그가 2개 이상 존재하는 경우에만 (게시물 데이터일 경우) 처리
            if len(td_elements) < 3:
                continue

            # 1. 제목 및 링크 추출: 첫 번째 <td> (td_elements[0]) 안에서 <a> 태그를 찾습니다.
            title_tag = td_elements[1].find("a") 
            
            # 2. 작성자 추출: 두 번째 <td> (td_elements[1])의 텍스트를 가져옵니다.
            # get_text(strip=True)를 사용하여 불필요한 공백과 개행 문자를 제거합니다.
            author = td_elements[2].get_text(strip=True)

            if not title_tag:
                continue
                
            # <a> 태그에서 텍스트(제목) 추출
            title = title_tag.get_text(strip=True) 
            # <a> 태그의 href 속성(링크) 추출
            link = title_tag["href"] 
            
            # [수정] 상대 경로일 경우, 자바스크립트 함수 호출이 아닌 실제 링크를 만들어야 합니다.
            # data-id 속성 값을 추출하여 링크를 재구성하는 것이 더 정확합니다.
            data_id = title_tag.get('data-id')
            if data_id:
                # 사이트의 링크 구조를 분석하여 data-id를 사용하는 링크로 재구성합니다.
                # 이 구조는 사이트마다 다르니, 실제 작동하는 링크를 확인 후 수정해야 합니다.
                link = f"https://www.gbe.kr/gs/na/ntt/selectNttInfo.do?mi=19265&bbsId=2577&nttSn={data_id}"
            else:
                # data-id가 없는 경우나 다른 링크 형태인 경우 건너뜁니다.
                 continue 
            
            # 고유 ID 생성 (재구성된 링크를 사용)
            post_id = link 

            # 1. 키워드 검사 및 2. 중복 검사는 기존 로직 유지
            if any(keyword in title for keyword in KEYWORDS):
                if post_id not in sent_posts:
                    # [수정] 발송 메시지에 작성자(author) 정보를 추가합니다.
                    msg = f"🔔 [새로운 공고 발견]\n*제목*: {title}\n*작성자*: {author}\n*링크*: {link}"
                    print(msg)
                    send_telegram_message(msg)
                    
                    sent_posts.append(post_id)
                    new_posts_found = True
        
        if new_posts_found:
           save_sent_posts(sent_posts)
            
    except Exception as e:
        print(f"에러 발생: {e}")

# --- 스케줄링 실행 ---
# 1시간마다 실행
#schedule.every(24).hours.do(check_new_posts)

# 테스트를 위해 즉시 한 번 실행
check_new_posts()

#while True:
#    schedule.run_pending()
#    time.sleep(1)
