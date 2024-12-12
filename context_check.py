from mobile_automation import MobileAutomation
import time

class ContextChecker(MobileAutomation):
    def check_contexts(self):
        """사용 가능한 모든 컨텍스트 확인"""
        # 앱이 완전히 로드될 때까지 대기
        time.sleep(5)
        
        # 현재 사용 가능한 모든 컨텍스트 출력
        contexts = self.driver.contexts
        print("사용 가능한 컨텍스트:", contexts)
        
        # 현재 활성화된 컨텍스트 출력
        current = self.driver.current_context
        print("현재 컨텍스트:", current)
        
        # 페이지 소스 출력 (구조 확인)
        print("\n페이지 소스:")
        print(self.driver.page_source)

if __name__ == "__main__":
    checker = ContextChecker()
    checker.check_contexts() 