from enhanced_native_automation import EnhancedCoupangAutomation

def main():
    automation = EnhancedCoupangAutomation()
    
    # 상품 검색
    automation.search_product("노트북")
    
    # 복합 조건으로 상품 찾기
    target_product = {
        'name': 'LG gram',
        'price_range': (1000000, 2000000),  # 100~200만원
        'rating': 4.5  # 4.5점 이상
    }
    
    if automation.find_product_by_complex_condition(
        target_product['name'],
        target_product['price_range'],
        target_product['rating']
    ):
        print("조건에 맞는 상품을 찾았습니다!")
    else:
        print("조건에 맞는 상품을 찾지 못했습니다.")

if __name__ == "__main__":
    main() 