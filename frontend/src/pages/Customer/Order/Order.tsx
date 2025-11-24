import CommonLoading from "@components/common/CommonLoading";
import { NoOrder, OrderCard } from "@components/customer/order";
import type { OrderBaseType } from "@interface";
import { getCurrentOrders } from "@services";
import { useEffect, useState } from "react";

const Order = () => {
  const [orders, setOrders] = useState<OrderBaseType[] | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const handleGetOrders = async () => {
    try {
      const res = await getCurrentOrders();
      const orders = res.orders;
      const filteredOrders = orders.filter((order) => order.status != "cancel");
      setOrders(filteredOrders);
    } catch (err: unknown) {
      console.error("get stores fail", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    handleGetOrders();
  }, []);

  if (isLoading) {
    return <CommonLoading type="data" isLoading={isLoading} />;
  }

  if (!orders || orders.length == 0) {
    return <NoOrder />;
  }

  return (
    <>
      <OrderCard orders={orders} onRefresh={handleGetOrders} />
    </>
  );
};

export default Order;
