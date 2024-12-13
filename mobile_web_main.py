from search_automation import CoupangSearchAutomation
from product_finder import CoupangProductFinder

def main():
    search_automation = CoupangSearchAutomation()
    try:
        # URL로 검색 실행
        if search_automation.search_product_by_url("노트북"):
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