from utils.logger import Logger
import time

class PopupHandler:
    def __init__(self, driver):
        self.driver = driver
        self.logger = Logger('PopupHandler')
        
    def close_all_popups(self):
        """모든 팝업과 배너 닫기"""
        try:
            self.close_bottom_sheet()
            self.close_app_banner()
            self.close_full_banner()
            return True
        except Exception as e:
            self.logger.debug(f"팝업/배너 처리 중 에러: {str(e)}")
            return False
            
    def close_bottom_sheet(self):
        """하단 시트 팝업 닫기"""
        try:
            popup_visible = self.driver.execute_script("""
                const closeBtn = document.querySelector("#bottomSheetBudgeCloseButton");
                return closeBtn && closeBtn.offsetParent !== null;
            """)
            
            if popup_visible:
                self.logger.debug("하단 시트 팝업 발견, 닫기 시도")
                self.driver.execute_script("""
                    document.querySelector("#bottomSheetBudgeCloseButton").click();
                """)
                time.sleep(1)
                return True
            return False
            
        except Exception as e:
            self.logger.debug(f"하단 시트 팝업 처리 중 에러: {str(e)}")
            return False
            
    def close_app_banner(self):
        """앱 설치 배너 닫기"""
        try:
            banner_visible = self.driver.execute_script("""
                const banner = document.querySelector("#BottomAppBanner > div > div > a");
                return banner && banner.offsetParent !== null;
            """)
            
            if banner_visible:
                self.logger.debug("앱 설치 배너 발견, 닫기 시도")
                self.driver.execute_script("""
                    const banner = document.querySelector("#BottomAppBanner > div > div > a");
                    if (banner) {
                        const closeBtn = banner.querySelector('.close') || 
                                       banner.parentElement.querySelector('.close');
                        if (closeBtn) {
                            closeBtn.click();
                        } else {
                            banner.closest('#BottomAppBanner').style.display = 'none';
                        }
                    }
                """)
                time.sleep(1)
                return True
            return False
            
        except Exception as e:
            self.logger.debug(f"앱 설치 배너 처리 중 에러: {str(e)}")
            return False

    def close_full_banner(self):
        """전체 배너 닫기"""
        try:
            banner_visible = self.driver.execute_script("""
                const closeBtn = document.querySelector("#fullBanner > div > div > button");
                return closeBtn && closeBtn.offsetParent !== null;
            """)
            
            if banner_visible:
                self.logger.debug("전체 배너 발견, 닫기 시도")
                self.driver.execute_script("""
                    document.querySelector("#fullBanner > div > div > button").click();
                """)
                time.sleep(1)
                return True
            return False
            
        except Exception as e:
            self.logger.debug(f"전체 배너 처리 중 에러: {str(e)}")
            return False 