from web_automation import CoupangWebAutomation

def main():
    automation = CoupangWebAutomation()
    try:
        # 상품 검색
        if automation.search_product("노트북"):
            # 조건에 맞는 상품 찾기
            target_product = {
                'name': 'LG gram',
                'price_range': (1000000, 2000000),
                'rating': 4.5
            }
            
            if automation.find_product_by_conditions(
                target_product['name'],
                target_product['price_range'],
                target_product['rating']
            ):
                print("상품을 찾았습니다!")
            else:
                print("조건에 맞는 상품이 없습니다.")
        else:
            print("검색에 실패했습니다.")
            
    finally:
        automation.close()

if __name__ == "__main__":
    main() 