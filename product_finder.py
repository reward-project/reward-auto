from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.logger import Logger
from popup_handler import PopupHandler
from pagination_handler import PaginationHandler
from ad_checker import AdChecker
import time
import random

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

    def find_product_by_id(self, target_product_id, is_ad=False):
        """상품 ID로 상품 찾기"""
        try:
            # target_product_id가 float인 경우 문자열로 변환
            target_product_id = str(target_product_id).split('.')[0]  # float 부분 제거
            self.logger.info(f"상품 검색 시작 - ID: {target_product_id} (광고: {is_ad})")
            
            while True:  # 모든 페이지 검색
                # 팝업 처리
                self.popup_handler.close_all_popups()
                
                # 현재 페이지에서 상품 찾기
                product_containers = self.driver.find_elements(By.CSS_SELECTOR, '#productList li')
                self.logger.info(f"현재 페이지 상품 수: {len(product_containers)}")
                
                # 광고/일반 상품 구분 처리
                for container in product_containers:
                    try:
                        # 링크 찾기
                        links = container.find_elements(By.CSS_SELECTOR, 'a[href*="/products/"]')
                        for link in links:
                            product_url = link.get_attribute('href')
                            self.logger.info(f"검사 중인 상품 URL: {product_url}")
                            
                            # 광고 여부 확인
                            is_ad_product = 'search-product-ad' in container.get_attribute('class')
                            self.logger.info(f"광고 상품 여부: {is_ad_product}")
                            
                            # 타겟 상품 ID가 URL에 포함되어 있고, 광고 여부가 일치하는 경우
                            if target_product_id in product_url and is_ad == is_ad_product:
                                self.logger.info(f"목표 상품 발견! URL: {product_url}")
                                
                                try:
                                    # 방해되는 요소 제거
                                    self.driver.execute_script("""
                                        var elements = document.getElementsByClassName('service-shortcut-row-toggle');
                                        for(var i=0; i<elements.length; i++) {
                                            elements[i].style.display = 'none';
                                        }
                                    """)
                                    
                                    # 스크롤 위치 조정
                                    self.driver.execute_script("window.scrollBy(0, -150);")  # 약간 위로 스크롤
                                    time.sleep(1)
                                    
                                    # 클릭 시도 1: 직접 클릭
                                    try:
                                        self.logger.info("직접 클릭 시도...")
                                        link.click()
                                        self.logger.info("직접 클릭 성공!")
                                        time.sleep(3)
                                        # 상세 페이지 확인 및 스크롤
                                        if self.check_detail_page(target_product_id):
                                            return True
                                        return False
                                    except Exception as click_error:
                                        self.logger.info(f"직접 클릭 실패: {str(click_error)}")
                                        
                                        # 클릭 시도 2: JavaScript 클릭
                                        try:
                                            self.logger.info("JavaScript 클릭 시도...")
                                            self.driver.execute_script("arguments[0].click();", link)
                                            self.logger.info("JavaScript 클릭 성공!")
                                            time.sleep(3)
                                            # 상세 페이지 확인 및 스크롤
                                            if self.check_detail_page(target_product_id):
                                                return True
                                            return False
                                        except Exception as js_error:
                                            self.logger.error(f"JavaScript 클릭 실패: {str(js_error)}")
                                            continue
                                    
                                except Exception as e:
                                    self.logger.error(f"상품 클릭 처리 중 오류: {str(e)}")
                                    continue
                                
                    except Exception as e:
                        self.logger.error(f"상품 컨테이너 처리 중 오류: {str(e)}")
                        continue
                
                # 다음 페이지 확인
                if not self.pagination_handler.has_next_page():
                    self.logger.info("마지막 페이지 도달")
                    break
                    
                # 다음 페이지로 이동
                if not self.pagination_handler.go_to_next_page():
                    self.logger.error("페이지 이동 실패")
                    break
                
                time.sleep(2)
            
            self.logger.warning("상품을 찾지 못했습니다.")
            return False
            
        except Exception as e:
            self.logger.error(f"상품 검색 중 오류: {str(e)}")
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
            time.sleep(2)  # 페이지 로딩 대기
            
            # 현재 URL에서 상품 ID 확인
            current_url = self.driver.current_url
            self.logger.info(f"상세 페이지 URL: {current_url}")
            
            # 상품 ID 확인
            if target_product_id in current_url:
                try:
                    # 전체 페이지 높이 확인
                    total_height = self.driver.execute_script("return document.body.scrollHeight")
                    
                    # 한 번에 10% 지점까지 부드럽게 스크롤
                    target_position = total_height * 0.1  # 10% 지점으로 수정
                    self.driver.execute_script(f"window.scrollTo({{top: {target_position}, behavior: 'smooth'}})")
                    time.sleep(1.5)  # 스크롤 후 대기
                    
                    return True
                    
                except Exception as scroll_error:
                    self.logger.error(f"스크롤 중 오류: {str(scroll_error)}")
                    return True  # 스크롤 실패해도 상품 ID가 일치하면 성공으로 간주
            
            self.logger.warning("상세 페이지 확인 실패")
            return False
            
        except Exception as e:
            self.logger.error(f"상세 페이지 확인 중 오류: {str(e)}")
            return False