import { CommonBtn } from "@components/common";
import CommonLoading from "@components/common/CommonLoading";
import { OrderCard } from "@components/customer/order";
import type { OrderBaseType } from "@interface/common/types";
import { getCurrentOrders } from "@services";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const Order = () => {
  const navigate = useNavigate();
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
    return (
      <div className="flex flex-col h-full justify-center items-center">
        <img
          src="/icon/angrySalad.svg"
          alt="saladBowlIcon"
          className="pb-[26px] w-[116px]"
        />
        <div className="text-[20px] pb-[17px] font-bold">
          주문 내역이 비어있어요.
        </div>
        <div className="text-[12px] font-base pb-[46px]">
          다양한 랜덤팩을 주문하고 픽업해보세요.
        </div>
        <CommonBtn
          label="실시간 랜덤팩 보러가기"
          notBottom
          width="w-[calc(100%-40px)]"
          onClick={() => navigate("/c/stores")}
        />
      </div>
    );
  }

  return (
    <>
      <OrderCard orders={orders} onRefresh={handleGetOrders} />
    </>
  );
};

export default Order;
