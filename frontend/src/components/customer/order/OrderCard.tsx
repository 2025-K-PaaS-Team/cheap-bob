import { CommonBtn, CommonModal } from "@components/common";
import { orderStatus } from "@constant";
import type { OrderBaseType } from "@interface/common/types";
import { completePickup, deleteOrder, getCurrentOrders } from "@services";
import { formatDate, formatErrMsg } from "@utils";
import { useRef, useState } from "react";
import { QrReader } from "react-qr-reader";

interface OrderCardProps {
  orders: OrderBaseType[];
  isAll?: boolean;
  onRefresh?: () => void | Promise<void>;
}

const OrderCard = ({ orders, isAll = false, onRefresh }: OrderCardProps) => {
  const [qrReaderOpen, setQrReaderOpen] = useState<Boolean>(false);
  const [paymentIdToComplete, setPaymentIdToComplete] = useState<string | null>(
    null
  );
  const scannedRef = useRef(false);
  const [showModal, setShowModal] = useState<boolean>(false);
  const [showCancelModal, setShowCancelModal] = useState<boolean>(false);
  const [paymentIdToCancel, setPaymentIdToCancel] = useState<string | null>(
    null
  );
  const [modalMsg, setModalMsg] = useState("");
  const [showCancelReason, setShowCancelReason] = useState<boolean>(false);
  const [cancelReason, setCancelReason] = useState<string>("");

  const [isProcessing, setIsProcessing] = useState<boolean>(false);

  const getColorByStautus = (status: string) => {
    if (status == "reservation" || status == "cancel") {
      return "bg-[#E7E7E7]";
    } else {
      return "bg-main-pale text-main-deep border-main-deep border";
    }
  };
  const handleCompletePickup = async (paymentId: string, qrData: string) => {
    try {
      await completePickup(paymentId, { qr_data: qrData });
      setQrReaderOpen(false);
      setModalMsg("픽업이 완료되었습니다!");
      setShowModal(true);
      await onRefresh?.();
    } catch (err: any) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    } finally {
      setQrReaderOpen(false);
      setPaymentIdToComplete(null);
      scannedRef.current = false;
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

  const handleClickPickupCompleteBtn = (paymentId: string) => {
    setQrReaderOpen(true);
    setPaymentIdToComplete(paymentId);
    scannedRef.current = false;
  };

  const timeKeyMap: Record<string, keyof OrderBaseType> = {
    reservation: "reservation_at",
    accept: "accepted_at",
    complete: "completed_at",
    cancel: "canceled_at",
  };

  return (
    <>
      {orders.map((order, idx) => {
        const timeStampKey = timeKeyMap[order.status] ?? "reservation_at";
        const timeStampValue = order[timeStampKey as keyof OrderBaseType];
        const orderTime = formatDate(timeStampValue)
          ?.slice(0, 10)
          .replaceAll("-", ".");
        const orderState =
          orderStatus[order.status as keyof typeof orderStatus] ?? "";

        return (
          <div className="m-[20px]" key={idx}>
            <div
              key={idx}
              className="shadow p-[20px] flex flex-col gap-y-[22px]"
            >
              {/* first row */}
              <div className="flex flex-row justify-between">
                {/* order status */}
                <div
                  className={`px-[16px] py-[8px] rounded tagFont ${getColorByStautus(
                    order.status
                  )}`}
                >
                  {orderState}
                </div>

                {/* date */}
                <div className="tagFont flex flex-row gap-x-[3px]">
                  <div>{orderTime}</div>
                  <div>·</div>
                  <div>{order.quantity}개</div>
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
                {order.status == "reservation" && (
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
                {order.status == "accept" && (
                  <CommonBtn
                    label="QR 인증하고 픽업하기"
                    category="green"
                    notBottom
                    className="w-full"
                    onClick={() =>
                      handleClickPickupCompleteBtn(order.payment_id)
                    }
                  />
                )}
                {order.status == "cancel" && (
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

                {qrReaderOpen && paymentIdToComplete === order.payment_id && (
                  <CommonModal>
                    <div className="flex flex-col gap-y-[20px]">
                      <div className="bodyFont text-center">
                        점주가 보여주는 QR코드를 찍으면 <br />
                        <span className="font-bold">픽업이 완료</span>됩니다.
                      </div>
                      <QrReader
                        constraints={{ facingMode: "environment" }}
                        onResult={(result) => {
                          if (result && !scannedRef.current) {
                            const data = result?.getText();
                            if (data && !scannedRef.current) {
                              scannedRef.current = true;
                              handleCompletePickup(order.payment_id, data);
                            }
                          }
                        }}
                        videoStyle={{
                          width: "100%",
                          height: "100%",
                          objectFit: "cover",
                        }}
                      />
                      <CommonBtn
                        label="취소"
                        category="white"
                        onClick={() => setQrReaderOpen(false)}
                        notBottom
                        width="w-[300px]"
                        className="border-none text-sub-red"
                      />
                    </div>
                  </CommonModal>
                )}
              </div>
            </div>

            {/* show cancel modal */}
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
                      onClick={() => {
                        if (paymentIdToCancel) {
                          handleClickCancelBtn(paymentIdToCancel);
                        }
                      }}
                    >
                      {isProcessing ? "처리 중..." : "주문 취소"}
                    </button>
                    <div
                      className="text-custom-black"
                      onClick={() => {
                        setShowCancelModal(false);
                        setPaymentIdToCancel(null);
                      }}
                    >
                      뒤로 가기
                    </div>
                  </div>
                </div>
              </CommonModal>
            )}

            {/* show modal */}
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

            {/* show modal */}
            {showModal && (
              <CommonModal
                desc={modalMsg}
                confirmLabel="확인"
                onConfirmClick={() => setShowModal(false)}
                category="green"
              />
            )}
          </div>
        );
      })}
    </>
  );
};

export default OrderCard;
