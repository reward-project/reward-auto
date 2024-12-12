from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import os

class MobileAutomation:
    def __init__(self):
        # ChromeDriver 자동 다운로드
        chromedriver_path = ChromeDriverManager().install()
        
        # Appium 설정
        options = UiAutomator2Options()
        options.set_capability('platformName', 'Android')
        options.set_capability('deviceName', 'emulator-5554')
        options.set_capability('automationName', 'UiAutomator2')
        options.set_capability('appPackage', 'com.coupang.mobile')
        options.set_capability('appActivity', '.SplashActivity')
        options.set_capability('noReset', True)
        options.set_capability('chromedriverExecutable', chromedriver_path)
        
        # 크롬 디버깅 관련 설정 추가
        options.set_capability('chromedriverExecutableDir', '/path/to/chromedriver')
        options.set_capability('ensureWebviewsHavePages', True)
        options.set_capability('enableWebviewDetailsCollection', True)
        options.set_capability('showChromedriverLog', True)
        
        # 웹뷰 관련 설정은 일단 비활성화
        # options.set_capability('autoWebview', True)
        # options.set_capability('webviewDevtoolsPort', 9222)
        
        try:
            self.driver = webdriver.Remote('http://127.0.0.1:4723', options=options)
            self.wait = WebDriverWait(self.driver, 20)
        except Exception as e:
            print(f"Appium 서버 연결 실패: {str(e)}")
            raise

    def safe_click(self, locator, locator_type=AppiumBy.ID, timeout=20):
        """안전한 클릭 동작을 수행하는 메소드"""
        try:
            element = self.wait.until(
                EC.presence_of_element_located((locator_type, locator))
            )
            element.click()
            return True
        except TimeoutException:
            print(f"요소를 찾을 수 없음: {locator}")
            self.handle_popup()  # 팝업 처리
            return False

    def handle_popup(self):
        """예상치 못한 팝업을 처리하는 메소드"""
        try:
            # 빈 화면 클릭 (팝업 닫기)
            self.driver.tap([(500, 500)], 500)  # 화면 중앙 
            
            # 일반적인 닫기 버튼 처리
            close_buttons = [
                '//android.widget.Button[@text="닫기"]',
                '//android.widget.Button[@text="확"]',
                # 더 많은 팝업 패턴 추가
            ]
            
            for button in close_buttons:
                try:
                    self.driver.find_element(AppiumBy.XPATH, button).click()
                    return True
                except NoSuchElementException:
                    continue
                    
        except Exception as e:
            print(f"팝업 처리 중 에러 발생: {str(e)}")
            return False

    def execute_step(self, step_function):
        """각 단계를 실행하고 결과를 확인하는 메소드"""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                result = step_function()
                if result:
                    return True
                else:
                    self.handle_popup()
                    retry_count += 1
            except Exception as e:
                print(f"단계 실행 중 에러 발생: {str(e)}")
                self.handle_popup()
                retry_count += 1
        
        return False

    def find_and_click_element(self, identifier, wait_time=20):
        """요소를 찾아서 클릭하는 메소드"""
        try:
            # ID로 찾기
            element = self.wait.until(
                EC.presence_of_element_located((AppiumBy.ID, identifier))
            )
            element.click()
            return True
        except TimeoutException:
            try:
                # XPATH로 찾기
                element = self.wait.until(
                    EC.presence_of_element_located((AppiumBy.XPATH, f"//*[@text='{identifier}']"))
                )
                element.click()
                return True
            except TimeoutException:
                print(f"요소를 찾을 수 없음: {identifier}")
                return False