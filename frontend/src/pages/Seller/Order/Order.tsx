import { CommonModal } from "@components/common";
import { Now, OrderList, StatusBar } from "@components/seller/order";
import type { OrderBaseType, OrderResponseType } from "@interface";
import { getStoreOrder } from "@services/seller/order";
import { useEffect, useMemo, useState } from "react";

const Order = () => {
  const [orders, setOrders] = useState<OrderResponseType | null>();

  const [status, setStatus] = useState<string>("reservation");

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

  const sortByDateDesc = (a?: string | null, b?: string | null) =>
    new Date(b ?? 0).getTime() - new Date(a ?? 0).getTime();

  const reservationOrders = useMemo<OrderBaseType[]>(
    () =>
      (orders?.orders ?? [])
        .filter((o) => o.status === "reservation")
        .sort((a, b) => sortByDateDesc(a.reservation_at, b.reservation_at)),
    [orders]
  );

  const acceptedOrders = useMemo<OrderBaseType[]>(
    () =>
      (orders?.orders ?? [])
        .filter((o) => o.status === "accepted")
        .sort((a, b) => sortByDateDesc(a.accepted_at, b.accepted_at)),
    [orders]
  );

  const otherOrders = useMemo<OrderBaseType[]>(
    () =>
      (orders?.orders ?? [])
        .filter((o) => o.status === "completed" || o.status === "canceled")
        .sort((a, b) => sortByDateDesc(a.completed_at, b.completed_at)),
    [orders]
  );

  const nowOrderList = useMemo<OrderBaseType[]>(() => {
    switch (status) {
      case "reservation":
        return reservationOrders;
      case "accepted":
        return acceptedOrders;
      case "others":
        return otherOrders;
      default:
        return reservationOrders;
    }
  }, [status, reservationOrders, acceptedOrders, otherOrders]);

  return (
    <>
      <Now />
      <StatusBar status={status} setStatus={setStatus} />

      {/* summary */}
      <div className="text-[14px] justify-between mx-[16px] flex flex-row my-[20px]">
        <div>{orders?.total ?? "0"}건의 주문 내역이 있습니다.</div>
        <div>주문 시간 순 ▽</div>
      </div>

      <OrderList orders={nowOrderList} />

      {/* show modal */}
      {showModal && (
        <CommonModal
          desc={modalMsg}
          confirmLabel="확인"
          onConfirmClick={() => setShowModal(false)}
          category="green"
        />
      )}
    </>
  );
};

export default Order;
