import subprocess
import time
from bs4 import BeautifulSoup
import sys

def search_in_coupang(adb_path, search_keyword):
    """쿠팡 앱에서 검색 실행"""
    try:
        # URI 인코딩된 검색어로 검색 실행
        encoded_keyword = search_keyword.replace(' ', '%20')
        subprocess.run(
            f'{adb_path} shell am start -a android.intent.action.VIEW -d "coupang://search?q={encoded_keyword}" com.coupang.mobile',
            shell=True
        )
        time.sleep(3)
        return True
    except Exception as e:
        print(f"검색 실행 중 오류 발생: {str(e)}")
        return False

def dump_ui():
    """현재 화면의 XML 구조를 덤프하는 함수"""
    try:
        subprocess.run("adb shell uiautomator dump /sdcard/window_dump.xml", shell=True)
        time.sleep(1)
        subprocess.run("adb pull /sdcard/window_dump.xml .", shell=True)
        time.sleep(1)
        
        with open("window_dump.xml", "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"UI 덤프 중 오류 발생: {str(e)}")
        return None

def check_product_rank(search_keyword="베르가못", target_product_name="VitalBio", target_product_id="8279505062"):
    """특정 상품의 검색 결과 순위를 확인하는 함수"""
    try:
        # 기존 쿠팡 앱 강제 종료
        print("기존 쿠팡 앱 종료 중...")
        subprocess.run("adb shell am force-stop com.coupang.mobile", shell=True)
        time.sleep(2)
        
        # 검색 실행
        print(f"'{search_keyword}' 검색어로 순위 확인 중...")
        if search_in_coupang("adb", search_keyword):
            time.sleep(5)  # 검색 결과 로딩 대기
            
            found = False
            page = 1
            max_pages = 5  # 최대 5페이지까지만 확인
            
            while not found and page <= max_pages:
                # XML 덤프 가져오기
                xml_data = dump_ui()
                if not xml_data:
                    break
                
                # BeautifulSoup으로 XML 파싱
                soup = BeautifulSoup(xml_data, 'lxml')
                
                # VitalBio 텍스트를 포함하는 노드 찾기
                nodes = soup.find_all('node', {'text': lambda text: text and target_product_name in text})
                
                for node in nodes:
                    print(f"\n상품 '{target_product_name}'을 찾았습니다!")
                    bounds = node.get('bounds', '')
                    if bounds:
                        try:
                            # bounds format: [x1,y1][x2,y2]
                            coords = bounds.replace('][', ',').strip('[]').split(',')
                            x = (int(coords[0]) + int(coords[2])) // 2
                            y = (int(coords[1]) + int(coords[3])) // 2
                            
                            print(f"클릭 좌표: {x}, {y}")
                            subprocess.run(f"adb shell input tap {x} {y}", shell=True)
                            time.sleep(3)
                            
                            # 상품 ID 확인
                            xml_data = dump_ui()
                            if target_product_id in xml_data:
                                print("썸네일, 전체 상품 페이지 및 리뷰 확인 완료")
                                print("1번 성공")
                                return True
                            else:
                                print("상품 ID를 확인할 수 없습니다. 다음 항목 확인 중...")
                                continue
                        except Exception as e:
                            print(f"좌표 처리 중 오류: {str(e)}")
                            continue
                
                # 다음 페이지로 스크롤
                subprocess.run("adb shell input swipe 500 1800 500 300", shell=True)
                time.sleep(2)
                page += 1
            
            if not found:
                print(f"\n상품 '{target_product_name}'을 찾지 못했습니다.")
                return None
                
    except Exception as e:
        print(f"순위 확인 중 오류 발생: {str(e)}")
        return None
    finally:
        # 앱 종료
        print("\n앱 종료 중...")
        subprocess.run("adb shell am force-stop com.coupang.mobile", shell=True)
        time.sleep(1)

if __name__ == "__main__":
    # 검색어와 상품명을 인자로 받을 수 있게 함
    if len(sys.argv) > 2:
        keyword = sys.argv[1]
        product_name = sys.argv[2]
    else:
        keyword = "베르가못"  # 기본 검색어
        product_name = "VitalBio"  # 찾고자 하는 상품명
    
    result = check_product_rank(keyword, product_name)
    if result:
        print(f"상품 '{product_name}'을 찾아서 클릭했습니다.") 