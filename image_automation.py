from mobile_automation import MobileAutomation
import cv2
import numpy as np

class ImageBasedAutomation(MobileAutomation):
    def find_and_click_image(self, template_path, threshold=0.8):
        """이미지로 요소를 찾아 클릭"""
        # 화면 캡처
        screenshot = self.driver.get_screenshot_as_png()
        screen = cv2.imdecode(np.frombuffer(screenshot, np.uint8), cv2.IMREAD_COLOR)
        
        # 찾을 이미지 템플릿
        template = cv2.imread(template_path)
        
        # 이미지 매칭
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= threshold:
            # 찾은 위치 중앙점 계산
            h, w = template.shape[:2]
            center_x = max_loc[0] + w//2
            center_y = max_loc[1] + h//2
            
            # 클릭
            self.driver.tap([(center_x, center_y)])
            return True
        return False 