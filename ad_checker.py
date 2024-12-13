from selenium.webdriver.common.by import By
from utils.logger import Logger

class AdChecker:
    def __init__(self):
        self.logger = Logger('AdChecker')

    def find_ad_elements(self, container):
        """광고 관련 엘리먼트 검색"""
        try:
            # 광고 텍스트를 포함하는 모든 엘리먼트 찾기
            all_elements = container.find_elements(By.XPATH, ".//*[contains(text(), '광고')]")
            
            ad_elements = []
            for element in all_elements:
                element_text = element.text
                element_html = element.get_attribute('outerHTML')
                parent_a = element.find_element(By.XPATH, "./ancestor::a[contains(@href, '/products/')]")
                parent_url = parent_a.get_attribute('href') if parent_a else "상위 a태그 없음"
                
                ad_info = {
                    'element_text': element_text,
                    'element_html': element_html,
                    'parent_url': parent_url
                }
                ad_elements.append(ad_info)
            
            return ad_elements
            
        except Exception as e:
            self.logger.error(f"광고 엘리먼트 검색 중 에러: {str(e)}")
            return []

    def is_ad_product(self, container, href):
        """상품이 광고인지 확인"""
        try:
            # 기존 광고 배지 확인
            ad_badge = container.find_elements(By.CSS_SELECTOR, 
                'span.ad-badge, span.ad-badge-text, div.details > span.ad-badge')
            
            # 광고 텍스트 검색
            ad_elements = self.find_ad_elements(container)
            
            # URL 파라미터로 광고 확인
            is_ad = ('sourceType=srp_product_ads' in href or 
                    bool(ad_badge) or 
                    bool(ad_elements))
            
            if is_ad:
                self.logger.debug(f"광고 상품 감: {href}")
                if ad_elements:
                    self.logger.debug("광고 텍스트 발견됨")
                
            return is_ad
            
        except Exception as e:
            self.logger.error(f"광고 체크 중 에러: {str(e)}")
            return False

    def check_product_status(self, container, product_id):
        """상품의 광고 여부 상태 확인"""
        try:
            link = container.find_element(By.CSS_SELECTOR, 'a[href*="/products/"]')
            href = link.get_attribute('href')
            
            # 광고 엘리먼트 검사 먼저 실행
            ad_elements = self.find_ad_elements(container)
            
            is_ad = self.is_ad_product(container, href)
            
            return {
                'href': href,
                'is_ad': is_ad,
                'ad_elements': ad_elements
            }
            
        except Exception as e:
            self.logger.error(f"상품 상태 체크 중 에러: {str(e)}")
            return None 

    def check_page_products(self, containers, target_product_id):
        """페이지 내 모든 상품의 광고 여부 체크"""
        try:
            target_product = None
            target_ad_count = 0
            target_normal_count = 0
            
            for container in containers:
                try:
                    link = container.find_element(By.CSS_SELECTOR, 'a[href*="/products/"]')
                    href = link.get_attribute('href')
                    current_product_id, _ = self.extract_product_id(href)
                    
                    # 찾는 상품인 경우에만 카운트
                    if current_product_id == target_product_id:
                        status = self.check_product_status(container, current_product_id)
                        if status['is_ad']:
                            target_ad_count += 1
                        else:
                            target_normal_count += 1
                            target_product = container
                
                except Exception as e:
                    continue
            
            # 찾는 상품의 광고/일반 수 로깅
            if target_ad_count + target_normal_count > 0:
                self.logger.info(f"\n=== 상품 ID: {target_product_id} 발견 현황 ===")
                self.logger.info(f"광고 상품: {target_ad_count}개")
                self.logger.info(f"일반 상품: {target_normal_count}개")
            
            return {
                'target_product': target_product,
                'target_ad_count': target_ad_count,
                'target_normal_count': target_normal_count
            }
            
        except Exception as e:
            self.logger.error(f"페이지 상품 체크 중 에러: {str(e)}")
            return {
                'target_product': None,
                'target_ad_count': 0,
                'target_normal_count': 0
            }

    def extract_product_id(self, href):
        """URL에서 상품 ID와 itemId 추출"""
        try:
            product_id = None
            item_id = None
            
            if '/products/' in href:
                parts = href.split('/products/')[-1].split('?')
                if parts:
                    product_id = parts[0]
            elif '/vp/products/' in href:
                parts = href.split('/vp/products/')[-1].split('?')
                if parts:
                    product_id = parts[0]
            
            if 'itemId=' in href:
                item_id = href.split('itemId=')[-1].split('&')[0]
            
            return product_id, item_id
        except:
            return None, None 