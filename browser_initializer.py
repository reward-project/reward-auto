from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from utils.logger import Logger
import os

class BrowserInitializer:
    def __init__(self):
        self.logger = Logger('BrowserInitializer')
        
    def initialize_browser(self):
        """모바일 크롬 브라우저 초기화"""
        try:
            self.logger.info("=== 브라우저 초기화 시작 ===")
            
            # ChromeDriver 자동 다운로드
            chromedriver_path = ChromeDriverManager().install()
            self.logger.debug(f"ChromeDriver 경로: {chromedriver_path}")
            
            # Appium 설정
            options = UiAutomator2Options()
            options.set_capability('platformName', 'Android')
            options.set_capability('deviceName', 'emulator-5554')
            options.set_capability('automationName', 'UiAutomator2')
            options.set_capability('browserName', 'Chrome')
            options.set_capability('noReset', True)
            
            # ADB 타임아웃 설정
            options.set_capability('adbExecTimeout', 60000)
            options.set_capability('newCommandTimeout', 60000)
            options.set_capability('androidDeviceReadyTimeout', 60000)
            
            # 크롬 옵션 설정
            options.set_capability('chromedriverExecutable', chromedriver_path)
            options.set_capability('chromeOptions', {
                'w3c': False,
                'args': ['--no-sandbox', '--disable-dev-shm-usage']
            })
            
            # WebDriver 초기화
            driver = webdriver.Remote('http://127.0.0.1:4723', options=options)
            self.logger.info("브라우저 초기화 성공")
            
            return driver
            
        except Exception as e:
            self.logger.error(f"브라우저 초기화 실패: {str(e)}")
            raise 