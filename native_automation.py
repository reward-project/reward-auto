from mobile_automation import MobileAutomation
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class CoupangNativeAutomation(MobileAutomation):
    def search_product(self, keyword):
        """상품 검색"""
        try:
            # 검색창 찾기 (리소스 ID 사용)
            search_btn = self.driver.find_element(AppiumBy.ID, "com.coupang.mobile:id/search_button")
            search_btn.click()
            
            # 검색어 입력
            search_input = self.driver.find_element(AppiumBy.ID, "com.coupang.mobile:id/search_input")
            search_input.send_keys(keyword)
            
            # 검색 실행
            search_input.click()  # 키보드의 검색 버튼
            return True
        except Exception as e:
            print(f"검색 중 에러: {str(e)}")
            return False

    def find_product_by_text(self, product_name):
        """상품명으로 상품 찾기"""
        max_scroll = 5
        scroll_count = 0
        
        while scroll_count < max_scroll:
            try:
                # UiSelector 사용하여 텍스트 포함된 요소 찾기
                selector = f'new UiSelector().textContains("{product_name}")'
                element = self.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, selector)
                element.click()
                return True
            except:
                # 스크롤
                self.scroll_down()
                scroll_count += 1
        
        return False

    def scroll_down(self):
        """화면 스크롤"""
        screen_size = self.driver.get_window_size()
        start_y = screen_size['height'] * 0.8
        end_y = screen_size['height'] * 0.2
        
        self.driver.swipe(
            screen_size['width'] // 2,
            start_y,
            screen_size['width'] // 2,
            end_y,
            duration=800
        ) 