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
        """상품 ID 또는 제품명으로 상품 찾기"""
        try:
            # 스크롤 속도 설정 읽기
            try:
                df = pd.read_excel('coupang_click.xlsx')
                scroll_speed = str(df[df['number'] == 0]['scroll'].iloc[0]).strip().upper()
            except:
                scroll_speed = 'M'  # 기본값
            
            self.logger.info(f"스크롤 속도 설정: {'사람 속도(H)' if scroll_speed == 'H' else '기본 속도(M)'}")
            
            # target_product_id가 float인 경우 문자열로 변환
            target_product_id = str(target_product_id).split('.')[0]  # float 부분 제거
            self.logger.info(f"상품 검색 시작 - ID: {target_product_id}, 제품명: {product_name}, 광고: {is_ad}")
            
            # 상품명이 있으면 로그 출력
            if product_name:
                self.logger.info(f"검색할 상품명: {product_name}")
            
            while True:  # 모든 페이지 검색
                # 팝업 처리
                self.popup_handler.close_all_popups()
                
                # 현재 페이지에서 상품 찾기
                product_containers = self.driver.find_elements(By.CSS_SELECTOR, '#productList li')
                self.logger.info(f"현재 페이지 상품 수: {len(product_containers)}")
                
                # 스크롤 처리
                total_height = self.driver.execute_script("return document.body.scrollHeight")
                current_position = 0
                
                while current_position < total_height:
                    if scroll_speed == 'H':  # 사람 속도
                        scroll_amount = random.randint(100, 300)
                        current_position += scroll_amount
                        self.driver.execute_script(f"window.scrollTo({{top: {current_position}, behavior: 'smooth'}})")
                        time.sleep(random.uniform(0.8, 2.0))
                        
                        # 가끔 잠깐 멈춤 (20% 확률)
                        if random.random() < 0.2:
                            time.sleep(random.uniform(0.5, 1.5))
                    else:  # 기본 속도
                        scroll_amount = random.randint(300, 500)
                        current_position += scroll_amount
                        self.driver.execute_script(f"window.scrollTo(0, {current_position})")
                        time.sleep(random.uniform(0.3, 0.7))
                
                # 광고/일반 상품 구분 처리
                for container in product_containers:
                    try:
                        # 제품명 확인 (있는 경우)
                        if product_name:
                            try:
                                # 여러 선택자로 상품명 찾기 시도
                                title_selectors = [
                                    '.name',
                                    'div.name',
                                    'div.product-name',
                                    'a[href*="/products/"] .name'
                                ]
                                
                                product_title = None
                                for selector in title_selectors:
                                    try:
                                        title_element = container.find_element(By.CSS_SELECTOR, selector)
                                        product_title = title_element.text.strip()
                                        if product_title:
                                            break
                                    except:
                                        continue
                                
                                if not product_title:
                                    continue
                                    
                                self.logger.info(f"상품명 비교: 검색={product_name}, 발견={product_title}")
                                
                                # 상품명 비교 (대소문자 구분 없이, 부분 일치)
                                if product_name.lower() in product_title.lower():
                                    self.logger.info(f"상품명 일치: {product_title}")
                                else:
                                    self.logger.info(f"상품명 불일치. 다음 상품 확인")
                                    continue
                                    
                            except Exception as title_error:
                                self.logger.error(f"상품명 확인 중 오류: {str(title_error)}")
                                continue
                        
                        # 링크 찾기
                        links = container.find_elements(By.CSS_SELECTOR, 'a[href*="/products/"]')
                        for link in links:
                            product_url = link.get_attribute('href')
                            self.logger.info(f"검사 중인 상품 URL: {product_url}")
                            
                            # 광고 여부 확인
                            is_ad_product = 'search-product-ad' in container.get_attribute('class')
                            self.logger.info(f"광고 상품 여부: {is_ad_product}")
                            
                            # ID 또는 제품명이 일치하고, 광고 여부가 일치하는 경우
                            if ((target_product_id in product_url) and is_ad == is_ad_product):
                                self.logger.info(f"목표 상품 발견! URL: {product_url}")
                                
                                try:
                                    # 방해되는 요소 제거
                                    self.driver.execute_script("""
                                        var elements = document.getElementsByClassName('service-shortcut-row-toggle');
                                        for(var i=0; i<elements.length; i++) {
                                            elements[i].style.display = 'none';
                                        }
                                    """)
                                    
                                    # 상품 위치로 스크롤
                                    try:
                                        container_location = container.location['y']
                                        viewport_height = self.driver.execute_script("return window.innerHeight")
                                        scroll_to = max(0, container_location - (viewport_height / 3))
                                        
                                        if scroll_speed == 'H':
                                            # 사람 속도: 천천히 스크롤
                                            current_pos = self.driver.execute_script("return window.pageYOffset")
                                            steps = 10  # 10단계로 나누어 스크롤
                                            for i in range(steps + 1):
                                                pos = current_pos + ((scroll_to - current_pos) * (i / steps))
                                                self.driver.execute_script(f"window.scrollTo(0, {pos})")
                                                time.sleep(random.uniform(0.1, 0.3))
                                        else:
                                            # 기본 속도
                                            self.driver.execute_script(f"window.scrollTo(0, {scroll_to})")
                                            time.sleep(0.5)
                                            
                                    except Exception as scroll_error:
                                        self.logger.error(f"스크롤 오류: {scroll_error}")
                                    
                                    # 클릭 전 대기
                                    if scroll_speed == 'H':
                                        time.sleep(random.uniform(1.0, 2.0))
                                    else:
                                        time.sleep(0.5)
                                    
                                    # 클릭 시도
                                    try:
                                        wait = WebDriverWait(self.driver, 10)
                                        clickable = wait.until(EC.element_to_be_clickable(link))
                                        clickable.click()
                                    except:
                                        self.driver.execute_script("arguments[0].click();", link)
                                    
                                    time.sleep(2)
                                    if self.check_detail_page(target_product_id):
                                        return True
                                    return False
                                    
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
            # 스크롤 속도 설정 읽기
            try:
                df = pd.read_excel('coupang_click.xlsx')
                scroll_speed = str(df[df['number'] == 0]['scroll'].iloc[0]).strip().upper()
            except:
                scroll_speed = 'M'  # 기본값
            
            time.sleep(3)  # 페이지 로딩 대기
            
            # 현재 URL에서 상품 ID 확인
            current_url = self.driver.current_url
            self.logger.info(f"상세 페이지 URL: {current_url}")
            
            # 상품 ID 확인
            if target_product_id in current_url:
                try:
                    # 전체 페이지 높이 확인
                    total_height = self.driver.execute_script("return document.body.scrollHeight")
                    window_height = self.driver.execute_script("return window.innerHeight")
                    scroll_positions = []
                    
                    # 스크롤 위치 계산
                    current_position = 0
                    while current_position < total_height:
                        if scroll_speed == 'H':  # 사람 속도
                            # 더 작은 단위로 스크롤하고 랜덤한 일시 정지 추가
                            scroll_amount = random.randint(100, 300)
                            current_position += scroll_amount
                            scroll_positions.append(min(current_position, total_height))
                        else:  # 기본 속도
                            scroll_amount = random.randint(300, 500)
                            current_position += scroll_amount
                            scroll_positions.append(min(current_position, total_height))
                    
                    # 자연스러운 스크롤 수행
                    for position in scroll_positions:
                        if scroll_speed == 'H':
                            # 사람 속도: 부드러운 스크롤과 랜덤한 일시 정지
                            self.driver.execute_script(f"window.scrollTo({{top: {position}, behavior: 'smooth'}})")
                            time.sleep(random.uniform(0.8, 2.0))  # 더 긴 대기 시간
                            
                            # 가끔 잠깐 멈춤 (20% 확률)
                            if random.random() < 0.2:
                                time.sleep(random.uniform(0.5, 1.5))
                        else:
                            # 기본 속도
                            self.driver.execute_script(f"window.scrollTo(0, {position})")
                            time.sleep(random.uniform(0.3, 0.7))
                    
                    # 리뷰 또는 상품평 섹션 찾기
                    review_found = False
                    review_selectors = [
                        'div.sdp-review__article',  # 리뷰
                        'div.product-review',       # 상품평
                        'div.js_reviewArticleContainer', # 상품평 컨테이너
                        '#btfTab > ul.product-tab-list > li.product-review-tab' # 상품평 탭
                    ]
                    
                    for selector in review_selectors:
                        try:
                            review_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                            self.logger.info(f"리뷰/상품평 섹션 발견: {selector}")
                            
                            # 해당 섹션으로 스크롤
                            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", review_element)
                            time.sleep(random.uniform(1, 2))
                            
                            # 상품평 탭인 경우 클릭
                            if 'product-review-tab' in selector:
                                review_element.click()
                                time.sleep(random.uniform(1, 2))
                            
                            review_found = True
                            break
                        except:
                            continue
                    
                    if not review_found:
                        self.logger.info("리뷰/상품평 섹션 없음")
                    
                    # 가끔 위로 살짝 스크롤
                    if random.random() < 0.3:
                        up_scroll = random.randint(100, 300)
                        self.driver.execute_script(f"window.scrollBy({{top: -{up_scroll}, behavior: 'smooth'}})")
                        time.sleep(random.uniform(0.5, 1))
                    
                    # 상세 페이지 체류 시간
                    time.sleep(random.uniform(3, 5))
                    
                    return True
                    
                except Exception as scroll_error:
                    self.logger.error(f"스크롤 중 오류: {str(scroll_error)}")
                    return True  # 스크롤 실패해도 상품 ID가 일치하면 성공으로 간주
            
            self.logger.warning("상세 페이지 확인 실패")
            return False
            
        except Exception as e:
            self.logger.error(f"상��� 페이지 확인 중 오류: {str(e)}")
            return False