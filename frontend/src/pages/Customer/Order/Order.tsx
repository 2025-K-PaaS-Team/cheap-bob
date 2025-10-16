import { CommonBtn } from "@components/common";
import { orderStatus } from "@constant";
import type { OrderBaseType } from "@interface/common/types";
import type { OrderDetailResponseType } from "@interface/customer/order";
import {
  completePickup,
  // deleteOrder,
  getOrderDetail,
  getOrders,
} from "@services";
import { formatDate } from "@utils";
import { AxiosError } from "axios";
import { useEffect, useRef, useState } from "react";
import { QrReader } from "react-qr-reader";
import { useNavigate } from "react-router";

const Order = () => {
  const [orders, setOrders] = useState<OrderBaseType[] | null>(null);
  // const [currentOrders, setCurrentOrders] = useState<OrderBaseType[] | null>(
  //   null
  // );
  const [orderDetail, setOrderDetail] =
    useState<OrderDetailResponseType | null>(null);
  const [reason, setReason] = useState<string>("");
  const [qrReaderOpen, setQrReaderOpen] = useState<Boolean>(false);
  const [paymentIdToComplete, setPaymentIdToComplete] = useState<string | null>(
    null
  );
  const scannedRef = useRef(false);
  const isOrder = false;
  const navigate = useNavigate();

  if (!isOrder) {
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

  const handleGetOrders = async () => {
    try {
      const res = await getOrders();
      console.log("주문 목록 가져오기 성공", res);
      setOrders(res.orders);
    } catch (err: unknown) {
      console.error("get stores fail", err);
    }
  };

  // get current orders
  // const handleGetCurrentOrders = async () => {
  //   try {
  //     const res = await getCurrentOrders();
  //     console.log("현재 주문 목록 가져오기 성공", orders);
  //     setCurrentOrders(res.orders);
  //   } catch (err: unknown) {
  //     console.error("get current stores fail");
  //   }
  // };

  useEffect(() => {
    // get orders
    handleGetOrders();
    // get current orders
    // handleGetCurrentOrders();
  }, []);

  if (!orders) {
    return <div>주문 정보를 불러오는 중입니다...</div>;
  }

  const handleGetOrderDetail = async (paymentId: string) => {
    try {
      const res = await getOrderDetail(paymentId);
      console.log("주문 상세 가져오기 성공", res);
      setOrderDetail(res);
    } catch (err: unknown) {
      console.error("get order detail failed", err);
    }
  };

  // const handleDeleteOrder = async (paymentId: string) => {
  //   try {
  //     const res = await deleteOrder(paymentId, {
  //       reason: reason,
  //     });
  //     console.log("결제 취소 성공", res);
  //     window.alert("결제 취소 성공했옹 （づ￣3￣）づ╭❤️～");
  //   } catch (err: any) {
  //     console.error("get order detail failed", err);
  //     window.alert(`결제 취소 실패! ( ⓛ ω ⓛ *) ${err.response.data.detail}`);
  //   }
  // };

  const handleCompletePickup = async (paymentId: string, qrData: string) => {
    try {
      const res = await completePickup(paymentId, { qr_data: qrData });
      console.log("픽업 완료 성공", res);
      window.alert("픽업 완료 성공했옹 （づ￣3￣）づ╭❤️～");
    } catch (err: any) {
      console.error("픽업 완료 실패", err);
      const errorMessage =
        (err instanceof AxiosError && err.response?.data?.detail) ||
        "픽업 완료 실패!";
      window.alert(`픽업 완료 실패! ( ⓛ ω ⓛ *) ${errorMessage}`);
    } finally {
      setQrReaderOpen(false);
      setPaymentIdToComplete(null);
    }
  };

  const handleClickDetailBtn = (paymentId: string) => {
    handleGetOrderDetail(paymentId);
  };

  // const handleClickCancelBtn = (paymentId: string) => {
  //   handleDeleteOrder(paymentId);
  // };

  const handleClickPickupCompleteBtn = (paymentId: string) => {
    setQrReaderOpen(true);
    setPaymentIdToComplete(paymentId);
  };

  if (orders.length === 0) return <div>주문 내역이 없습니다</div>;
  return (
    <>
      <h1>전체 주문 목록</h1>
      {orders.map((order, idx) => {
        const timeStampKey = `${order.status.toLowerCase()}_at`;
        const timeStampValue = order[timeStampKey];
        const orderTime = formatDate(timeStampValue);
        const orderState = orderStatus[order.status];

        console.log(timeStampKey);

        return (
          <>
            <div
              key={idx}
              className="bg-yellow-200 flex justify-center align-center flex-col text-center items-center p-3 m-3"
            >
              <img
                src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRyMNzjqxn4hQQ8bmPj7I1VN8DEWEKf5AsILQ&s"
                className="flex items-center justify-center w-50"
                alt="dummyProductImg"
              />
              <div>가게 이름: {order.store_name}</div>
              <div>상품 이름: {order.product_name}</div>
              <div>수량: {order.quantity}개</div>
              <div>가격: {order.price}원</div>
              <div>상태: {orderState}</div>
              <div>일시: {orderTime}</div>
              <div className="flex flex-col gap-5">
                <button
                  type="button"
                  onClick={() => handleClickDetailBtn(order.payment_id)}
                  className="bg-custom-white p-3"
                >
                  주문 상세 보기
                </button>
                {orderDetail && (
                  <>
                    <div>할인율: {orderDetail.discount_rate}</div>
                    <div>가격: {orderDetail.price}</div>
                    <div>unit 가격: {orderDetail.unit_price}</div>
                  </>
                )}
                {/* <button
                  type="button"
                  onClick={() => handleClickCancelBtn(order.payment_id)}
                  className="bg-custom-white p-3"
                >
                  주문 취소하기(환불 포함)
                </button> */}
                <input
                  type="text"
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  placeholder="취소 사유를 입력"
                />
                <button
                  type="button"
                  onClick={() => handleClickPickupCompleteBtn(order.payment_id)}
                  className="bg-custom-white p-3"
                >
                  픽업 완료하기(qr)
                </button>
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
          </>
        );
      })}
    </>
  );
};

export default Order;
