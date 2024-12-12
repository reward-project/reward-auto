from mobile_automation import MobileAutomation
from appium.webdriver.common.appiumby import AppiumBy
import time
import os

class ContextChecker(MobileAutomation):
    def check_contexts(self):
        """사용 가능한 모든 컨텍스트 확인"""
        try:
            # 앱이 완전히 로드될 때까지 대기
            time.sleep(5)
            
            # 결과를 저장할 디렉토리 생성
            os.makedirs('logs', exist_ok=True)
            
            # 결과를 파일로 저장
            with open('logs/context_check.log', 'w', encoding='utf-8') as f:
                # WebView 검색
                webviews = self.driver.find_elements(AppiumBy.CLASS_NAME, "android.webkit.WebView")
                f.write("=== WebView 검색 결과 ===\n")
                f.write(f"발견된 WebView 수: {len(webviews)}\n")
                
                for idx, webview in enumerate(webviews, 1):
                    f.write(f"\nWebView #{idx} 정보:\n")
                    try:
                        resource_id = webview.get_attribute("resourceId")
                        content_desc = webview.get_attribute("contentDescription")
                        f.write(f"리소스 ID: {resource_id}\n")
                        f.write(f"설명: {content_desc}\n")
                    except Exception as e:
                        f.write(f"WebView 정보 추출 실패: {str(e)}\n")
                
                f.write("\n=== 컨텍스트 정보 ===\n")
                # 현재 사용 가능한 모든 컨텍스트 저장
                contexts = self.driver.contexts
                f.write(f"사용 가능한 컨텍스트: {contexts}\n")
                
                # 현재 활성화된 컨텍스트 저장
                current = self.driver.current_context
                f.write(f"현재 컨텍스트: {current}\n")
                
                # 페이지 소스 저장
                f.write("\n=== 페이지 소스 ===\n")
                f.write(self.driver.page_source)
            
        except Exception as e:
            with open('logs/error.log', 'w', encoding='utf-8') as f:
                f.write(f"컨텍스트 확인 중 에러 발생: {str(e)}")
            raise

if __name__ == "__main__":
    try:
        checker = ContextChecker()
        checker.check_contexts()
    except Exception as e:
        with open('logs/error.log', 'a', encoding='utf-8') as f:
            f.write(f"\n프로그램 실행 중 에러 발생: {str(e)}") 