def deep_check_webview(self):
    try:
        # 1. 페이지 소스에서 WebView 문자열 검색
        page_source = self.driver.page_source
        if 'WebView' in page_source:
            print("페이지 소스에서 WebView 발견")
            
        # 2. 다른 WebView 클래스명으로 검색
        alternate_webviews = [
            'android.webkit.WebView',
            'com.android.webview.WebView',
            'com.google.android.webview.WebView'
        ]
        
        for webview_class in alternate_webviews:
            elements = self.driver.find_elements(AppiumBy.CLASS_NAME, webview_class)
            if elements:
                print(f"발견된 WebView: {webview_class}")
                
        # 3. 컨텍스트 상세 정보
        contexts = self.driver.contexts
        print(f"모든 컨텍스트: {contexts}")
        
        # 4. 크롬 디버거 상태 확인
        chrome_status = self.driver.execute_script('chrome.send("inspect:chrome")')
        print(f"크롬 디버거 상태: {chrome_status}")
        
    except Exception as e:
        print(f"상세 검사 중 에러: {str(e)}") 