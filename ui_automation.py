from mobile_automation import MobileAutomation
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class CoupangUIAutomation(MobileAutomation):
    def find_by_content_desc(self, desc):
        """content-desc로 요소 찾기"""
        try:
            element = self.driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR,
                f'new UiSelector().description("{desc}")'
            )
            return element
        except:
            return None

    def find_by_resource_id(self, resource_id):
        """resource-id로 요소 찾기"""
        try:
            element = self.driver.find_element(AppiumBy.ID, resource_id)
            return element
        except:
            return None

    def wait_and_click(self, locator, locator_type=AppiumBy.ID, timeout=10):
        """요소가 나타날 때까지 기다렸다가 클릭"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((locator_type, locator))
            )
            element.click()
            return True
        except:
            return False 