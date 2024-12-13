from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.logger import Logger
from popup_handler import PopupHandler
from pagination_handler import PaginationHandler
import time

class CoupangProductFinder:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)
        self.logger = Logger('CoupangProductFinder')
        self.popup_handler = PopupHandler(self.driver)
        self.pagination_handler = PaginationHandler(self.driver)
        
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
        """현재 페이지에서 상품 찾기"""
        try:
            max_scroll = 5
            scroll_count = 0
            
            while scroll_count < max_scroll:
                # 팝업 처리
                self.popup_handler.close_all_popups()
                
                # 현재 페이지의 모든 상품 링크 수집
                all_links = self.driver.find_elements(By.CSS_SELECTOR, '#productList a[href*="/products/"]')
                self.logger.info(f"\n=== 현재 페이지 상품 목록 (총 {len(all_links)}개) ===")
                
                # 상품 ID 추출 및 표시
                found_ids = []
                for link in all_links:
                    try:
                        href = link.get_attribute('href')
                        product_id, item_id = self.extract_product_id(href)
                        
                        if product_id:
                            id_info = f"{product_id}"
                            if item_id:
                                id_info += f" (itemId: {item_id})"
                            found_ids.append(id_info)
                            
                            # 찾는 상품인 경우
                            if product_id == productId:
                                self.logger.info(f"\n=== 찾는 상품 발견! (ID: {productId}, itemId: {item_id}) ===")
                                self.driver.get(href)
                                time.sleep(3)
                                return True
                                
                    except Exception as e:
                        continue
                
                # 발견된 모든 상품 ID 출력
                self.logger.info("발견된 상품 ID 목록:")
                self.logger.info("\n".join(found_ids))  # 각 ID를 새 줄에 표시
                
                # 스크롤
                before_height = self.driver.execute_script("return document.documentElement.scrollHeight")
                self.driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
                time.sleep(2)
                after_height = self.driver.execute_script("return document.documentElement.scrollHeight")
                
                if after_height == before_height:
                    self.logger.debug("더 이상 스크롤할 수 없음")
                    break
                
                scroll_count += 1
                self.logger.debug(f"스크롤 {scroll_count}/{max_scroll}")
            
            self.logger.warning("상품을 찾지 못함")
            return False
            
        except Exception as e:
            self.logger.error(f"상품 검색 중 에러: {str(e)}")
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
            
            # 쿼리 파라미터 파싱
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