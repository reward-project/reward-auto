from mobile_automation import MobileAutomation
import time

class CoupangWebViewTest(MobileAutomation):
    def switch_to_webview(self):
        """웹뷰로 전환"""
        # 웹뷰가 로드될 때까지 대기
        time.sleep(3)
        # 사용 가능한 컨텍스트 확인
        contexts = self.driver.contexts
        print(f"사용 가능한 컨텍스트: {contexts}")
        
        # WEBVIEW로 시작하는 컨텍스트를 찾아 전환
        for context in contexts:
            if 'WEBVIEW' in context:
                self.driver.switch_to.context(context)
                print(f"전환된 컨텍스트: {context}")
                return True
        return False

    def switch_to_native(self):
        """네이티브 앱으로 전환"""
        self.driver.switch_to.context('NATIVE_APP')
        
    def test_hybrid_interaction(self):
        try:
            # 네이티브 요소 클릭 (예: 검색 버튼)
            self.find_and_click_element("search_button")
            
            # 웹뷰로 전환
            if self.switch_to_webview():
                # 웹뷰 내의 요소 찾기 (Selenium 방식)
                search_input = self.driver.find_element('name', 'q')
                search_input.send_keys("노트북")
                
                # 필요한 경우 다시 네이티브로 전환
                self.switch_to_native()
            
        except Exception as e:
            print(f"테스트 중 에러 발생: {str(e)}")
            return False
        
        return True

# 테스트 실행
if __name__ == "__main__":
    test = CoupangWebViewTest()
    test.test_hybrid_interaction()