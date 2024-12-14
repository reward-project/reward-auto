from search_automation import CoupangSearchAutomation
from product_finder import CoupangProductFinder
import logging
from selenium.common.exceptions import WebDriverException
#appium
#python mobile_web_main.py 


def main():
    search_automation = CoupangSearchAutomation()
    try:
        # URL로 검색 실행
        try:
            search_success = search_automation.search_product_by_url("노트북")
        except WebDriverException as e:
            if "net::ERR_INTERNET_DISCONNECTED" in str(e):
                print("인터넷 연결이 끊어졌습니다. 네트워크 연결을 확인해주세요.")
                return
            else:
                print(f"검색 중 오류가 발생했습니다: {str(e)}")
                return

        if search_success:
            # 검색 성공 시 상품 찾기 시작
            product_finder = CoupangProductFinder(search_automation.get_driver())
            
            target_product_id = '6662026640'
            if product_finder.find_product_by_id(target_product_id):
                print(f"상품을 찾았습니다! (Product ID: {target_product_id})")
            else:
                print("상품을 찾지 못했습니다.")
        else:
            print("검색에 실패했습니다.")
            
    finally:
        search_automation.close()

if __name__ == "__main__":
    main() 