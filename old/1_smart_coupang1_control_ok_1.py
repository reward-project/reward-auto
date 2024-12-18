#conda activate sc3_10
import os
import time
import subprocess

def toggle_airplane_mode():
    """비행기모드 켜고 끄기"""
    print("비행기모드 켜기...")
    os.system("adb shell settings put global airplane_mode_on 1")
    os.system("adb shell am broadcast -a android.intent.action.AIRPLANE_MODE --ez state true")
    print("IP 변경을 위해 30초 대기 중...")
    time.sleep(30)  # 비행기모드 30초 유지
    
    print("비행기모드 끄기...")
    os.system("adb shell settings put global airplane_mode_on 0")
    os.system("adb shell am broadcast -a android.intent.action.AIRPLANE_MODE --ez state false")
    print("네트워크 재연결 및 새 IP 할당을 위해 60초 대기 중...")
    time.sleep(60)  # 네트워크 재연결 및 새 IP 할당 대기

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
                # 실제 인터넷 연결 테스트
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

def change_ip_address(method='airplane'):
    """IP 변경 방식 선택
    Args:
        method (str): 'airplane' 또는 'cellular' 선택
    """
    if method == 'airplane':
        print("\n비행기모드를 사용하여 IP 변경 중...")
        toggle_airplane_mode()
    else:
        print("\n셀룰러 데��터를 사용하여 IP 변경 중...")
        toggle_cellular_data()

def set_screen_always_on():
    """화면 항상 켜지도록 설정"""
    print("화면 항상 켜지도록 설정...")
    os.system("adb shell settings put system screen_off_timeout 2147483647")
    result = os.popen("adb shell settings get system screen_off_timeout").read().strip()
    if result == "2147483647":
        print("화면 대기 시간이 성공적으로 설정되었습니다.")
    else:
        print(f"설정 실패: 현재 화면 대기 시간은 {result}입니다.")

def get_smartphone_ip():
    """스마트폰의 공인 IP 주소 확인"""
    try:
        # 여러 IP 확인 서비스를 시도
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
                # IP 주소 형식 검증
                import re
                if re.match(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$', ip_address):
                    return ip_address
        
        return "IP 주소를 찾을 수 없습니다."
    except Exception as e:
        return f"IP 확인 오류: {e}"

def save_ip_to_file(ip):
    """IP 주소를 파일에 저장"""
    try:
        with open('smartphone_ip.txt', 'a', encoding='utf-8') as f:
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"{timestamp}: {ip}\n")
        print(f"IP 주소가 파일에 저장되었습니다: {ip}")
    except Exception as e:
        print(f"파일 저장 오류: {e}")

def open_url_with_chrome(url):
    """Chrome 브라우저에서 URL 열기"""
    try:
        command = f'adb shell am start -n com.android.chrome/com.google.android.apps.chrome.Main -a android.intent.action.VIEW -d "{url}"'
        os.system(command)
        print(f"URL 열림 (Chrome): {url}")
        time.sleep(5)  # 브라우저 로딩 대기
    except Exception as e:
        print(f"브라우저 실행 오류: {e}")

def test_ip_changes():
    """IP 변경 테스트 10회 실행"""
    print("\nIP 변경 테스트 시작 (10회 반복)")
    previous_ip = None
    changes = 0
    
    for i in range(10):
        print(f"\n=== {i+1}번째 시도 ===")
        
        # 현재 IP 확인
        print("현재 IP 확인 중...")
        current_ip = get_smartphone_ip()
        print(f"시도 전 IP: {current_ip}")
        
        # 셀룰러 데이터로 IP 변경
        print("\n셀룰러 데이터 전환 시도...")
        if not toggle_cellular_data():
            print("셀룰러 데이터 전환 실패. 다음 시도로 넘어갑니다.")
            time.sleep(30)
            continue
        
        # 새 IP 확인 및 저장
        print("새 IP 확인 중...")
        new_ip = get_smartphone_ip()
        print(f"변경 후 IP: {new_ip}")
        save_ip_to_file(new_ip)
        
        # IP 변경 여부 확인
        if previous_ip and previous_ip != new_ip and "찾을 수 없습니다" not in new_ip:
            changes += 1
            print(f"IP 변경 감지: {previous_ip} -> {new_ip}")
        else:
            print("IP가 변경되지 않았습니다.")
        
        previous_ip = new_ip
        
        print("다음 시도까지 30초 대기...")
        time.sleep(30)
    
    print(f"\n테스트 완료!")
    print(f"총 시도: 10회")
    print(f"IP 변경 횟수: {changes}회")
    if changes > 0:
        print(f"변경 성공률: {(changes/9)*100:.1f}%")

def main():
    """메인 실행 함수"""
    try:
        # IP 변경 테스트 실행
        test_ip_changes()
        
    except Exception as e:
        print(f"오류 발생: {str(e)}")

if __name__ == "__main__":
    main()