import { Now, OrderList, StatusBar } from "@components/seller/order";

const Order = () => {
  return (
    <>
      <Now />
      <StatusBar />

      {/* summary */}
      <div className="text-[14px] justify-between mx-[16px] flex flex-row my-[20px]">
        <div>n건의 주문 내역이 있습니다.</div>
        <div>주문 시간 순▽</div>
      </div>

      <OrderList />
    </>
  );
};

export default Order;
