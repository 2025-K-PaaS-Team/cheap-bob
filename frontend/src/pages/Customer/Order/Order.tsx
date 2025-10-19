import { CommonBtn, CommonModal } from "@components/common";
import { orderStatus } from "@constant";
import type { OrderBaseType } from "@interface/common/types";
import { completePickup, deleteOrder, getCurrentOrders } from "@services";
import { formatDate, formatErrMsg } from "@utils";
import { useEffect, useRef, useState } from "react";
import { QrReader } from "react-qr-reader";
import { useNavigate } from "react-router";

const Order = () => {
  const navigate = useNavigate();
  const [orders, setOrders] = useState<OrderBaseType[] | null>(null);
  const [qrReaderOpen, setQrReaderOpen] = useState<Boolean>(false);
  const [paymentIdToComplete, setPaymentIdToComplete] = useState<string | null>(
    null
  );
  const scannedRef = useRef(false);
  const [showModal, setShowModal] = useState<boolean>(false);
  const [showCancelModal, setShowCancelModal] = useState<boolean>(false);

  const [modalMsg, setModalMsg] = useState("");

  const handleGetOrders = async () => {
    try {
      const res = await getCurrentOrders();
      setOrders(res.orders);
    } catch (err: unknown) {
      console.error("get stores fail", err);
    }
  };

  useEffect(() => {
    handleGetOrders();
  }, []);

  if (!orders) {
    return (
      <div className="flex flex-col w-full h-full justify-center items-center">
        <img
          src="/icon/angrySalad.svg"
          alt="saladBowlIcon"
          className="pb-[26px] w-[116px]"
        />
        <div className="text-[20px] pb-[17px] font-bold">
          주문내역이 비어있어요.
        </div>
        <div className="text-[12px] font-base pb-[46px]">
          다양한 랜덤팩을 주문하고 픽업해보세요.
        </div>
        <CommonBtn
          label="실시간 랜덤팩 보러가기"
          notBottom={true}
          onClick={() => navigate("/c/stores")}
        />
      </div>
    );
  }

  const handleCompletePickup = async (paymentId: string, qrData: string) => {
    try {
      await completePickup(paymentId, { qr_data: qrData });
    } catch (err: any) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    } finally {
      setQrReaderOpen(false);
      setPaymentIdToComplete(null);
    }
  };

  const handleClickCancelBtn = async (paymentId: string) => {
    try {
      await deleteOrder(paymentId);
      setShowCancelModal(false);
      getCurrentOrders();
    } catch (err: any) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    }
  };

  const handleClickPickupCompleteBtn = (paymentId: string) => {
    setQrReaderOpen(true);
    setPaymentIdToComplete(paymentId);
  };

  const getColorByStautus = (status: string) => {
    if (status == "reservation") {
      return "bg-[#E7E7E7]";
    } else {
      return "bg-main-pale text-main-deep border-main-deep border";
    }
  };

  return (
    <>
      {orders.map((order, idx) => {
        const timeStampKey = `${order.status.toLowerCase()}_at`;
        const timeStampValue = order[timeStampKey];
        const orderTime = formatDate(timeStampValue)
          ?.slice(0, 10)
          .replaceAll("-", ".");
        const orderState = orderStatus[order.status];

        return (
          <div className="m-[20px]">
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
                  src=""
                  alt="storeImg"
                  className="bg-main-deep rounded object-cover col-span-2"
                />

                <div className="col-span-3 flex flex-col">
                  <div className="bodyFont font-bold pb-[8px]">
                    {order.store_name}
                  </div>
                  <div className="tagFont pb-[22px]">
                    {order.total_amount}원
                  </div>
                  <div className="font-bold tagFont">
                    픽업: {order.pickup_ready_at}
                  </div>
                </div>
              </div>

              <div className="flex flex-col gap-5">
                {order.status == "reservation" && (
                  <CommonBtn
                    label="주문 취소"
                    category="red"
                    notBottom
                    className="w-full"
                    onClick={() => setShowCancelModal(true)}
                  />
                )}
                {order.status == "accepted" && (
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

                {qrReaderOpen && paymentIdToComplete === order.payment_id && (
                  <div style={{ width: "300px", margin: "auto" }}>
                    <QrReader
                      constraints={{ facingMode: "environment" }}
                      onResult={(result, error) => {
                        if (result && !scannedRef.current) {
                          const data = result?.getText();
                          console.log(result, scannedRef.current);
                          if (data && !scannedRef.current) {
                            scannedRef.current = true;
                            window.alert("qr 코드를 읽었어유");
                            handleCompletePickup(order.payment_id, data);
                          }
                        }
                        // QR 읽는 중 에러가 있어도 무시 (계속 스캔하도록)
                        if (error) console.log("qr error", error);
                      }}
                    />
                  </div>
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
                    <div
                      className="text-sub-red"
                      onClick={() => handleClickCancelBtn(order.payment_id)}
                    >
                      주문 취소
                    </div>
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

export default Order;
