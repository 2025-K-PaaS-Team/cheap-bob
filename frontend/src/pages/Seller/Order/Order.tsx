import { CommonModal } from "@components/common";
import CommonLoading from "@components/common/CommonLoading";
import {
  Now,
  OrderList,
  OtherOrderList,
  StatusBar,
} from "@components/seller/order";
import type {
  OrderBaseType,
  OrderResponseType,
  StoreOperationType,
} from "@interface";
import { GetStoreOperation } from "@services";
import { getStoreTodayOrder } from "@services/seller/order";
import { useEffect, useMemo, useState } from "react";

const Order = () => {
  const [orders, setOrders] = useState<OrderResponseType | null>(null);
  const [status, setStatus] = useState<string>("reservation");
  const [op, setOp] = useState<StoreOperationType>([]);

  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");
  const [lastUpdated, setLastUpdated] = useState<string>("");

  const [isLoading, setIsLoading] = useState<boolean>(true);

  const fetchInitialData = async () => {
    setIsLoading(true);
    try {
      const [ordersRes, opRes] = await Promise.all([
        getStoreTodayOrder(),
        GetStoreOperation(),
      ]);
      setOrders(ordersRes);
      setOp(opRes);

      const now = new Date();
      const hh = now.getHours().toString().padStart(2, "0");
      const mm = now.getMinutes().toString().padStart(2, "0");
      setLastUpdated(`${hh}시 ${mm}분`);
    } catch (err) {
      setModalMsg("데이터를 불러오는데 실패했습니다.");
      setShowModal(true);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchInitialData();
  }, []);

  // 리프레시용
  const handleGetOrders = async () => {
    setIsLoading(true);
    try {
      const res = await getStoreTodayOrder();
      setOrders(res);

      const now = new Date();
      const hh = now.getHours().toString().padStart(2, "0");
      const mm = now.getMinutes().toString().padStart(2, "0");
      setLastUpdated(`${hh}시 ${mm}분`);
    } catch (err) {
      setModalMsg("주문 목록을 불러오는데 실패했습니다.");
      setShowModal(true);
    } finally {
      setIsLoading(false);
    }
  };

  const reservationOrders = useMemo<OrderBaseType[]>(
    () => (orders?.orders ?? []).filter((o) => o.status === "reservation"),
    [orders]
  );

  const acceptedOrders = useMemo<OrderBaseType[]>(
    () => (orders?.orders ?? []).filter((o) => o.status === "accept"),
    [orders]
  );

  const otherOrders = useMemo<OrderBaseType[]>(
    () =>
      (orders?.orders ?? []).filter(
        (o) => o.status === "complete" || o.status === "cancel"
      ),
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

  if (isLoading) {
    return <CommonLoading type="data" isLoading={isLoading} />;
  }

  return (
    <div className="flex flex-col h-full">
      <Now onRefresh={handleGetOrders} lastUpdated={lastUpdated} op={op} />
      <StatusBar status={status} setStatus={setStatus} />

      {status === "others" ? (
        <OtherOrderList
          orders={nowOrderList}
          status={status}
          onRefresh={handleGetOrders}
        />
      ) : (
        <OrderList
          orders={nowOrderList}
          status={status}
          onRefresh={handleGetOrders}
        />
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
};

export default Order;
