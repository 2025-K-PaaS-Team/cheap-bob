import { CommonModal } from "@components/common";
import { Now, OrderList, StatusBar } from "@components/seller/order";
import type {
  OrderBaseType,
  OrderResponseType,
  StoreOperationType,
} from "@interface";
import { GetStoreOperation } from "@services";
import { getStoreOrder } from "@services/seller/order";
import { useEffect, useMemo, useState } from "react";

const Order = () => {
  const [orders, setOrders] = useState<OrderResponseType | null>();

  const [status, setStatus] = useState<string>("reservation");
  const [op, setOp] = useState<StoreOperationType>([]);

  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");
  const [lastUpdated, setLastUpdated] = useState<string>("");

  const handleGetOrders = async () => {
    try {
      const res = await getStoreOrder();
      setOrders(res);

      const now = new Date();
      const hh = now.getHours().toString().padStart(2, "0");
      const mm = now.getMinutes().toString().padStart(2, "0");
      setLastUpdated(`${hh}시 ${mm}분`);
    } catch (err) {
      setModalMsg("주문 목록을 불러오는데 실패했습니다.");
      setShowModal(true);
    }
  };

  const handleGetStoreOperation = async () => {
    try {
      const res = await GetStoreOperation();
      setOp(res);
    } catch {
      setModalMsg("운영 정보를 불러오는 것에 실패했습니다.");
      setShowModal(true);
    }
  };

  useEffect(() => {
    handleGetOrders();
    handleGetStoreOperation();
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
        .filter((o) => o.status === "accept")
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
      case "accept":
        return acceptedOrders;
      case "others":
        return otherOrders;
      default:
        return reservationOrders;
    }
  }, [status, reservationOrders, acceptedOrders, otherOrders]);

  return (
    <div className="flex flex-col h-full">
      <Now onRefresh={handleGetOrders} lastUpdated={lastUpdated} op={op} />
      <StatusBar status={status} setStatus={setStatus} />

      <OrderList
        orders={nowOrderList}
        status={status}
        onRefresh={handleGetOrders}
      />

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
};

export default Order;
