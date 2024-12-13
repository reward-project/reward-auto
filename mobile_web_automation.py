from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.logger import Logger
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
from selenium.webdriver.common.keys import Keys

class CoupangMobileWebAutomation:
    def __init__(self):
        self.logger = Logger('CoupangMobileWebAutomation')
        self.logger.info("=== 쿠팡 모바일 웹 자동화 시작 ===")
        
        # ChromeDriver 자동 다운로드
        chromedriver_path = ChromeDriverManager().install()
        self.logger.debug(f"ChromeDriver 경로: {chromedriver_path}")
        
        # Appium 설정
        options = UiAutomator2Options()
        options.set_capability('platformName', 'Android')
        options.set_capability('deviceName', 'emulator-5554')
        options.set_capability('automationName', 'UiAutomator2')
        options.set_capability('browserName', 'Chrome')
        options.set_capability('noReset', True)
        
        # 크롬 옵션 설정
        options.set_capability('chromedriverExecutable', chromedriver_path)
        
        # 추가 크롬 설정
        options.set_capability('chromeOptions', {
            'w3c': False,
            'args': ['--no-sandbox', '--disable-dev-shm-usage']
        })
        
        self.driver = webdriver.Remote('http://127.0.0.1:4723', options=options)
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
            self.close_popup()
            
            try:
                # JavaScript로 요소 확인
                self.logger.debug("페이지 상태 확인")
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

    def try_click_search_button(self):
        """검색 버튼 클릭 시도"""
        search_button_selectors = [
            (By.CSS_SELECTOR, "button[type='submit']"),
            (By.CSS_SELECTOR, ".btn-search"),
            (By.CSS_SELECTOR, "button.search"),
            (By.XPATH, "//button[@type='submit']"),
            (By.XPATH, "//button[contains(@class, 'search')]")
        ]
        
        for selector_type, selector in search_button_selectors:
            try:
                button = self.wait.until(
                    EC.element_to_be_clickable((selector_type, selector))
                )
                button.click()
                return True
            except:
                continue
        return False

    def check_search_results(self):
        """검색 결과 확인"""
        result_selectors = [
            (By.CSS_SELECTOR, ".search-product-list"),
            (By.CSS_SELECTOR, ".search-results"),
            (By.CSS_SELECTOR, ".product-list"),
            (By.XPATH, "//div[contains(@class, 'search')]//ul")
        ]
        
        for selector_type, selector in result_selectors:
            try:
                self.wait.until(
                    EC.presence_of_element_located((selector_type, selector))
                )
                return True
            except:
                continue
        return False

    def find_product_by_conditions(self, productId):
        """상품 ID로 상품 찾기"""
        try:
            self.logger.info(f"상품 검색 - ID: {productId}")
            max_scroll = 5
            scroll_count = 0
            
            while scroll_count < max_scroll:
                # 팝업 처리
                self.close_popup()
                
                # 상품 링크 찾기 (직접 href로 검색)
                try:
                    # 정확한 상품 ID를 포함하는 링크 찾기
                    product_link = self.driver.find_element(
                        By.CSS_SELECTOR, 
                        f'a[href*="/products/{productId}"], a[href*="/vp/products/{productId}"]'
                    )
                    
                    self.logger.info(f"=== 상품 ID 일치: {productId} ===")
                    self.logger.info(f"URL: {product_link.get_attribute('href')}")
                    
                    # 클릭 시도
                    try:
                        product_link.click()
                    except:
                        self.driver.execute_script("arguments[0].click();", product_link)
                    
                    return True
                    
                except Exception as e:
                    self.logger.debug(f"현재 페이지에서 상품을 찾지 못함: {str(e)}")
                
                # 다음 페이지로 스크롤
                self.scroll_down()
                scroll_count += 1
                time.sleep(2)
            
            self.logger.warning("상품을 찾지 못함")
            return False
            
        except Exception as e:
            self.logger.error(f"상품 검색 중 에러: {str(e)}")
            self.save_screenshot('search_error.png')
            return False

    def scroll_down(self):
        """페이지 스크롤"""
        try:
            # 화면 크기 가져오기
            screen_size = self.driver.get_window_size()
            start_y = screen_size['height'] * 0.8
            end_y = screen_size['height'] * 0.2
            
            # 스크롤
            self.driver.swipe(
                screen_size['width'] // 2,
                start_y,
                screen_size['width'] // 2,
                end_y,
                duration=1000
            )
            time.sleep(1)
            return True
            
        except Exception as e:
            self.logger.error(f"스크롤 중 에러: {str(e)}")
            return False

    def save_screenshot(self, filename):
        """스크린샷 저장"""
        try:
            filepath = os.path.join(self.screenshot_dir, filename)
            self.driver.save_screenshot(filepath)
            self.logger.debug(f"스크린샷 저장됨: {filepath}")
        except Exception as e:
            self.logger.error(f"스크린샷 저장 실패: {str(e)}")

    def close(self):
        """브라우저 종료"""
        try:
            self.driver.quit()
            self.logger.info("브라우저 종료")
        except Exception as e:
            self.logger.error(f"브라우저 종료 중 에러: {str(e)}")

    def close_popup(self):
        """팝업과 배너 닫기"""
        try:
            # 팝업 닫기 버튼 확인 및 처리
            popup_visible = self.driver.execute_script("""
                const closeBtn = document.querySelector("#bottomSheetBudgeCloseButton");
                return closeBtn && closeBtn.offsetParent !== null;
            """)
            
            if popup_visible:
                self.logger.debug("팝업 발견, 닫기 시도")
                self.driver.execute_script("""
                    document.querySelector("#bottomSheetBudgeCloseButton").click();
                """)
                time.sleep(1)
            
            # 하단 앱 배너 확인 및 처리
            banner_visible = self.driver.execute_script("""
                const banner = document.querySelector("#BottomAppBanner > div > div > a");
                return banner && banner.offsetParent !== null;
            """)
            
            if banner_visible:
                self.logger.debug("하단 앱 배너 발견, 닫기 시도")
                self.driver.execute_script("""
                    const banner = document.querySelector("#BottomAppBanner > div > div > a");
                    if (banner) {
                        // 배너의 닫기 버튼 찾기 시도
                        const closeBtn = banner.querySelector('.close') || 
                                       banner.parentElement.querySelector('.close');
                        if (closeBtn) {
                            closeBtn.click();
                        } else {
                            // 닫기 버튼이 없으면 배너 자체를 숨김
                            banner.closest('#BottomAppBanner').style.display = 'none';
                        }
                    }
                """)
                time.sleep(1)
            
            return True
            
        except Exception as e:
            self.logger.debug(f"팝업/배너 처리 중 에러: {str(e)}")
            return False 