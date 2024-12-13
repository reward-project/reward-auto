from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import requests
import json
import os

class DepositStatus(Enum):
    PENDING = "대기중"
    CONFIRMED = "입금확인"
    COMPLETED = "처리완료"
    CANCELLED = "취소됨"

@dataclass
class BankAccount:
    bank_name: str
    account_number: str
    account_holder: str
    description: str = ""

@dataclass
class DepositRequest:
    amount: int
    depositor_name: str
    bank_account: BankAccount
    memo: str
    request_date: datetime
    status: DepositStatus = DepositStatus.PENDING
    reference_id: str = ""

class DepositRequestManager:
    def __init__(self):
        self.webhook_url = os.getenv('SLACK_WEBHOOK_URL')  # Slack 웹훅 URL
        self.bank_accounts = [
            BankAccount(
                bank_name="신한은행",
                account_number="110-123-456789",
                account_holder="(주)회사명",
                description="기본 입금계좌"
            ),
            BankAccount(
                bank_name="국민은행",
                account_number="123-45-6789-012",
                account_holder="(주)회사명",
                description="별도 입금계좌"
            )
        ]

    def create_deposit_request(self, amount: int, depositor_name: str, bank_account: BankAccount, memo: str = "") -> DepositRequest:
        """무통장 입금 요청 생성"""
        request = DepositRequest(
            amount=amount,
            depositor_name=depositor_name,
            bank_account=bank_account,
            memo=memo,
            request_date=datetime.now(),
            reference_id=self._generate_reference_id()
        )
        
        # 관리자에게 알림
        self._notify_admin(request)
        
        return request

    def _generate_reference_id(self) -> str:
        """고유 참조번호 생성"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return f"DEP{timestamp}"

    def _notify_admin(self, request: DepositRequest):
        """Slack으로 관리자에게 알림"""
        if not self.webhook_url:
            return

        message = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🔔 새로운 무통장입금 요청"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*참조번호:*\n{request.reference_id}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*입금자명:*\n{request.depositor_name}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*입금금액:*\n{format(request.amount, ',')}원"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*입금계좌:*\n{request.bank_account.bank_name}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*계좌번호:*\n{request.bank_account.account_number}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*요청시간:*\n{request.request_date.strftime('%Y-%m-%d %H:%M:%S')}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*메모:*\n{request.memo if request.memo else '없음'}"
                    }
                }
            ]
        }

        try:
            response = requests.post(
                self.webhook_url,
                data=json.dumps(message),
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
        except Exception as e:
            print(f"Slack 알림 전송 실패: {str(e)}")

    def update_status(self, reference_id: str, new_status: DepositStatus):
        """입금 상태 업데이트"""
        # DB 업데이트 로직
        pass

    def get_deposit_request(self, reference_id: str) -> DepositRequest:
        """입금 요청 조회"""
        # DB 조회 로직
        pass

    def list_pending_requests(self) -> list[DepositRequest]:
        """대기중인 입금 요청 목록 조회"""
        # DB 조회 로직
        pass 