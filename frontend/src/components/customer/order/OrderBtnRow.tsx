import { CommonBtn } from "@components/common";
import type { OrderBaseType } from "@interface";

interface OrderBtnRowType {
  order: OrderBaseType;
  handleClickPickupCompleteBtn: (order: OrderBaseType) => void;
  setShowCancelModal: (res: boolean) => void;
  setPaymentIdToCancel: (res: string) => void;
  processedRef: React.RefObject<Set<string>>;
  processingPaymentId: string | null;
  disabledPickup: boolean;
  setCancelReason: (res: string) => void;
  setShowCancelReason: (res: boolean) => void;
}

export const OrderBtnRow = ({
  order,
  handleClickPickupCompleteBtn,
  setPaymentIdToCancel,
  setShowCancelModal,
  processedRef,
  processingPaymentId,
  disabledPickup,
  setCancelReason,
  setShowCancelReason,
}: OrderBtnRowType) => {
  return (
    <div className="flex flex-col gap-5">
      {order.status === "reservation" && (
        <CommonBtn
          label="주문 취소"
          category="red"
          notBottom
          className="w-full"
          onClick={() => {
            setPaymentIdToCancel(order.payment_id);
            setShowCancelModal(true);
          }}
        />
      )}

      {order.status === "accept" && (
        <CommonBtn
          label={
            processingPaymentId === order.payment_id
              ? "처리 중..."
              : processedRef.current.has(order.payment_id)
              ? "처리됨"
              : "QR 인증하고 픽업하기"
          }
          category="green"
          notBottom
          className={`w-full ${
            disabledPickup ? "opacity-60 pointer-events-none" : ""
          }`}
          onClick={() => handleClickPickupCompleteBtn(order)}
        />
      )}

      {order.status === "cancel" && (
        <CommonBtn
          label="취소사유 보기"
          category="red"
          notBottom
          className="w-full"
          onClick={() => {
            setCancelReason(order.cancel_reason);
            setShowCancelReason(true);
          }}
        />
      )}
    </div>
  );
};
