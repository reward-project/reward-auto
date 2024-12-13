from mobile_automation import MobileAutomation
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.logger import Logger
import time
import traceback
import os
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

class EnhancedCoupangAutomation(MobileAutomation):
    def __init__(self):
        super().__init__()
        self.logger = Logger('CoupangAutomation')
        self.logger.info("=== 쿠팡 자동화 시작 ===")
        self.logger.info("자동화 전략:")
        self.logger.info("1. 네이티브 UI 요소 탐색")
        self.logger.info("2. 다중 locator 전략 사용")
        self.logger.info("3. 동적 대기 및 재시도")
        self.logger.info("4. 스크린샷 기반 디버깅")
        
        self.resource_ids = {
            'search_button': 'com.coupang.mobile:id/search_button',
            'search_input': 'com.coupang.mobile:id/search_input',
            'product_list': 'com.coupang.mobile:id/product_list',
            'product_name': 'com.coupang.mobile:id/product_name',
            'cart_button': 'com.coupang.mobile:id/cart_button',
            'buy_button': 'com.coupang.mobile:id/buy_button'
        }
        self.logger.debug("리소스 ID 매핑 완료")

    def search_product(self, keyword):
        """향상된 상품 검색"""
        try:
            self.logger.info(f"\n=== 상품 검색 시작: {keyword} ===")
            self.logger.info("검색 전략:")
            self.logger.info("1. 다중 locator로 검색 버튼 찾기")
            self.logger.info("2. 검색창 접근 방식 다양화")
            self.logger.info("3. 키보드 입력 대체 방안 준비")
            
            # 앱 로딩 대기
            self.logger.debug("\n[1단계] 앱 초기화")
            time.sleep(5)
            self.logger.debug("- 앱 로딩 대기 완료")
            
            # 현재 화면 분석
            self.logger.debug("\n[2단계] 화면 분석")
            page_source = self.driver.page_source
            self.logger.debug("- 현재 화면 구조:")
            self.logger.debug(page_source)
            
            # 검색 버튼 찾기
            self.logger.debug("\n[3단계] 검색 버튼 찾기")
            search_locators = [
                (AppiumBy.ID, "com.coupang.mobile:id/search_button", "리소스 ID"),
                (AppiumBy.ACCESSIBILITY_ID, "검색", "접근성 레이블"),
                (AppiumBy.XPATH, "//android.widget.TextView[@content-desc='검색']", "XPath - TextView"),
                (AppiumBy.XPATH, "//android.widget.ImageView[@content-desc='검색']", "XPath - ImageView"),
                (AppiumBy.XPATH, "//*[@resource-id='com.coupang.mobile:id/search_button']", "XPath - 리소스 ID"),
                (AppiumBy.XPATH, "//android.widget.TextView[contains(@content-desc, '검색')]", "XPath - 부분일치"),
                (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().descriptionContains("검색")', "UiSelector")
            ]
            
            search_btn = None
            for locator_type, locator_value, strategy_name in search_locators:
                try:
                    self.logger.debug(f"- {strategy_name} 시도 중...")
                    search_btn = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((locator_type, locator_value))
                    )
                    if search_btn:
                        self.logger.info(f"✓ 검색 버튼 발견 - 전략: {strategy_name}")
                        break
                except Exception as e:
                    self.logger.debug(f"  → 실패: {str(e)}")
            
            if not search_btn:
                self.logger.error("✗ 모든 검색 전략 실패")
                raise Exception("검색 버튼을 찾을 수 없습니다")
            
            # 검색 실행
            self.logger.debug("\n[4단계] 검색 실행")
            self.driver.save_screenshot(os.path.join(self.logger.log_dir, 'before_search_click.png'))
            self.logger.debug("- ���릭 전 스크린샷 저장")
            
            search_btn.click()
            self.logger.debug("- 검색 버튼 클릭됨")
            time.sleep(2)
            
            # 검색어 입력
            self.logger.debug("\n[5단계] 검색어 입력")
            try:
                search_input_locators = [
                    (AppiumBy.ID, "com.coupang.mobile:id/search_input", "ID 직접 접근"),
                    (AppiumBy.XPATH, "//android.widget.EditText[@resource-id='com.coupang.mobile:id/search_input']", "XPath"),
                    (AppiumBy.CLASS_NAME, "android.widget.EditText", "클래스명")
                ]
                
                for locator_type, locator_value, strategy_name in search_input_locators:
                    self.logger.debug(f"- {strategy_name} 시도 중...")
                    try:
                        search_input = WebDriverWait(self.driver, 3).until(
                            EC.presence_of_element_located((locator_type, locator_value))
                        )
                        if search_input:
                            self.logger.info(f"✓ 검색창 발견 - 전략: {strategy_name}")
                            break
                    except:
                        self.logger.debug("  → 실패")
                
                if not search_input:
                    raise Exception("검색창을 찾을 수 없습니다")
                
                # 검색어 입력 부분 수정
                self.logger.debug("\n[6단계] 검색 수행")
                try:
                    # 검색창 초기화
                    search_input.click()
                    time.sleep(1)
                    
                    # 기존 텍스트 완전히 제거
                    search_input.clear()
                    time.sleep(0.5)
                    current_text = search_input.text
                    if current_text:
                        self.logger.debug(f"텍스트가 남아있음: {current_text}, 백스페이스로 제거 시도")
                        for _ in range(len(current_text)):
                            search_input.send_keys(Keys.BACKSPACE)
                            time.sleep(0.1)
                    
                    # 검색어 입력 전 상태 확인
                    self.logger.debug("검색창 상태 확인")
                    self.driver.save_screenshot(os.path.join(self.logger.log_dir, 'before_input.png'))
                    
                    # 검색어 한 글자씩 입력하며 확인
                    self.logger.debug(f"검색어 입력 시작: {keyword}")
                    for char in keyword:
                        search_input.send_keys(char)
                        time.sleep(0.1)
                        current = search_input.text
                        self.logger.debug(f"현재 입력된 텍스트: {current}")
                        
                        # 입력 확인
                        if char not in current:
                            self.logger.debug(f"문자 '{char}' 입력 실패, 재시도")
                            search_input.send_keys(char)
                            time.sleep(0.1)
                    
                    # 최종 입력 확인
                    final_text = search_input.text
                    self.logger.debug(f"최종 입력된 텍스트: {final_text}")
                    
                    if keyword not in final_text:
                        self.logger.debug("입력 실패, 전체 재입력 시도")
                        search_input.clear()
                        time.sleep(0.5)
                        search_input.send_keys(keyword)
                        time.sleep(0.5)
                    
                    # 검색 실행
                    try:
                        # 먼저 키보드 검색 버튼 찾기
                        keyboard_search_locators = [
                            (AppiumBy.ID, "com.android.inputmethod.latin:id/key_enter"),
                            (AppiumBy.ID, "com.google.android.inputmethod.latin:id/key_enter"),
                            (AppiumBy.XPATH, "//android.widget.Button[@text='검색']"),
                            (AppiumBy.XPATH, "//android.widget.Button[@text='이동']"),
                            (AppiumBy.XPATH, "//android.widget.Button[@text='완료']")
                        ]
                        
                        for locator_type, locator_value in keyboard_search_locators:
                            try:
                                self.logger.debug(f"키보드 버튼 찾기: {locator_value}")
                                button = self.driver.find_element(locator_type, locator_value)
                                button.click()
                                time.sleep(2)
                                if self.check_search_result():
                                    return True
                            except:
                                continue
                        
                        # 키보드 버튼을 찾지 못한 경우 Enter 키 전송
                        self.logger.debug("Enter 키 전송 시도")
                        search_input.send_keys(Keys.ENTER)
                        time.sleep(2)
                        
                        if self.check_search_result():
                            return True
                            
                        # 마지막으로 검색 버튼 클릭 시도
                        self.logger.debug("검색 버튼 클릭 시도")
                        search_button = self.driver.find_element(AppiumBy.ID, "com.coupang.mobile:id/search_submit")
                        search_button.click()
                        time.sleep(2)
                        
                        return self.check_search_result()
                        
                    except Exception as e:
                        self.logger.error(f"검색 실행 중 에러: {str(e)}")
                        self.logger.debug(f"상세 에러:\n{traceback.format_exc()}")
                        return False
                    
                except Exception as e:
                    self.logger.error(f"검색어 입력 중 에러: {str(e)}")
                    self.logger.debug(f"상세 에러:\n{traceback.format_exc()}")
                    return False
                
            except Exception as e:
                self.logger.error(f"✗ 검색창 조작 실패: {str(e)}")
                self.logger.debug(f"상세 에러:\n{traceback.format_exc()}")
                return False
                
        except Exception as e:
            self.logger.error(f"✗ 검색 프로세스 실패: {str(e)}")
            self.logger.debug(f"상세 에러:\n{traceback.format_exc()}")
            self.driver.save_screenshot(os.path.join(self.logger.log_dir, 'error_screenshot.png'))
            return False

    def try_search_button(self):
        """검색 버튼 찾아서 클릭"""
        search_button_locators = [
            (AppiumBy.ID, "com.coupang.mobile:id/search_submit"),
            (AppiumBy.ID, "com.coupang.mobile:id/search_button"),
            (AppiumBy.XPATH, "//android.widget.TextView[contains(@text, '검색')]"),
            (AppiumBy.XPATH, "//android.widget.Button[contains(@content-desc, '검색')]")
        ]
        
        for locator_type, locator_value in search_button_locators:
            try:
                button = self.driver.find_element(locator_type, locator_value)
                button.click()
                return True
            except:
                continue
        raise Exception("검색 버튼을 찾을 수 없음")

    def try_ime_search(self):
        """IME 액션 실행"""
        self.driver.execute_script('mobile: performEditorAction', {'action': 'search'})

    def try_keyboard_search(self):
        """키보드의 검색 버튼 찾아서 클릭"""
        keyboard_search_locators = [
            (AppiumBy.ID, "com.android.inputmethod.latin:id/key_pos_ime_action"),
            (AppiumBy.ID, "com.google.android.inputmethod.latin:id/key_pos_ime_action"),
            (AppiumBy.XPATH, "//android.widget.Button[contains(@resource-id, 'search')]")
        ]
        
        for locator_type, locator_value in keyboard_search_locators:
            try:
                button = self.driver.find_element(locator_type, locator_value)
                button.click()
                return True
            except:
                continue
        raise Exception("키보드 검색 버튼을 찾을 수 없음")

    def check_search_result(self):
        """검색 결과 로딩 확인"""
        try:
            # 검색 결과 로딩 대기
            time.sleep(3)
            
            # 검색 결과 확 방법들
            result_locators = [
                (AppiumBy.ID, "com.coupang.mobile:id/product_list"),
                (AppiumBy.XPATH, "//android.widget.TextView[contains(@text, '검색결과')]"),
                (AppiumBy.ID, "com.coupang.mobile:id/product_name")
            ]
            
            for locator_type, locator_value in result_locators:
                try:
                    self.driver.find_element(locator_type, locator_value)
                    return True
                except:
                    continue
                
            return False
        except:
            return False

    def find_product_by_complex_condition(self, name, price_range=None, rating=None):
        """복합 조건으로 상품 찾기"""
        self.logger.info(f"상품 검색 시작 - 이름: {name}, 가격: {price_range}, 평점: {rating}")
        max_scroll = 5
        scroll_count = 0
        
        while scroll_count < max_scroll:
            try:
                self.logger.debug(f"스크롤 {scroll_count + 1}/{max_scroll}")
                complex_selector = (
                    f'new UiSelector().resourceId("{self.resource_ids["product_name"]}")'
                    f'.textContains("{name}")'
                )
                self.logger.debug(f"검색 Selector: {complex_selector}")
                
                products = self.driver.find_elements(
                    AppiumBy.ANDROID_UIAUTOMATOR, 
                    complex_selector
                )
                self.logger.debug(f"발견된 상품 수: {len(products)}")
                
                for idx, product in enumerate(products, 1):
                    self.logger.debug(f"상품 {idx} 분석 중")
                    
                    if price_range:
                        try:
                            price_element = product.find_element(
                                AppiumBy.XPATH,
                                './following-sibling::*[contains(@resource-id, "price")]'
                            )
                            price = self.extract_price(price_element.text)
                            self.logger.debug(f"상품 가격: {price}")
                            if not (price_range[0] <= price <= price_range[1]):
                                continue
                        except Exception as e:
                            self.logger.warning(f"가격 확인 실패: {str(e)}")
                            continue
                    
                    if rating:
                        try:
                            rating_element = product.find_element(
                                AppiumBy.XPATH,
                                './following-sibling::*[contains(@resource-id, "rating")]'
                            )
                            current_rating = float(rating_element.text.split()[0])
                            self.logger.debug(f"상품 평점: {current_rating}")
                            if current_rating < rating:
                                continue
                        except Exception as e:
                            self.logger.warning(f"평점 확인 실패: {str(e)}")
                            continue
                    
                    self.logger.info("조건에 맞는 상품 발견")
                    product.click()
                    return True
                
                self.smart_scroll()
                scroll_count += 1
                
            except Exception as e:
                self.logger.error(f"상품 검색 중 에러: {str(e)}")
                self.logger.debug(f"상세 에러: {traceback.format_exc()}")
                scroll_count += 1
        
        self.logger.warning("조건에 맞는 상품을 찾지 못함")
        return False

    def smart_scroll(self):
        """스마트 스크롤"""
        try:
            self.logger.debug("스마트 스크롤 시작")
            items = self.driver.find_elements(
                AppiumBy.ID, 
                self.resource_ids['product_name']
            )
            
            if items:
                last_item = items[-1]
                location = last_item.location
                size = last_item.size
                
                self.logger.debug(f"마지막 아이템 위치: {location}, 크기: {size}")
                self.driver.swipe(
                    location['x'],
                    location['y'],
                    location['x'],
                    50,
                    duration=1000
                )
                time.sleep(1)
                
            self.logger.debug("스크롤 완료")
            
        except Exception as e:
            self.logger.error(f"스크롤 중 에러: {str(e)}")
            self.logger.debug(f"상세 에러: {traceback.format_exc()}")
            self.scroll_down()

    def wait_for_element(self, resource_id, timeout=10):
        """요소 대기"""
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((AppiumBy.ID, resource_id))
        )

    def wait_and_click_by_selector(self, selector, timeout=10):
        """UiSelector로 요소 찾아 클릭"""
        element = WebDriverWait(self.driver, timeout).until(
            lambda d: d.find_element(AppiumBy.ANDROID_UIAUTOMATOR, selector)
        )
        element.click()

    @staticmethod
    def extract_price(price_text):
        """가격 텍스트에서 숫자만 추출"""
        return int(''.join(filter(str.isdigit, price_text))) 