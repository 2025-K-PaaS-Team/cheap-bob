import { CommonBtn, CommonModal, CommonProfile } from "@components/common";
import {
  AllergyList,
  MenuList,
  NutritionList,
  orderStatus,
  ToppingList,
} from "@constant";
import type { OrderBaseType } from "@interface";
import { completePickup, deleteOrder, getCurrentOrders } from "@services";
import { formatErrMsg, getTitleByKey } from "@utils";
import { useRef, useState } from "react";
import { QrReader } from "react-qr-reader";
import { OrderStatus } from "./OrderStatus";
import { OrderInfo } from "./OrderInfo";
import { OrderBtnRow } from "./OrderBtnRow";

interface OrderCardProps {
  orders: OrderBaseType[];
  isAll?: boolean;
  onRefresh?: () => void | Promise<void>;
}

export const OrderCard = ({
  orders,
  isAll = false,
  onRefresh,
}: OrderCardProps) => {
  const [qrReaderOpen, setQrReaderOpen] = useState(false);
  const [currentOrderForQr, setCurrentOrderForQr] =
    useState<OrderBaseType | null>(null);

  const [showModal, setShowModal] = useState(false);
  const [modalMsg, setModalMsg] = useState("");

  const [showCancelModal, setShowCancelModal] = useState(false);
  const [paymentIdToCancel, setPaymentIdToCancel] = useState<string | null>(
    null
  );
  const [isProcessing, setIsProcessing] = useState(false);

  const [showCancelReason, setShowCancelReason] = useState(false);
  const [cancelReason, setCancelReason] = useState("");

  const [showProfile, setShowProfile] = useState(false);
  const [selectedProfile, setSelectedProfile] = useState<OrderBaseType | null>(
    null
  );

  const scanLockRef = useRef(false);
  const inflightRef = useRef<Set<string>>(new Set());
  const processedRef = useRef<Set<string>>(new Set());

  const [processingPaymentId, setProcessingPaymentId] = useState<string | null>(
    null
  );

  const handleCompletePickup = async (paymentId: string, qrData: string) => {
    if (
      processedRef.current.has(paymentId) ||
      inflightRef.current.has(paymentId)
    )
      return;

    processedRef.current.add(paymentId);
    inflightRef.current.add(paymentId);
    setProcessingPaymentId(paymentId);

    try {
      await completePickup(paymentId, { qr_data: qrData /*, axiosRetry: 0*/ });
      setModalMsg("픽업이 완료되었습니다!");
      setShowModal(true);
      await onRefresh?.();
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    } finally {
      inflightRef.current.delete(paymentId);
      setProcessingPaymentId((cur) => (cur === paymentId ? null : cur));
    }
  };

  const handleClickCancelBtn = async (paymentId: string) => {
    if (isProcessing) return;
    setIsProcessing(true);

    try {
      await deleteOrder(paymentId);
      getCurrentOrders();
      await onRefresh?.();
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    } finally {
      setIsProcessing(false);
      setShowCancelModal(false);
    }
  };

  const handleClickPickupCompleteBtn = (order: OrderBaseType) => {
    if (
      processedRef.current.has(order.payment_id) ||
      inflightRef.current.has(order.payment_id)
    )
      return;
    setCurrentOrderForQr(order);
    scanLockRef.current = false;
    setQrReaderOpen(true);
  };

  const timeKeyMap: Record<string, keyof OrderBaseType> = {
    reservation: "reservation_at",
    accept: "accepted_at",
    complete: "completed_at",
    cancel: "canceled_at",
  };

  const handleOpenProfile = (order: OrderBaseType) => {
    setSelectedProfile(order);
    setShowProfile(true);
  };

  return (
    <>
      {orders.map((order, idx) => {
        const timeStampKey = timeKeyMap[order.status] ?? "reservation_at";
        const timeStampValue = order[timeStampKey as keyof OrderBaseType] as
          | string
          | number;
        const orderTime = new Date(timeStampValue)
          .toLocaleString("ko-KR", {
            timeZone: "Asia/Seoul",
            year: "numeric",
            month: "2-digit",
            day: "2-digit",
            hour: "2-digit",
            minute: "2-digit",
            hour12: false,
          })
          .replace(/\.\s/g, ".")
          .replace(/\.$/, "")
          .replace(/\.(\d{2}:\d{2})$/, " $1");

        const orderState =
          orderStatus[order.status as keyof typeof orderStatus] ?? "";

        const disabledPickup =
          order.status !== "accept" ||
          inflightRef.current.has(order.payment_id) ||
          processedRef.current.has(order.payment_id) ||
          processingPaymentId === order.payment_id;

        return (
          <div className="m-[20px]" key={`${order.payment_id}-${idx}`}>
            <div className="shadow p-[20px] flex flex-col gap-y-[22px]">
              {/* first row */}
              <OrderStatus
                order={order}
                orderState={orderState}
                handleOpenProfile={handleOpenProfile}
                orderTime={orderTime}
              />

              {/* second row */}
              <OrderInfo order={order} isAll={isAll} />

              {/* button row */}
              <OrderBtnRow
                order={order}
                handleClickPickupCompleteBtn={handleClickPickupCompleteBtn}
                setShowCancelModal={setShowCancelModal}
                setShowCancelReason={setShowCancelReason}
                setPaymentIdToCancel={setPaymentIdToCancel}
                processedRef={processedRef}
                processingPaymentId={processingPaymentId}
                disabledPickup={disabledPickup}
                setCancelReason={setCancelReason}
              />
            </div>
          </div>
        );
      })}

      {/* QR Reader Modal */}
      {qrReaderOpen && currentOrderForQr && (
        <CommonModal>
          <div className="flex flex-col gap-y-[20px]">
            <div className="bodyFont text-center">
              점주가 보여주는 QR코드를 찍으면 <br />
              <span className="font-bold">픽업이 완료</span>됩니다.
            </div>

            <QrReader
              key={currentOrderForQr.payment_id}
              constraints={{ facingMode: "environment" }}
              scanDelay={1200}
              onResult={(result) => {
                if (!result || scanLockRef.current) return;

                const text = result?.getText?.();
                const orderId = currentOrderForQr?.payment_id;

                if (!text || !orderId) return;
                if (
                  processedRef.current.has(orderId) ||
                  inflightRef.current.has(orderId)
                )
                  return;

                scanLockRef.current = true;
                setQrReaderOpen(false);
                setCurrentOrderForQr(null);

                handleCompletePickup(orderId, text).finally(() => {
                  setTimeout(() => {
                    scanLockRef.current = false;
                  }, 500);
                });
              }}
              videoStyle={{ width: "100%", height: "100%", objectFit: "cover" }}
            />

            <CommonBtn
              label="취소"
              notBottom
              category="white"
              onClick={() => {
                setQrReaderOpen(false);
                setCurrentOrderForQr(null);
                scanLockRef.current = false;
              }}
            />
          </div>
        </CommonModal>
      )}

      {showCancelModal && (
        <CommonModal desc="">
          <div className="flex flex-col text-start gap-y-[20px]">
            <h3>주문을 취소하시겠어요?</h3>
            <div className="bodyFont">
              사장님이 픽업 확정하기 전까지 취소할 수 있어요. <br />
              3~5일 내에 환불이 진행돼요.
            </div>
            <div className="grid grid-cols-2 btnFont text-center">
              <button
                disabled={isProcessing}
                className="text-sub-red"
                onClick={() =>
                  paymentIdToCancel && handleClickCancelBtn(paymentIdToCancel)
                }
              >
                {isProcessing ? "처리 중..." : "주문 취소"}
              </button>
              <div
                className="text-custom-black"
                onClick={() => setShowCancelModal(false)}
              >
                뒤로 가기
              </div>
            </div>
          </div>
        </CommonModal>
      )}

      {showCancelReason && (
        <CommonModal
          confirmLabel="확인"
          onConfirmClick={() => setShowCancelReason(false)}
          category="green"
        >
          <div className="font-bold">주문취소 사유</div>
          {cancelReason}
        </CommonModal>
      )}

      {showModal && (
        <CommonModal
          desc={modalMsg}
          confirmLabel="확인"
          onConfirmClick={() => setShowModal(false)}
          category="green"
        />
      )}

      {showProfile && selectedProfile && (
        <CommonProfile
          nickname={selectedProfile.customer_nickname}
          phone={selectedProfile.customer_phone_number}
          nutrition_goal={selectedProfile.nutrition_types?.map((n) =>
            getTitleByKey(n, NutritionList)
          )}
          prefer_menu={selectedProfile.preferred_menus?.map((m) =>
            getTitleByKey(m, MenuList)
          )}
          prefer_topping={selectedProfile.topping_types?.map((t) =>
            getTitleByKey(t, ToppingList)
          )}
          allergy={selectedProfile.allergies?.map((a) =>
            getTitleByKey(a, AllergyList)
          )}
          onCancelClick={() => setShowProfile(false)}
          datetime={selectedProfile.reservation_at}
          qty={selectedProfile.quantity}
        />
      )}
    </>
  );
};
