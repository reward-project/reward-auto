from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.logger import Logger
from popup_handler import PopupHandler
from pagination_handler import PaginationHandler
from ad_checker import AdChecker
import time

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

    def find_product_by_id(self, productId):
        """상품 ID로 상품 찾기"""
        try:
            self.logger.info(f"상품 검색 - ID: {productId}")
            
            while True:  # 모든 페이지 검색
                # 팝업 처리
                self.popup_handler.close_all_popups()
                
                # 현재 페이지 정보
                current_page = self.pagination_handler.get_current_page()
                total_count = self.pagination_handler.get_total_count()
                self.logger.info(f"현재 페이지: {current_page} (전체 상품 수: {total_count})")
                
                # 현재 페이지에서 상품 찾기
                if self.find_product_in_current_page(productId):
                    return True
                
                # 다음 페이지가 있으면 이동, 없으면 종료
                if not self.pagination_handler.has_next_page():
                    self.logger.warning("마지막 페이지까지 검색 완료")
                    break
                    
                if not self.pagination_handler.go_to_next_page():
                    self.logger.error("페이지 이동 실패")
                    break
            
            self.logger.warning("상품을 찾지 못함")
            return False
            
        except Exception as e:
            self.logger.error(f"상품 검색 중 에러: {str(e)}")
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
            self.logger.error(f"��품 검색 중 에러: {str(e)}")
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