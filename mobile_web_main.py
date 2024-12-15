from search_automation import CoupangSearchAutomation
from product_finder import CoupangProductFinder
import logging
from selenium.common.exceptions import WebDriverException
import os
import time
import subprocess
import pandas as pd
import msvcrt

def get_smartphone_ip():
    """스마트폰의 공인 IP 주소 확인"""
    try:
        urls = [
            "https://api.ip.pe.kr/",
            "https://ipv4.icanhazip.com",
            "https://api.ipify.org"
        ]
        
        for url in urls:
            command = ["adb", "shell", "curl", "-s", url]
            result = subprocess.run(command, capture_output=True, text=True)
            
            if result.returncode == 0:
                ip_address = result.stdout.strip()
                import re
                if re.match(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$', ip_address):
                    return ip_address
        
        return "IP 주소를 찾을 수 없습니다."
    except Exception as e:
        return f"IP 확인 오류: {e}"

def toggle_cellular_data():
    """셀룰러 데이터 켜고 끄기"""
    try:
        print("셀룰러 데이터 끄기...")
        os.system("adb shell svc data disable")
        print("IP 변경을 위해 15초 대기 중...")
        time.sleep(15)
        
        print("셀룰러 데이터 켜기...")
        os.system("adb shell svc data enable")
        print("네트워크 재연결 및 새 IP 할당을 위해 30초 대기 중...")
        time.sleep(30)
        
        # 연결 상태 확인 (2회만 시도)
        print("네트워크 연결 확인 중...")
        for _ in range(2):
            data_enabled = os.popen("adb shell settings get global mobile_data").read().strip()
            if data_enabled == "1":
                test_result = os.popen('adb shell ping -c 1 8.8.8.8').read()
                if "1 packets transmitted" in test_result:
                    print("셀룰러 데이터 연결 완료")
                    time.sleep(3)
                    
                    # IP 변경 확인
                    new_ip = get_smartphone_ip()
                    if "찾을 수 없습니다" not in new_ip and "오류" not in new_ip:
                        print(f"새로운 IP 확인: {new_ip}")
                        return True
            print("연결 대기 중...")
            time.sleep(3)
        
        # 마지막으로 한 번 더 IP 확인
        final_ip = get_smartphone_ip()
        if "찾을 수 없습니다" not in final_ip and "오류" not in final_ip:
            print(f"최종 IP 확인: {final_ip}")
            return True
            
        print("셀룰러 데이터 연결 실패")
        return False
            
    except Exception as e:
        print(f"셀룰러 데이터 전환 중 오류: {e}")
        return False

def change_ip():
    """IP 변경 및 확인"""
    print("\n=== IP 변경 프로세스 시작 ===")
    
    # 초기 IP 확인
    initial_ip = get_smartphone_ip()
    print(f"현재 IP: {initial_ip}")
    
    # 셀룰러 데이터 전환으로 IP 변경
    print("\n셀룰러 데이터 전환 시도...")
    if not toggle_cellular_data():
        print("IP 변경 실패")
        return False
    
    # 새 IP 확인
    new_ip = get_smartphone_ip()
    print(f"변경된 IP: {new_ip}")
    
    if initial_ip != new_ip and "찾을 수 없습니다" not in new_ip:
        print("IP 변경 성공!")
        return True
    else:
        print("IP가 변경되지 않았습니다.")
        return False

def toggle_location_service(mode):
    """위치 서비스 켜고 끄기"""
    try:
        if mode == 'test_location_mode_off':
            print("모바일 및 웹 위치 서비스 모두 끄기...")
            os.system("adb shell settings put secure location_mode 0")
            time.sleep(2)
            print("모든 위치 서비스가 비활성화되었습니다.")
            return True
        elif mode == 'test_location_mode_mobileoff':
            print("모바일 위치 서비스 끄기...")
            os.system("adb shell settings put secure location_mode 0")
            time.sleep(2)
            print("모바일 위치 서비스가 비활성화되었습니다.")
            return True
        elif mode == 'test_location_mode_mobileon':
            print("모바일 위치 서비스 켜기...")
            os.system("adb shell settings put secure location_mode 3")
            time.sleep(2)
            print("모바일 위치 서비스가 활성화되었습니다.")
            return True
        elif mode == 'test_location_mode_weboff':
            print("웹 위치 서비스 끄기...")
            os.system("adb shell settings put secure location_mode 0")
            time.sleep(2)
            print("웹 위치 서비스가 비활성화되었습니다.")
            return True
        elif mode == 'test_location_mode_webon':
            print("웹 위치 서비스 켜기...")
            os.system("adb shell settings put secure location_mode 3")
            time.sleep(2)
            print("웹 위치 서비스가 활성화되었습니다.")
            return True
        else:
            print(f"알 수 없는 위치 서비스 모드: {mode}")
            return False
    except Exception as e:
        print(f"위치 서비스 설정 중 오류: {str(e)}")
        return False

def process_product(keyword, target_product_id, click_count, ad_click_count, should_change_ip, location_mode):
    """개별 상품 처리"""
    print(f"\n=== 상품 처리 시작 ===")
    print(f"키워드: {keyword}")
    print(f"상품 ID: {target_product_id}")
    print(f"일반 클릭 횟수: {click_count}")
    print(f"광고 클릭 횟수: {ad_click_count}")
    print(f"위치 서비스 모드: {location_mode}")

    # 위치 서비스 설정
    if location_mode in ['location_mobile_off', 'location_web_on']:
        if not toggle_location_service(location_mode):
            print("위치 서비스 설정 실패")
            return

    total_clicks = click_count + ad_click_count
    
    detail_success = 0  # 일반 상품 상세 페이지 성공 횟수
    detail_ad_success = 0  # 광고 상품 상세 페이지 성공 횟수
    
    for click_num in range(total_clicks):
        print(f"\n--- 클릭 {click_num + 1}/{total_clicks} 시작 ---")
        
        search_automation = CoupangSearchAutomation()
        try:
            try:
                search_success = search_automation.search_product_by_url(keyword)
            except WebDriverException as e:
                if "net::ERR_INTERNET_DISCONNECTED" in str(e):
                    print("인터넷 연결이 끊어졌습니다. 네트워크 연결을 확인해주세요.")
                    continue
                else:
                    print(f"검색 중 오류가 발생했습니다: {str(e)}")
                    continue

            if search_success:
                product_finder = CoupangProductFinder(search_automation.get_driver())
                
                # 광고/일반 상품 클릭 결정
                is_ad_click = click_num >= click_count
                print(f"현재 클릭 유형: {'광고' if is_ad_click else '일반'} 상품")
                
                if product_finder.find_product_by_id(target_product_id, is_ad=is_ad_click):
                    print(f"상품을 찾아 클릭했습니다! (Product ID: {target_product_id})")
                    # 성공 횟수 증가
                    if is_ad_click:
                        detail_ad_success += 1
                    else:
                        detail_success += 1
                    time.sleep(5)
                else:
                    print(f"{'광고' if is_ad_click else '일반'} 상품을 찾지 못했습니다.")
            else:
                print("검색에 실패했습니다.")
                
        finally:
            search_automation.close()
            time.sleep(3)  # 다음 시도 전 대기
            
        # 모든 클릭 끝난 후 IP 변경 체크
        if should_change_ip == 'change_ip_ok' and click_num == total_clicks - 1:
            print("\n=== 모든 클릭 완료, IP 변경 시도 ===")
            if not change_ip():
                print("IP 변경 실패")

    return detail_success, detail_ad_success

def update_excel_result(df, index, result, result_click, result_ad_click, detail_success=0, detail_ad_success=0):
    """엑셀 파일에 결과 업데이트"""
    try:
        df.at[index, 'result'] = result
        df.at[index, 'result_click'] = result_click
        df.at[index, 'result_ad_click'] = result_ad_click
        df.at[index, 'detail_page'] = detail_success
        df.at[index, 'detail_ad_page'] = detail_ad_success
        df.to_excel('coupang_click.xlsx', index=False)
        print(f"결과 저장 완료: result={result}, result_click={result_click}, result_ad_click={result_ad_click}")
        print(f"상세 페이지 성공: 일반={detail_success}, 광고={detail_ad_success}")
        return True
    except Exception as e:
        print(f"결과 저장 중 오류 발생: {str(e)}")
        return False

def select_initial_location_mode():
    """초기 위치 정보 설정 메뉴"""
    print("\n=== 초기 위치 정보 설정 ===")
    print("1. 모든 위치 서비스 끄기")
    print("2. 모바일 위치 서비스만 끄기")
    print("3. 모바일 위치 서비스 켜기")
    print("4. 웹 위치 서비스 끄기")
    print("5. 웹 위치 서비스 켜기")
    print("6. 위치 설정 건너뛰기")
    print("7. 모든 위치 서비스 끄고 상태 저장 후 바로 시작")
    print("8. 모든 위치 서비스 켜고 상태 저장 후 바로 시작")
    
    try:
        choice = input("\n선택하세요 (1-8): ").strip()
        
        mode_map = {
            '1': 'test_location_mode_off',
            '2': 'test_location_mode_mobileoff',
            '3': 'test_location_mode_mobileon',
            '4': 'test_location_mode_weboff',
            '5': 'test_location_mode_webon',
            '6': 'skip',
            '7': 'save_all_off',
            '8': 'save_all_on'
        }
        
        if choice in mode_map:
            selected_mode = mode_map[choice]
            
            if selected_mode == 'skip':
                print("위치 설정을 건너뜁니다.")
                return True
                
            elif selected_mode == 'save_all_off':
                print("\n모든 위치 서비스를 끄고 상태를 저장합니다...")
                os.system("adb shell settings put secure location_mode 0")
                # 상태 저장
                with open('location_state.txt', 'w') as f:
                    f.write('all_off')
                print("위치 서비스가 비활성화되고 상태가 저장되었습니다.")
                return True
                
            elif selected_mode == 'save_all_on':
                print("\n모든 위치 서비스를 켜고 상태를 저장합니다...")
                os.system("adb shell settings put secure location_mode 3")
                # 상태 저장
                with open('location_state.txt', 'w') as f:
                    f.write('all_on')
                print("위치 서비스가 활성화되고 상태가 저장되었습니다.")
                return True
                
            else:
                print(f"\n선택된 모드: {selected_mode}")
                if toggle_location_service(selected_mode):
                    print("\n위치 설정이 완료되었습니다.")
                    print("1분 대기합니다. 대기 중 다음 작업을 선택할 수 있습니다:")
                    print("1. 대기 시간 스킵")
                    print("2. 위치 설정 다시하기")
                    print("3. 그대로 대기")
                    
                    start_time = time.time()
                    while time.time() - start_time < 60:  # 1분 대기
                        remaining = int(60 - (time.time() - start_time))
                        print(f"\r남은 시간: {remaining}초... (1-3 중 선택하세요)", end='')
                        
                        if msvcrt.kbhit():  # 키 입력 확인
                            key = msvcrt.getch().decode()
                            if key == '1':
                                print("\n대기를 스킵합니다.")
                                return True
                            elif key == '2':
                                print("\n위치 설정을 다시 시작합니다.")
                                return select_initial_location_mode()
                            elif key == '3':
                                print("\n남은 시간동안 대기합니다.")
                        
                        time.sleep(1)
                    
                    print("\n대기 완료")
                    return True
        else:
            print("잘못된 선택입니다.")
            return False
            
    except Exception as e:
        print(f"위치 설정 선택 중 오류 발생: {str(e)}")
        return False

def load_saved_location_state():
    """저장된 위치 서비스 상태 확인"""
    try:
        if os.path.exists('location_state.txt'):
            with open('location_state.txt', 'r') as f:
                state = f.read().strip()
                print(f"저장된 위치 서비스 상태: {state}")
                return state
        return None
    except:
        return None

def save_last_ip(ip):
    """마지막 IP 주소 저장"""
    try:
        with open('last_ip.txt', 'w') as f:
            f.write(ip)
    except Exception as e:
        print(f"IP 저장 중 오류: {e}")

def get_last_ip():
    """저장된 마지막 IP 주소 읽기"""
    try:
        if os.path.exists('last_ip.txt'):
            with open('last_ip.txt', 'r') as f:
                return f.read().strip()
    except Exception as e:
        print(f"저장된 IP 읽기 오류: {e}")
    return None

def main():
    try:
        # 초기 IP 확인
        current_ip = get_smartphone_ip()
        print(f"\n=== 프로그램 시작 ===")
        print(f"현재 IP: {current_ip}")
        
        # 이전 IP와 비교
        last_ip = get_last_ip()
        if last_ip and last_ip == current_ip:
            print("이전 실행과 동일한 IP가 감지되었습니다.")
            print("IP 변경을 시도합니다...")
            
            if not change_ip():
                print("IP 변경 실패. 프로그램을 종료합니다.")
                return
            
            # 변경된 IP 확인
            new_ip = get_smartphone_ip()
            print(f"변경된 IP: {new_ip}")
            
            if new_ip == current_ip:
                print("IP 변경 실패. 프로그램을 종료합니다.")
                return
            
            current_ip = new_ip
        
        # 현재 IP 저장
        save_last_ip(current_ip)
        
        # 저장된 위치 상태 확인
        saved_state = load_saved_location_state()
        if saved_state:
            print(f"\n저장된 위치 서비스 상태를 적용합니다: {saved_state}")
            if saved_state == 'all_off':
                os.system("adb shell settings put secure location_mode 0")
            elif saved_state == 'all_on':
                os.system("adb shell settings put secure location_mode 3")
        else:
            # 초기 위치 설정 메뉴
            if not select_initial_location_mode():
                print("초기 위치 설정 실패. 프로그램을 종료합니다.")
                return

        # 엑셀 파일 읽기
        try:
            df = pd.read_excel('coupang_click.xlsx')
            print("\n=== 엑셀 파일 읽기 성공 ===")
            print("현재 엑셀 파일의 컬럼:", df.columns.tolist())
        except Exception as e:
            print(f"엑셀 파일을 읽는 중 오류가 발생했습니다: {e}")
            return

        # 컬럼명 공백 제거 및 소문자 변환
        df.columns = df.columns.str.strip().str.lower()
        
        # 필수 컬럼 확인
        required_columns = ['number', 'keyword', 'target_product_id', 'click', 'ad click', 
                          'change_ip', 'location_off', 'result', 'result_click', 'result_ad_click']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"엑셀 파일에 필수 컬럼이 없습니다: {', '.join(missing_columns)}")
            return

        # 데이터 처리
        df = df.sort_values('number')
        for index, row in df.iterrows():
            if row['number'] == 0:  # 초기 설정 행은 건너뛰기
                continue
                
            print(f"\n=== 처리 중인 항목 {row['number']} ===")
            try:
                # 상품 처리 및 결과 받기
                detail_success, detail_ad_success = process_product(
                    keyword=str(row['keyword']),
                    target_product_id=str(row['target_product_id']),
                    click_count=int(row['click']),
                    ad_click_count=int(row['ad click']),
                    should_change_ip=str(row['change_ip']),
                    location_mode=str(row['location_off'])
                )
                
                # 결과 저장
                result = 'ok' if (detail_success > 0 or detail_ad_success > 0) else 'nok'
                result_click = 'ok' if detail_success > 0 else 'nok'
                result_ad_click = 'ok' if detail_ad_success > 0 else 'nok'
                
                update_excel_result(
                    df, index, result, result_click, result_ad_click,
                    detail_success=detail_success,
                    detail_ad_success=detail_ad_success
                )
                
            except Exception as e:
                print(f"처리 중 오류 발생: {str(e)}")
                update_excel_result(df, index, 'nok', 'nok', 'nok', 0, 0)
                continue
            
    except Exception as e:
        print(f"프로그램 실행 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    main() 