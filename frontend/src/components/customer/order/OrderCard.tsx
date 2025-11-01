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
import { useState } from "react";
import { QrReader } from "react-qr-reader";

interface OrderCardProps {
  orders: OrderBaseType[];
  isAll?: boolean;
  onRefresh?: () => void | Promise<void>;
}

const OrderCard = ({ orders, isAll = false, onRefresh }: OrderCardProps) => {
  const [qrReaderOpen, setQrReaderOpen] = useState(false);
  const [currentOrderForQr, setCurrentOrderForQr] =
    useState<OrderBaseType | null>(null);
  const [scanned, setScanned] = useState(false);

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

  const getColorByStatus = (status: string) => {
    if (status === "reservation" || status === "cancel") {
      return "bg-[#E7E7E7]";
    }
    return "bg-main-pale text-main-deep border-main-deep border";
  };

  const handleCompletePickup = async (paymentId: string, qrData: string) => {
    try {
      await completePickup(paymentId, { qr_data: qrData });
      setModalMsg("픽업이 완료되었습니다!");
      setShowModal(true);
      setQrReaderOpen(false);
      setCurrentOrderForQr(null);
      setScanned(false);
    } catch (err: any) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    } finally {
      await onRefresh?.();
    }
  };

  const handleClickCancelBtn = async (paymentId: string) => {
    if (isProcessing) return;
    setIsProcessing(true);

    try {
      await deleteOrder(paymentId);
      getCurrentOrders();
      await onRefresh?.();
    } catch (err: any) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    } finally {
      setIsProcessing(false);
      setShowCancelModal(false);
    }
  };

  const handleClickPickupCompleteBtn = (order: OrderBaseType) => {
    setCurrentOrderForQr(order);
    setQrReaderOpen(true);
    setScanned(false);
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

        return (
          <div className="m-[20px]" key={idx}>
            <div className="shadow p-[20px] flex flex-col gap-y-[22px]">
              {/* first row */}
              <div className="flex flex-row justify-between">
                <div
                  className={`px-[16px] py-[8px] rounded tagFont ${getColorByStatus(
                    order.status
                  )}`}
                >
                  {orderState}
                </div>
                <div
                  onClick={() => handleOpenProfile(order)}
                  className="tagFont font-bold flex flex-row gap-x-[3px] items-center justify-center"
                >
                  <div>{orderTime}</div>
                  <div>·</div>
                  <div>{order.quantity}개</div>
                  <img src="/icon/next.svg" alt="nextIcon" width="14px" />
                </div>
              </div>

              {/* second row */}
              <div className="grid grid-cols-5 gap-x-[11px]">
                <img
                  src={order.main_image_url}
                  alt="storeImg"
                  className="rounded object-cover col-span-2"
                />
                <div className="col-span-3 flex flex-col">
                  <div className="bodyFont font-bold pb-[8px]">
                    {order.store_name}
                  </div>
                  <div className="tagFont pb-[22px]">
                    {Number(order.total_amount).toLocaleString()}원
                  </div>
                  {isAll ? (
                    <div className="font-bold tagFont">
                      {order.product_name}
                    </div>
                  ) : (
                    <div className="font-bold tagFont">
                      픽업: {order.pickup_start_time} ~ {order.pickup_end_time}
                    </div>
                  )}
                </div>
              </div>

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
                    label="QR 인증하고 픽업하기"
                    category="green"
                    notBottom
                    className="w-full"
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
            </div>
          </div>
        );
      })}

      {qrReaderOpen && currentOrderForQr && (
        <CommonModal>
          <div className="flex flex-col gap-y-[20px]">
            <div className="bodyFont text-center">
              점주가 보여주는 QR코드를 찍으면 <br />
              <span className="font-bold">픽업이 완료</span>됩니다.
            </div>
            <QrReader
              constraints={{ facingMode: "environment" }}
              onResult={(result) => {
                if (result?.getText() && !scanned) {
                  setScanned(true);
                  handleCompletePickup(
                    currentOrderForQr.payment_id,
                    result.getText()
                  );
                }
              }}
              videoStyle={{ width: "100%", height: "100%", objectFit: "cover" }}
            />
            <CommonBtn
              label="취소"
              notBottom
              category="white"
              onClick={() => setQrReaderOpen(false)}
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

export default OrderCard;
