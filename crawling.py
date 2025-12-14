import requests
from bs4 import BeautifulSoup
import time
import json
import os

# --- [설정] 환경 변수 및 키워드 ---
KEYWORDS = ["채용", "모집", "공고", "늘봄"]
DATA_FILE = "sent_posts.json"

# 환경변수 로드 및 예외처리
BOT_TOKEN = os.environ.get('BOT_TOKEN')
try:
    CHAT_ID = int(os.environ.get('CHAT_ID'))
except (TypeError, ValueError):
    print("ERROR: CHAT_ID가 설정되지 않았거나 숫자가 아닙니다.")
    CHAT_ID = 0

# --- [공통 함수] 알림 및 데이터 관리 ---
def send_telegram_message(text):
    if not BOT_TOKEN or not CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"알림 발송 실패: {e}")

def load_sent_posts():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_sent_posts(posts):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=4)

# ============================================================================
# [사이트별 파싱 함수 구간] 
# 각 함수는 soup 객체를 받아 -> [{'id':, 'title':, 'link':, 'author':}, ...] 리스트 반환
# ============================================================================

def parse_site_A(soup):
    """
    1번 사이트: 경산교육청
    구조: .BD_list 테이블 형태
    """
    results = []
    base_url = "https://www.gbe.kr/gs/na/ntt/selectNttInfo.do?mi=19265&bbsId=2577&nttSn="
    
    rows = soup.select(".BD_list tr")
    for row in rows:
        tds = row.find_all("td")
        if len(tds) < 3: continue
        
        title_tag = tds[1].find("a")
        if not title_tag: continue
        
        title = title_tag.get_text(strip=True)
        author = tds[2].get_text(strip=True)
        
        # data-id를 이용한 링크 재구성
        data_id = title_tag.get('data-id')
        if not data_id: continue
        
        link = f"{base_url}{data_id}"
        
        results.append({
            'id': link,       # 고유 식별자 (보통 링크 사용)
            'title': title,
            'link': link,
            'author': author
        })
    return results

def parse_site_B(soup):
    """
    2번 사이트: 청도교육청
    구조: .BD_list 테이블 형태
    """
    results = []
    base_url = "https://www.gbe.kr/cd/na/ntt/selectNttInfo.do?mi=10467&bbsId=3251&nttSn="
    
    rows = soup.select(".BD_list tr")
    for row in rows:
        tds = row.find_all("td")
        if len(tds) < 3: continue
        
        title_tag = tds[1].find("a")
        if not title_tag: continue
        
        title = title_tag.get_text(strip=True)
        author = tds[2].get_text(strip=True)
        
        # data-id를 이용한 링크 재구성
        data_id = title_tag.get('data-id')
        if not data_id: continue
        
        link = f"{base_url}{data_id}"
        
        results.append({
            'id': link,       # 고유 식별자 (보통 링크 사용)
            'title': title,
            'link': link,
            'author': author
        })
    return results

def parse_site_C(soup):
    """
    3번 사이트: 영천교육청
    구조: .BD_list 테이블 형태
    """
    results = []
    base_url = "https://www.gbe.kr/yc/na/ntt/selectNttInfo.do?mi=4403&bbsId=2078&nttSn="
    
    rows = soup.select(".BD_list tr")
    for row in rows:
        tds = row.find_all("td")
        if len(tds) < 3: continue
        
        title_tag = tds[1].find("a")
        if not title_tag: continue
        
        title = title_tag.get_text(strip=True)
        author = tds[2].get_text(strip=True)
        
        # data-id를 이용한 링크 재구성
        data_id = title_tag.get('data-id')
        if not data_id: continue
        
        link = f"{base_url}{data_id}"
        
        results.append({
            'id': link,       # 고유 식별자 (보통 링크 사용)
            'title': title,
            'link': link,
            'author': author
        })
    return results

def parse_site_D(soup):
    """
    4번 사이트: 경주교육청
    구조: .BD_list 테이블 형태
    """
    results = []
    base_url = "https://www.gbe.kr/gj/na/ntt/selectNttInfo.do?mi=11638&bbsId=1583&nttSn="
    
    rows = soup.select(".BD_list tr")
    for row in rows:
        tds = row.find_all("td")
        if len(tds) < 3: continue
        
        title_tag = tds[1].find("a")
        if not title_tag: continue
        
        title = title_tag.get_text(strip=True)
        author = tds[2].get_text(strip=True)
        
        # data-id를 이용한 링크 재구성
        data_id = title_tag.get('data-id')
        if not data_id: continue
        
        link = f"{base_url}{data_id}"
        
        results.append({
            'id': link,       # 고유 식별자 (보통 링크 사용)
            'title': title,
            'link': link,
            'author': author
        })
    return results

# ============================================================================
# [메인 실행 로직]
# ============================================================================

def run_crawlers():
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 크롤링 시작...")
    sent_posts = load_sent_posts()
    new_posts_found = False
    
    # 1. 크롤링 대상 사이트 리스트 정의
    # (URL, 파싱함수이름, 사이트별칭)
    TARGETS = [
        (
            "https://www.gbe.kr/gs/na/ntt/selectNttList.do?mi=19265&bbsId=2577", 
            parse_site_A,
            "경산교육청"
        ),
        (
            "https://www.gbe.kr/cd/na/ntt/selectNttList.do?mi=10467&bbsId=3251",
            parse_site_B,
            "청도교육청"
        ),
        (
            "https://www.gbe.kr/yc/na/ntt/selectNttList.do?mi=4403&bbsId=2078",
            parse_site_C,
            "영천교육청"
        ),
        (
            "https://www.gbe.kr/gj/na/ntt/selectNttList.do?mi=11638&bbsId=1583",
            parse_site_D,
            "경주교육청"
        ),
        # 필요하면 더 추가 가능
    ]

    for url, parser_func, site_name in TARGETS:
        print(f"  Target: {site_name} 확인 중...")
        try:
            response = requests.get(url, timeout=10) # 10초 타임아웃
            response.encoding = 'utf-8' # 필요시 'euc-kr' 등으로 변경
            
            if response.status_code != 200:
                print(f"  [Error] {site_name} 접속 실패: {response.status_code}")
                continue
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 해당 사이트 전용 파서 실행
            posts = parser_func(soup) 

            for post in posts:
                # 키워드 필터링
                if any(k in post['title'] for k in KEYWORDS):
                    # 중복 필터링
                    if post['id'] not in sent_posts:
                        msg = (
                            f"🔔 [{site_name} 새 공고]\n"
                            f"*제목*: {post['title']}\n"
                            f"*작성자*: {post['author']}\n"
                            f"*링크*: {post['link']}"
                        )
                        print(msg)
                        send_telegram_message(msg)
                        
                        sent_posts.append(post['id'])
                        new_posts_found = True
                        
        except Exception as e:
            print(f"  [Error] {site_name} 처리 중 오류: {e}")

    # 변경사항이 있으면 파일 저장
    if new_posts_found:
        save_sent_posts(sent_posts)
    
    print("크롤링 종료.")

if __name__ == "__main__":
    run_crawlers()
