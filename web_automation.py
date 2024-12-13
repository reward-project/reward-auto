from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from utils.logger import Logger
import time
import os

class CoupangWebAutomation:
    def __init__(self):
        self.logger = Logger('CoupangWebAutomation')
        self.logger.info("=== 쿠팡 웹 자동화 시작 ===")
        
        # 모바일 에뮬레이션 설정
        chrome_options = Options()
        chrome_options.add_argument('--window-size=412,915')  # Galaxy S20 Ultra 해상도
        chrome_options.add_experimental_option("mobileEmulation", {
            "deviceMetrics": { "width": 412, "height": 915, "pixelRatio": 3.0 },
            "userAgent": "Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36"
        })
        
        self.driver = webdriver.Chrome(options=chrome_options)
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
            time.sleep(2)
            
            # 검색창 찾기
            search_box = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='search']"))
            )
            self.logger.debug("검색창 발견")
            
            # 검색어 입력
            search_box.clear()
            search_box.send_keys(keyword)
            self.logger.debug(f"검색어 입력: {keyword}")
            
            # 검색 버튼 클릭
            search_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
            )
            search_button.click()
            self.logger.info("검색 실행")
            
            # 검색 결과 로딩 대기
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".search-product"))
            )
            self.logger.debug("검색 결과 로드 완료")
            
            return True
            
        except Exception as e:
            self.logger.error(f"검색 중 에러: {str(e)}")
            self.save_screenshot('search_error.png')
            return False

    def find_product_by_conditions(self, name, price_range=None, rating=None):
        """조건에 맞는 상품 찾기"""
        try:
            self.logger.info(f"상품 검색 - 이름: {name}, 가격: {price_range}, 평점: {rating}")
            max_scroll = 5
            scroll_count = 0
            
            while scroll_count < max_scroll:
                # 현재 페이지의 상품들 확인
                products = self.driver.find_elements(By.CSS_SELECTOR, ".search-product")
                self.logger.debug(f"현재 페이지 상품 수: {len(products)}")
                
                for product in products:
                    try:
                        # 상품명 확인
                        product_name = product.find_element(By.CSS_SELECTOR, ".name").text
                        if name.lower() not in product_name.lower():
                            continue
                            
                        # 가격 확인
                        if price_range:
                            price_text = product.find_element(By.CSS_SELECTOR, ".price").text
                            price = int(''.join(filter(str.isdigit, price_text)))
                            if not (price_range[0] <= price <= price_range[1]):
                                continue
                        
                        # 평점 확인
                        if rating:
                            try:
                                rating_text = product.find_element(By.CSS_SELECTOR, ".rating").text
                                current_rating = float(rating_text.split()[0])
                                if current_rating < rating:
                                    continue
                            except NoSuchElementException:
                                continue
                        
                        # 조건 만족하는 상품 발견
                        self.logger.info(f"조건에 맞는 상품 발견: {product_name}")
                        product.click()
                        return True
                        
                    except Exception as e:
                        self.logger.debug(f"상품 분석 중 에러: {str(e)}")
                        continue
                
                # 다음 페이지로 스크롤
                self.scroll_down()
                scroll_count += 1
                time.sleep(2)
            
            self.logger.warning("조건에 맞는 상품을 찾지 못함")
            return False
            
        except Exception as e:
            self.logger.error(f"상품 검색 중 에러: {str(e)}")
            self.save_screenshot('search_error.png')
            return False

    def scroll_down(self):
        """페이지 스크롤"""
        try:
            # 현재 스크롤 위치 저장
            last_height = self.driver.execute_script("return window.pageYOffset")
            
            # 스크롤 다운
            self.driver.execute_script("window.scrollTo(0, window.pageYOffset + window.innerHeight);")
            time.sleep(1)
            
            # 새로운 스크롤 위치
            new_height = self.driver.execute_script("return window.pageYOffset")
            
            # 스크롤이 더 이상 되지 않으면 False 반환
            return new_height > last_height
            
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