from appium import webdriver
from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class MobileAutomation:
    def __init__(self):
        # Appium 설정
        self.desired_caps = {
            'platformName': 'Android',  # 또는 'iOS'
            'deviceName': '디바이스이름',
            'automationName': 'UiAutomator2',  # Android의 경우
            'appPackage': '앱패키지명',
            'appActivity': '시작액티비티명',
            'noReset': True
        }
        self.driver = webdriver.Remote('http://localhost:4723/wd/hub', self.desired_caps)
        self.wait = WebDriverWait(self.driver, 20)

    def safe_click(self, locator, locator_type=MobileBy.ID, timeout=20):
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
            self.driver.tap([(500, 500)], 500)  # 화면 중앙 탭
            
            # 일반적인 닫기 버튼 처리
            close_buttons = [
                '//android.widget.Button[@text="닫기"]',
                '//android.widget.Button[@text="확인"]',
                # 더 많은 팝업 패턴 추가
            ]
            
            for button in close_buttons:
                try:
                    self.driver.find_element(MobileBy.XPATH, button).click()
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
                EC.presence_of_element_located((MobileBy.ID, identifier))
            )
            element.click()
            return True
        except TimeoutException:
            try:
                # XPATH로 찾기
                element = self.wait.until(
                    EC.presence_of_element_located((MobileBy.XPATH, f"//*[@text='{identifier}']"))
                )
                element.click()
                return True
            except TimeoutException:
                print(f"요소를 찾을 수 없음: {identifier}")
                return False