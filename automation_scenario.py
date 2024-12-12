from mobile_automation import MobileAutomation

class RewardAutomation(MobileAutomation):
    def run_scenario(self):
        # 시나리오 실행
        steps = [
            self.step_1,
            self.step_2,
            # 추가 단계들...
        ]
        
        for step in steps:
            if not self.execute_step(step):
                print(f"단계 실패: {step.__name__}")
                return False
        return True

    def step_1(self):
        """첫 번째 단계 구현"""
        return self.find_and_click_element("로그인_버튼")

    def step_2(self):
        """두 번째 단계 구현"""
        return self.find_and_click_element("메뉴_버튼")

# 실행
if __name__ == "__main__":
    automation = RewardAutomation()
    automation.run_scenario() 