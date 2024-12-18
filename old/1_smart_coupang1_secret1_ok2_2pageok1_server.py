from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from utils.logger import Logger
import os
import urllib.parse

class BrowserInitializer:
    def __init__(self):
        self.logger = Logger('BrowserInitializer')
        
    def initialize_browser(self):
        """서버용 브라우저 초기화"""
        try:
            self.logger.info("=== 브라우저 초기화 시작 ===")
            
            # Chrome 옵션 설정
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")  # Sandbox 비활성화
            chrome_options.add_argument("--disable-dev-shm-usage")  # 공유 메모리 문제 해결
            chrome_options.add_argument("--headless")  # Headless 모드 활성화
            chrome_options.add_argument("--disable-gpu")  # GPU 가속 비활성화
            chrome_options.add_argument("--disable-extensions")  # 확장 프로그램 비활성화
            chrome_options.add_argument("--disable-software-rasterizer")
            chrome_options.add_argument("--ignore-certificate-errors")
            chrome_options.add_argument("--window-size=412,915")  # 모바일 화면 크기
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36")
            
            # ChromeDriver 서비스 설정 (Linux 서버용)
            service = Service('/usr/local/bin/chromedriver')  # Linux 경로
            
            # WebDriver 초기화
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            self.logger.info("브라우저 초기화 성공")
            return driver
            
        except Exception as e:
            self.logger.error(f"브라우저 초기화 실패: {str(e)}")
            raise e

def search_product(keyword, product_id):
    """쿠팡에서 상품을 검색하고 순위를 찾는 함수"""
    browser = None
    try:
        # 브라우저 설정
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")  # Sandbox 비활성화
        options.add_argument("--disable-dev-shm-usage")  # 공유 메모리 문제 해결
        options.add_argument("--headless")  # Headless 모드 활성화
        options.add_argument("--disable-gpu")  # GPU 가속 비활성화
        options.add_argument("--disable-extensions")  # 확장 프로그램 비활성화
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--window-size=1920x1080")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36")
        
        # ChromeDriver 서비스 설정 (Linux 서버용)
        service = Service('/usr/local/bin/chromedriver')  # Linux 경로
        browser = webdriver.Chrome(service=service, options=options)
        
        # 나머지 코드는 그대로 유지
        encoded_keyword = urllib.parse.quote(keyword)
        base_url = f'https://www.coupang.com/np/search?component=&q={encoded_keyword}&channel=user'
        
        # ... (이하 코드는 동일하게 유지)
