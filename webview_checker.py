from mobile_automation import MobileAutomation
from appium.webdriver.common.appiumby import AppiumBy
import time
import os

class WebViewChecker(MobileAutomation):
    def check_webview_in_screens(self):
        try:
            screens = [
                {'name': '메인', 'action': None},
                {'name': '검색결과', 'action': self.go_to_search},
                {'name': '상품상세', 'action': self.go_to_product},
                {'name': '카테고리', 'action': self.go_to_category}
            ]
            
            os.makedirs('logs', exist_ok=True)
            
            for screen in screens:
                if screen['action']:
                    screen['action']()
                time.sleep(3)
                
                with open(f"logs/webview_{screen['name']}.log", 'w', encoding='utf-8') as f:
                    webviews = self.driver.find_elements(AppiumBy.CLASS_NAME, "android.webkit.WebView")
                    f.write(f"=== {screen['name']} 화면 WebView 검사 ===\n")
                    f.write(f"WebView 수: {len(webviews)}\n")
                    
                    # 컨텍스트 정보도 함께 저장
                    f.write(f"\n컨텍스트 목록: {self.driver.contexts}\n")
        except Exception as e:
            with open('logs/webview_error.log', 'w', encoding='utf-8') as f:
                f.write(f"WebView 검사 중 에러 발생: {str(e)}")
            raise
    
    def go_to_search(self):
        """검색 화면으로 이동"""
        try:
            search_btn = self.driver.find_element(AppiumBy.ID, "com.coupang.mobile:id/search_button")
            search_btn.click()
            search_input = self.driver.find_element(AppiumBy.ID, "com.coupang.mobile:id/search_input")
            search_input.send_keys("노트북")
            search_input.submit()
        except Exception as e:
            print(f"검색 화면 이동 중 에러: {str(e)}")
            raise
    
    def go_to_product(self):
        """상품 상세 화면으로 이동"""
        try:
            # 첫 번째 상품 클릭
            products = self.driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.TextView")
            for product in products:
                if product.text:  # 상품명이 있는 요소 클릭
                    product.click()
                    break
        except Exception as e:
            print(f"상품 상세 화면 이동 중 에러: {str(e)}")
            raise
    
    def go_to_category(self):
        """카테고리 화면으로 이동"""
        try:
            category_btn = self.driver.find_element(AppiumBy.ID, "com.coupang.mobile:id/category_button")
            category_btn.click()
        except Exception as e:
            print(f"카테고리 화면 이동 중 에러: {str(e)}")
            raise

if __name__ == "__main__":
    try:
        checker = WebViewChecker()
        checker.check_webview_in_screens()
    except Exception as e:
        print(f"프로그램 실행 중 에러 발생: {str(e)}") 