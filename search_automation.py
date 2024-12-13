from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.logger import Logger
from browser_initializer import BrowserInitializer
from popup_handler import PopupHandler
import time
import os
from urllib.parse import quote

class CoupangSearchAutomation:
    def __init__(self):
        self.logger = Logger('CoupangSearchAutomation')
        self.logger.info("=== 쿠팡 검색 자동화 시작 ===")
        
        # 브라우저 초기화
        browser_initializer = BrowserInitializer()
        self.driver = browser_initializer.initialize_browser()
        
        # 팝업 핸들러 초기화
        self.popup_handler = PopupHandler(self.driver)
        
        self.wait = WebDriverWait(self.driver, 10)
        self.base_url = "https://m.coupang.com"
        
        # 스크린샷 저장 디렉토리
        self.screenshot_dir = os.path.join('logs', 'screenshots')
        os.makedirs(self.screenshot_dir, exist_ok=True)

    def search_product(self, keyword):
        """상품 검색"""
        try:
            self.logger.info(f"\n=== 상품 검색 시작: {keyword} ===")
            
            # 쿠팡 모바일 웹 접속
            self.driver.get(self.base_url)
            self.logger.debug("쿠팡 모바일 웹 페이지 로드")
            time.sleep(5)
            
            # 팝업 처리
            self.popup_handler.close_all_popups()
            
            try:
                # JavaScript로 요소 확인
                self.logger.debug("페이�� 상태 확인")
                is_ready = self.driver.execute_script("return document.readyState") == "complete"
                self.logger.debug(f"페이지 로드 상태: {is_ready}")
                
                # searchBtn 요소 확인
                search_btn_visible = self.driver.execute_script(
                    "return document.getElementById('searchBtn') !== null && "
                    "document.getElementById('searchBtn').offsetParent !== null"
                )
                self.logger.debug(f"검색 버튼 표시 상태: {search_btn_visible}")
                
                # JavaScript로 클릭 시도
                self.logger.debug("JavaScript로 검색 버튼 클릭 시도")
                self.driver.execute_script(
                    "document.getElementById('searchBtn').click();"
                )
                time.sleep(2)
                
                # 검색창 표시 확인
                search_input_visible = self.driver.execute_script(
                    "return document.getElementById('q') !== null && "
                    "document.getElementById('q').offsetParent !== null"
                )
                self.logger.debug(f"검색창 표시 상태: {search_input_visible}")
                
                # JavaScript로 검색어 입력
                self.logger.debug(f"JavaScript로 검색어 입력: {keyword}")
                self.driver.execute_script(
                    f"document.getElementById('q').value = '{keyword}';"
                )
                time.sleep(1)
                
                # 폼 제출
                self.logger.debug("검색 폼 제출")
                self.driver.execute_script(
                    "document.getElementById('q').form.submit();"
                )
                time.sleep(3)
                
                return True
                
            except Exception as e:
                self.logger.error(f"검색 실패: {str(e)}")
                self.save_screenshot('search_error.png')
                return False
                
        except Exception as e:
            self.logger.error(f"검색 중 에러: {str(e)}")
            self.save_screenshot('search_error.png')
            return False

    def search_product_by_url(self, keyword):
        """URL로 직접 검색"""
        try:
            self.logger.info(f"\n=== URL 검색 시작: {keyword} ===")
            
            # 검색 URL 생성 (한글 인코딩 처리)
            encoded_keyword = quote(keyword)
            search_url = f"https://m.coupang.com/nm/search?q={encoded_keyword}"
            
            self.logger.debug(f"검색 URL: {search_url}")
            
            # 검색 페이지로 직접 이동
            self.driver.get(search_url)
            self.logger.debug("검색 페이지 로드")
            time.sleep(5)
            
            # 팝업 처리
            self.popup_handler.close_all_popups()
            
            # 검색 결과 확인
            try:
                # 상품 목록 확인
                product_list = self.wait.until(
                    EC.presence_of_element_located((By.ID, "productList"))
                )
                self.logger.debug("검색 결과 로드 완료")
                
                # 현재 URL 확인
                current_url = self.driver.current_url
                self.logger.debug(f"현재 URL: {current_url}")
                
                if "search" in current_url and "q=" in current_url:
                    self.logger.info("검색 성공")
                    return True
                else:
                    self.logger.error("검색 페이지가 아님")
                    return False
                    
            except Exception as e:
                self.logger.error(f"검색 결과 확인 실패: {str(e)}")
                self.save_screenshot('search_error.png')
                return False
                
        except Exception as e:
            self.logger.error(f"URL 검색 중 에러: {str(e)}")
            self.save_screenshot('search_error.png')
            return False

    def save_screenshot(self, filename):
        """스크린샷 저장"""
        try:
            filepath = os.path.join(self.screenshot_dir, filename)
            self.driver.save_screenshot(filepath)
            self.logger.debug(f"스크린샷 저장됨: {filepath}")
        except Exception as e:
            self.logger.error(f"스크린샷 저장 실패: {str(e)}")

    def get_driver(self):
        """WebDriver 반환"""
        return self.driver

    def close(self):
        """브라우저 종료"""
        try:
            self.driver.quit()
            self.logger.info("브라우저 종료")
        except Exception as e:
            self.logger.error(f"브라우저 종료 중 에러: {str(e)}") 