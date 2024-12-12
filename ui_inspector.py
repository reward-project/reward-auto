from mobile_automation import MobileAutomation
from appium.webdriver.common.appiumby import AppiumBy
import time
import os

class UIInspector(MobileAutomation):
    def inspect_elements(self):
        """UI 요소 검사"""
        try:
            # 앱이 로드될 때까지 대기
            time.sleep(5)
            
            # 결과를 저장할 디렉토리 생성
            os.makedirs('logs', exist_ok=True)
            
            with open('logs/ui_elements.log', 'w', encoding='utf-8') as f:
                # WebView 특정 검색
                webviews = self.driver.find_elements(AppiumBy.CLASS_NAME, "android.webkit.WebView")
                f.write("=== WebView 검색 결과 ===\n")
                f.write(f"발견된 WebView 수: {len(webviews)}\n\n")
                
                # 일반 요소 검색
                f.write("=== 모든 UI 요소 ===\n")
                elements = self.driver.find_elements(AppiumBy.XPATH, "//*")
                for element in elements:
                    try:
                        class_name = element.get_attribute("className")
                        resource_id = element.get_attribute("resourceId")
                        text = element.get_attribute("text")
                        content_desc = element.get_attribute("contentDescription")
                        
                        f.write("\n요소 정보:\n")
                        f.write(f"클래스: {class_name}\n")
                        f.write(f"리소스 ID: {resource_id}\n")
                        f.write(f"텍스트: {text}\n")
                        f.write(f"설명: {content_desc}\n")
                    except Exception as e:
                        continue
                    
        except Exception as e:
            with open('logs/error.log', 'w', encoding='utf-8') as f:
                f.write(f"UI 검사 중 에러 발생: {str(e)}")

    def inspect_multiple_screens(self):
        """여러 화면의 요소 검사"""
        try:
            screens = [
                {'name': '메인화면', 'action': None},
                {'name': '검색화면', 'action': lambda: self.find_and_click_element("search_button")},
                {'name': '카테고리', 'action': lambda: self.find_and_click_element("category_button")}
            ]
            
            for screen in screens:
                if screen['action']:
                    screen['action']()
                time.sleep(3)
                
                with open(f"logs/ui_{screen['name']}.log", 'w', encoding='utf-8') as f:
                    webviews = self.driver.find_elements(AppiumBy.CLASS_NAME, "android.webkit.WebView")
                    f.write(f"=== {screen['name']} WebView 검색 결과 ===\n")
                    f.write(f"발견된 WebView 수: {len(webviews)}\n\n")
                    
                    elements = self.driver.find_elements(AppiumBy.XPATH, "//*")
                    f.write(f"=== {screen['name']} 모든 UI 요소 ===\n")
                    # ... 요소 정보 저장 ...
                    
        except Exception as e:
            with open('logs/error.log', 'w', encoding='utf-8') as f:
                f.write(f"화면 검사 중 에러 발생: {str(e)}")

if __name__ == "__main__":
    try:
        inspector = UIInspector()
        inspector.inspect_elements()
    except Exception as e:
        with open('logs/error.log', 'a', encoding='utf-8') as f:
            f.write(f"\n프로그램 실행 중 에러 발생: {str(e)}") 