from search_automation import CoupangSearchAutomation
from product_finder import CoupangProductFinder
import logging
from selenium.common.exceptions import WebDriverException
import os
import time
import subprocess

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
        print("IP 변경을 위해 30초 대기 중...")
        time.sleep(30)
        
        print("셀룰러 데이터 켜기...")
        os.system("adb shell svc data enable")
        print("네트워크 재연결 및 새 IP 할당을 위해 60초 대기 중...")
        time.sleep(60)
        
        # 연결 상태 확인
        print("네트워크 연결 확인 중...")
        for _ in range(6):
            data_enabled = os.popen("adb shell settings get global mobile_data").read().strip()
            if data_enabled == "1":
                test_result = os.popen('adb shell ping -c 1 8.8.8.8').read()
                if "1 packets transmitted" in test_result:
                    print("셀룰러 데이터 연결 완료")
                    time.sleep(5)
                    return True
            print("연결 대기 중...")
            time.sleep(5)
        
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

def main():
    # IP 변경 시도
    if not change_ip():
        print("IP 변경에 실패했습니다. 프로그램을 종료합니다.")
        return

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