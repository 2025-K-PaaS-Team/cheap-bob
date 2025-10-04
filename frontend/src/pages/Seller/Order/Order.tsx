import { CommonModal } from "@components/common";
import { Now, OrderList, StatusBar } from "@components/seller/order";
import type { OrderResponseType } from "@interface";
import { getStoreOrder } from "@services/seller/order";
import { useEffect, useState } from "react";

const Order = () => {
  const [orders, setOrders] = useState<OrderResponseType | null>();

  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");

  const handleGetOrders = async () => {
    try {
      const res = await getStoreOrder();
      setOrders(res);
    } catch (err) {
      setModalMsg("주문 목록을 불러오는데 실패했습니다.");
      setShowModal(true);
    }
  };

  useEffect(() => {
    handleGetOrders();
  }, []);

  return (
    <>
      <Now />
      <StatusBar />

      {/* summary */}
      <div className="text-[14px] justify-between mx-[16px] flex flex-row my-[20px]">
        <div>{orders?.total ?? "-"}건의 주문 내역이 있습니다.</div>
        <div>주문 시간 순 ▽</div>
      </div>

      <OrderList />

      {/* show modal */}
      {showModal && (
        <CommonModal
          desc={modalMsg}
          confirmLabel="확인"
          onConfirmClick={() => setShowModal(false)}
          category="black"
        />
      )}
    </>
  );
};

export default Order;
