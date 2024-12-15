from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.logger import Logger
from popup_handler import PopupHandler
from pagination_handler import PaginationHandler
from ad_checker import AdChecker
import time
import random
import pandas as pd

class CoupangProductFinder:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)
        self.logger = Logger('CoupangProductFinder')
        self.popup_handler = PopupHandler(self.driver)
        self.pagination_handler = PaginationHandler(self.driver)
        self.ad_checker = AdChecker()
        
    def extract_product_id(self, href):
        """URL에서 상품 ID와 itemId 추출"""
        try:
            product_id = None
            item_id = None
            
            # 기본 상품 ID 추출
            if '/products/' in href:
                parts = href.split('/products/')[-1].split('?')
                if parts:
                    product_id = parts[0]
            elif '/vp/products/' in href:
                parts = href.split('/vp/products/')[-1].split('?')
                if parts:
                    product_id = parts[0]
            
            # itemId 추출
            if 'itemId=' in href:
                item_id = href.split('itemId=')[-1].split('&')[0]
            
            return product_id, item_id
        except:
            return None, None

    def find_product_by_id(self, target_product_id, product_name=None, is_ad=False):
        """상품 ID로 상품 찾기"""
        try:
            # target_product_id가 float인 경우 문자열로 변환
            target_product_id = str(target_product_id).split('.')[0]  # float 부분 제거
            self.logger.info(f"상품 검색 시작 - ID: {target_product_id}, 광고: {is_ad}")
            
            while True:  # 모든 페이지 검색
                self.popup_handler.close_all_popups()
                
                # 현재 페이지에서 상품 찾기
                product_containers = self.driver.find_elements(By.CSS_SELECTOR, '#productList li')
                self.logger.info(f"현재 페이지 상품 수: {len(product_containers)}")
                
                # 페이지 스크롤 전에 먼저 현재 보이는 상품들 확인
                for container in product_containers:
                    try:
                        if self._check_and_click_product(container, target_product_id, is_ad):
                            return True
                    except Exception as e:
                        continue
                
                # 페이지 스크롤하면서 추가 상품 확인
                total_height = self.driver.execute_script("return document.body.scrollHeight")
                scroll_step = 300  # 한 번에 스크롤할 높이
                
                for scroll_pos in range(0, total_height, scroll_step):
                    # 스크롤 수행
                    self.driver.execute_script(f"window.scrollTo(0, {scroll_pos})")
                    time.sleep(0.3)  # 스크롤 후 잠시 대기
                    
                    # 새로 보이는 상품들 확인
                    visible_products = self.driver.find_elements(By.CSS_SELECTOR, '#productList li')
                    for container in visible_products:
                        try:
                            if self._check_and_click_product(container, target_product_id, is_ad):
                                return True
                        except Exception as e:
                            continue
                
                # 상품을 찾지 못한 경우 다음 페이지로 이동
                if not self.pagination_handler.has_next_page():
                    self.logger.info("마지막 페이지 도달")
                    break
                
                if not self.pagination_handler.go_to_next_page():
                    self.logger.error("페이지 이동 실패")
                    break
                
                time.sleep(0.5)
            
            self.logger.warning("상품을 찾지 못했습니다.")
            return False
            
        except Exception as e:
            self.logger.error(f"상품 검색 중 오류: {str(e)}")
            return False

    def _check_and_click_product(self, container, target_product_id, is_ad):
        """상품 확인 및 클릭 처리"""
        try:
            # 광고 여부 확인
            is_ad_product = 'search-product-ad' in container.get_attribute('class')
            if is_ad != is_ad_product:
                return False
            
            # 링크 찾기
            link = container.find_element(By.CSS_SELECTOR, 'a[href*="/products/"]')
            product_url = link.get_attribute('href')
            
            # ID 확인
            if target_product_id in product_url:
                self.logger.info(f"상품 발견! URL: {product_url}")
                
                try:
                    # 방해 요소 제거
                    self.driver.execute_script("""
                        var elements = document.getElementsByClassName('service-shortcut-row-toggle');
                        for(var i=0; i<elements.length; i++) {
                            elements[i].style.display = 'none';
                        }
                    """)
                    
                    # 상품 위치로 스크롤
                    container_location = container.location['y']
                    self.driver.execute_script(f"window.scrollTo({{top: {container_location - 100}, behavior: 'smooth'}})")
                    time.sleep(0.5)
                    
                    # 클릭
                    try:
                        link.click()
                    except:
                        self.driver.execute_script("arguments[0].click();", link)
                    
                    time.sleep(0.5)
                    if self.check_detail_page(target_product_id):
                        return True
                except:
                    pass
            
            return False
        except Exception as e:
            self.logger.error(f"상품 확인 중 오류: {str(e)}")
            return False

    def find_product_in_current_page(self, productId):
        try:
            max_scroll = 5
            scroll_count = 0
            
            while scroll_count < max_scroll:
                self.popup_handler.close_all_popups()
                
                product_containers = self.driver.find_elements(By.CSS_SELECTOR, '#productList li')
                
                # 현재 페이지의 모든 상품 광고 여부 체크
                check_result = self.ad_checker.check_page_products(product_containers, productId)
                
                # 일반 상품이 발견된 경우 클릭 진행
                if check_result['target_product']:
                    try:
                        container = check_result['target_product']
                        
                        # 링크 찾기
                        link = container.find_element(By.CSS_SELECTOR, 'a[href*="/products/"]')
                        
                        # 방해되는 요소 제거
                        self.driver.execute_script("""
                            var elements = document.getElementsByClassName('service-shortcut-row-toggle');
                            for(var i=0; i<elements.length; i++) {
                                elements[i].style.display = 'none';
                            }
                        """)
                        
                        # 컨테이너의 Y 위치 가져오기
                        container_location = container.location['y']
                        
                        # 컨테이너 위치로 스크롤
                        self.driver.execute_script(f"window.scrollTo(0, {container_location - 100});")
                        time.sleep(1)
                        
                        # 클릭 가능할 때까지 대기
                        wait = WebDriverWait(self.driver, 10)
                        clickable = wait.until(EC.element_to_be_clickable(link))
                        
                        # 클릭 실행
                        clickable.click()
                        time.sleep(3)
                        
                        # 이동 후 URL 확인 및 로깅
                        final_url = self.driver.current_url
                        self.logger.info(f"\n=== 상품 상세 페이지 이동 완료 ===")
                        self.logger.info(f"최종 URL: {final_url}")
                        
                        return True
                        
                    except Exception as e:
                        self.logger.error(f"상품 클릭 중 에러: {str(e)}")
                        return False
                
                # 스크롤 처리
                before_height = self.driver.execute_script("return document.documentElement.scrollHeight")
                self.driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
                time.sleep(2)
                after_height = self.driver.execute_script("return document.documentElement.scrollHeight")
                
                if after_height == before_height:
                    break
                
                scroll_count += 1
            
            return False
            
        except Exception as e:
            self.logger.error(f"품 검색 중 에러: {str(e)}")
            return False

    def scroll_down(self):
        """페이지 스크롤"""
        try:
            # 현재 스크롤 위치
            before_scroll = self.driver.execute_script("return window.pageYOffset;")
            
            # 스크롤 실행
            self.driver.execute_script(
                "window.scrollTo(0, window.pageYOffset + window.innerHeight);"
            )
            time.sleep(1)
            
            # 스크롤 후 위치
            after_scroll = self.driver.execute_script("return window.pageYOffset;")
            
            # 스크롤 성공 여부 반환
            return after_scroll > before_scroll
            
        except Exception as e:
            self.logger.error(f"스크롤 실행 에러: {str(e)}")
            return False 

    def extract_product_info(self, href):
        """URL에서 모든 상품 관련 정보 추출"""
        try:
            info = {
                'product_id': None,
                'item_id': None,
                'vendor_item_id': None,
                'search_id': None,
                'source_type': None,
                'search_keyword': None
            }
            
            # 기본 상품 ID 추출
            if '/products/' in href:
                parts = href.split('/products/')[-1].split('?')
                if parts:
                    info['product_id'] = parts[0]
            
            # 쿼리 파미터 파싱
            if '?' in href:
                query_string = href.split('?')[1]
                params = query_string.split('&')
                
                for param in params:
                    if '=' in param:
                        key, value = param.split('=')
                        if key == 'itemId':
                            info['item_id'] = value
                        elif key == 'vendorItemId':
                            info['vendor_item_id'] = value
                        elif key == 'searchId':
                            info['search_id'] = value
                        elif key == 'sourceType':
                            info['source_type'] = value
                        elif key == 'q':
                            from urllib.parse import unquote
                            info['search_keyword'] = unquote(value)
            
            return info
        except:
            return None 

    def check_detail_page(self, target_product_id):
        """상품 상세 페이지 확인"""
        try:
            time.sleep(1)  # 초기 로딩 대기
            
            # 현재 URL에서 상품 ID 확인
            current_url = self.driver.current_url
            self.logger.info(f"상세 페이지 URL: {current_url}")
            
            # 상품 ID 확인
            if target_product_id in current_url:
                try:
                    total_height = self.driver.execute_script("return document.body.scrollHeight")
                    current_height = 0
                    
                    # 스크롤 설정
                    if scroll_speed == 'H':
                        scroll_step = random.randint(200, 300)
                        scroll_delay = random.uniform(0.8, 1.2)
                        pause_chance = 0.2
                    else:
                        scroll_step = random.randint(400, 500)
                        scroll_delay = random.uniform(0.4, 0.6)
                        pause_chance = 0.1
                    
                    while current_height < total_height:
                        next_height = min(current_height + scroll_step, total_height)
                        
                        # 부드러운 스크롤
                        self.driver.execute_script(f"""
                            window.scrollTo({{
                                top: {next_height},
                                behavior: 'smooth'
                            }});
                        """)
                        
                        time.sleep(scroll_delay)
                        
                        if random.random() < pause_chance:
                            time.sleep(random.uniform(0.5, 1.0))
                        
                        current_height = next_height
                    
                    # 리뷰 섹션 찾기
                    review_selectors = [
                        'div.sdp-review__article',
                        'div.product-review',
                        'div.js_reviewArticleContainer',
                        '#btfTab > ul.product-tab-list > li.product-review-tab'
                    ]
                    
                    for selector in review_selectors:
                        try:
                            review_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                            self.logger.info(f"리뷰/상품평 섹션 발견: {selector}")
                            
                            # 리뷰 섹션으로 스크롤
                            self.driver.execute_script("arguments[0].scrollIntoView();", review_element)
                            time.sleep(0.2)
                            
                            # 상품평 탭인 경우 클릭
                            if 'product-review-tab' in selector:
                                review_element.click()
                                time.sleep(0.2)
                            
                            break
                        except:
                            continue
                    
                    # 최종 체류 시간
                    time.sleep(0.5)
                    return True
                    
                except Exception as scroll_error:
                    self.logger.error(f"스크롤 중 오류: {str(scroll_error)}")
                    return True
            
            self.logger.warning("상세 페이지 확인 실패")
            return False
            
        except Exception as e:
            self.logger.error(f"상품 페이지 확인 중 오류: {str(e)}")
            return False