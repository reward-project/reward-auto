from mobile_automation import MobileAutomation
import time

class UIInspector(MobileAutomation):
    def inspect_elements(self):
        """UI 요소 검사"""
        try:
            # 앱이 로드될 때까지 대기
            time.sleep(5)
            
            # 현재 화면의 모든 요소 가져오기
            elements = self.driver.find_elements(AppiumBy.XPATH, "//*")
            
            print("\n=== UI 요소 목록 ===")
            for element in elements:
                try:
                    # 요소의 클래스명
                    class_name = element.get_attribute("className")
                    # 요소의 리소스 ID
                    resource_id = element.get_attribute("resourceId")
                    # 요소의 텍스트
                    text = element.get_attribute("text")
                    
                    print(f"\n요소 정보:")
                    print(f"클래스: {class_name}")
                    print(f"리소스 ID: {resource_id}")
                    print(f"텍스트: {text}")
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"검사 중 에러 발생: {str(e)}")

if __name__ == "__main__":
    inspector = UIInspector()
    inspector.inspect_elements() 