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
            # URL에서 페이지 번호 추출 시도
            current_url = self.driver.current_url
            if 'page=' in current_url:
                page_param = current_url.split('page=')[1].split('&')[0]
                return int(page_param)
            
            # URL에 페이지 정보가 없으면 1페이지로 간주
            return 1
            
        except Exception as e:
            self.logger.error(f"현재 페이지 확인 실패: {str(e)}")
            return 1  # 기본값으로 1 반환
            
    def get_total_count(self):
        """전체 상품 수 가져오기"""
        try:
            pagination = self.driver.find_element(By.ID, "pagination")
            return int(pagination.get_attribute('count'))
        except Exception as e:
            self.logger.error(f"전체 상품 수 확인 실패: {str(e)}")
            return None
            
    def go_to_next_page(self):
        """다음 페이지로 이동"""
        try:
            # 현재 URL 가져오기
            current_url = self.driver.current_url
            
            # 현재 페이지 번호 확인
            current_page = self.get_current_page() or 1
            next_page = current_page + 1
            
            # URL에서 페이지 파라미터 변경 또는 추가
            if 'page=' in current_url:
                new_url = current_url.replace(f'page={current_page}', f'page={next_page}')
            else:
                separator = '&' if '?' in current_url else '?'
                new_url = f"{current_url}{separator}page={next_page}"
            
            # 새 URL로 이동
            self.driver.get(new_url)
            time.sleep(2)  # 페이지 로딩 대기
            
            return True
            
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