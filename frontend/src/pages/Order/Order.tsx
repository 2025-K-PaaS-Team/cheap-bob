import { orderStatus } from "@constant";
import type { OrderBaseType } from "@interface/common/types";
import type { OrderDetailResponseType } from "@interface/customer/order";
import { getOrderDetail, getOrders } from "@services";
import { formatDate } from "@utils";
import { useEffect, useState } from "react";

const Order = () => {
  const [orders, setOrders] = useState<OrderBaseType[] | null>(null);
  const [orderDetail, setOrderDetail] =
    useState<OrderDetailResponseType | null>(null);

  const handleGetOrders = async () => {
    try {
      const res = await getOrders();
      console.log("주문 목록 가져오기 성공", res);
      setOrders(res.orders);
    } catch (err: unknown) {
      console.error("get stores fail", err);
    }
  };

  useEffect(() => {
    handleGetOrders();
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

  const handleClickDetailBtn = (paymentId: string) => {
    handleGetOrderDetail(paymentId);
  };

  if (orders.length === 0) return <div>주문 내역이 없습니다</div>;
  return (
    <>
      {orders.map((order, idx) => {
        const timeStampKey = `${order.status.toLowerCase()}_at`;
        const timeStampValue = order[timeStampKey];
        const orderTime = formatDate(timeStampValue);
        const orderState = orderStatus[order.status];

        console.log(timeStampKey);

        return (
          <>
            <h1>전체 주문 목록</h1>
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
              <button
                type="button"
                onClick={() => handleClickDetailBtn(order.payment_id)}
                className="bg-white p-3"
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
            </div>
          </>
        );
      })}
    </>
  );
};

export default Order;
