from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.logger import Logger
import time

class PaginationHandler:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)
        self.logger = Logger('PaginationHandler')
        
    def get_current_page(self):
        """현재 페이지 번호 가져오기"""
        try:
            current = self.driver.find_element(
                By.CSS_SELECTOR, 
                "#pagination .page.selected"
            )
            return int(current.get_attribute('data-page'))
        except Exception as e:
            self.logger.error(f"현재 페이지 확인 실패: {str(e)}")
            return None
            
    def get_total_count(self):
        """전체 상품 수 가져오기"""
        try:
            pagination = self.driver.find_element(By.ID, "pagination")
            return int(pagination.get_attribute('count'))
        except Exception as e:
            self.logger.error(f"���체 상품 수 확인 실패: {str(e)}")
            return None
            
    def go_to_next_page(self):
        """다음 페이지로 이동"""
        try:
            # 다음 페이지 버튼 찾기
            next_button = self.driver.find_element(
                By.CSS_SELECTOR,
                "#pagination .page.next:not(.dim)"
            )
            
            if next_button:
                self.logger.info("다음 페이지로 이동")
                next_button.click()
                time.sleep(3)  # 페이지 로딩 대기
                
                # 페이지 이동 확인
                current_page = self.get_current_page()
                self.logger.info(f"현재 페이지: {current_page}")
                return True
                
            else:
                self.logger.info("마지막 페이지입니다")
                return False
                
        except Exception as e:
            self.logger.error(f"페이지 이동 실패: {str(e)}")
            return False
            
    def has_next_page(self):
        """다음 페이지 존재 여부 확인"""
        try:
            next_button = self.driver.find_element(
                By.CSS_SELECTOR,
                "#pagination .page.next"
            )
            return 'dim' not in next_button.get_attribute('class')
        except:
            return False 