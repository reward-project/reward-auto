from mobile_automation import MobileAutomation
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time

class CoupangAutomation(MobileAutomation):
    def __init__(self):
        super().__init__()
        self.scroll_attempts = 0
        self.max_scroll_attempts = 10  # 한 페이지당 최대 스크롤 횟수
        
    def search_product(self, keyword):
        """쿠팡 앱에서 상품 검색"""
        try:
            # 검색창 클릭
            self.find_and_click_element("search_button")
            
            # 검색어 입력
            search_box = self.wait.until(
                EC.presence_of_element_located((AppiumBy.ID, "search_edit_text"))
            )
            search_box.send_keys(keyword)
            
            # 검색 실행
            self.find_and_click_element("search_submit_button")
            return True
        except Exception as e:
            print(f"검색 중 에러 발생: {str(e)}")
            return False

    def scroll_down(self):
        """화면 아래로 스크롤"""
        try:
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
            time.sleep(1.5)  # 스크롤 후 로딩 대기
            return True
        except Exception as e:
            print(f"스크롤 중 에러 발생: {str(e)}")
            return False

    def find_product_by_title(self, product_title):
        """상품 제목으로 상품 찾기"""
        try:
            # XPath로 상품 찾기
            product = self.driver.find_element(
                AppiumBy.XPATH,
                f"//android.widget.TextView[@text='{product_title}']"
            )
            product.click()
            return True
        except NoSuchElementException:
            return False

    def go_to_next_page(self):
        """다음 페이지로 이동"""
        try:
            next_button = self.driver.find_element(
                AppiumBy.XPATH,
                "//android.widget.Button[contains(@text, '다음') or contains(@text, '→')]"
            )
            next_button.click()
            time.sleep(2)  # 페이지 로딩 대기
            self.scroll_attempts = 0  # 스크롤 시도 횟수 초기화
            return True
        except NoSuchElementException:
            print("더 이상 다음 페이지가 없습니다.")
            return False

    def search_and_find_product(self, keyword, product_title):
        """상품 검색부터 찾기까지의 전체 프로세스"""
        if not self.search_product(keyword):
            return False

        while True:
            # 현재 화면에서 상품 찾기
            if self.find_product_by_title(product_title):
                print(f"상품을 찾았습니다: {product_title}")
                return True

            # 현재 페이지에서 스크롤 시도
            if self.scroll_attempts < self.max_scroll_attempts:
                self.scroll_down()
                self.scroll_attempts += 1
                continue

            # 최대 스크롤 도달 시 다음 페이지로 이동
            if not self.go_to_next_page():
                print("상품을 찾지 못했습니다.")
                return False

    def run_scenario(self, keyword, product_title):
        """시나리오 실행"""
        try:
            return self.search_and_find_product(keyword, product_title)
        except Exception as e:
            print(f"시나리오 실행 중 에러 발생: {str(e)}")
            return False

# 실행 예시
if __name__ == "__main__":
    automation = CoupangAutomation()
    keyword = "노트북"
    product_title = "LG gram 2024년형 17"
    automation.run_scenario(keyword, product_title) 