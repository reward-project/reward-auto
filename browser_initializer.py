from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from utils.logger import Logger
import os

class BrowserInitializer:
    def __init__(self):
        self.logger = Logger('BrowserInitializer')
        
    def initialize_browser(self):
        """모라우저 초기화"""
        try:
            self.logger.info("=== 브라우저 초기화 시작 ===")
            
            # Chrome 옵션 설정
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")  # Sandbox 비활성화
            chrome_options.add_argument("--disable-dev-shm-usage")  # 공유 메모리 문제 해결
            chrome_options.add_argument("--disable-gpu")  # GPU 가속 비활성화
            chrome_options.add_argument("--disable-extensions")  # 확장 프로그램 비활성화
            chrome_options.add_argument("--disable-software-rasterizer")
            chrome_options.add_argument("--ignore-certificate-errors")
            chrome_options.add_argument("--window-size=412,915")  # 모바일 화면 크기
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36")
            
            # ChromeDriver 서비스 설정
            service = Service('chromedriver.exe')  # Windows의 경우
            
            # WebDriver 초기화
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            self.logger.info("브라우저 초기화 성공")
            return driver
            
        except Exception as e:
            self.logger.error(f"브라우저 초기화 실패: {str(e)}")
            raise e