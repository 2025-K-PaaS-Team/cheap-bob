import enum

class OrderStatus(enum.Enum):
    reservation = "reservation" # 예약 중
    accept = "accept" # 주문 수락
    pickup = "pickup" # 픽업 준비 완료
    complete = "complete" # 픽업 완료
    cancel = "cancel" # 취소