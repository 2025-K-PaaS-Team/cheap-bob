import type { OrderBaseType } from "@interface";

interface OrderStatusType {
  order: OrderBaseType;
  orderState: string;
  handleOpenProfile: (order: OrderBaseType) => void;
  orderTime: string;
}

export const OrderStatus = ({
  order,
  orderState,
  handleOpenProfile,
  orderTime,
}: OrderStatusType) => {
  const getColorByStatus = (status: string) => {
    if (status === "reservation" || status === "cancel") {
      return "bg-[#E7E7E7]";
    }
    return "bg-main-pale text-main-deep border-main-deep border";
  };

  return (
    <div className="flex flex-row justify-between">
      <div
        className={`px-[16px] py-[8px] rounded tagFont ${getColorByStatus(
          order.status
        )}`}
      >
        {orderState}
      </div>
      <div
        onClick={() => handleOpenProfile(order)}
        className="tagFont font-bold flex flex-row gap-x-[3px] items-center justify-center cursor-pointer"
      >
        <div>{orderTime}</div>
        <div>·</div>
        <div>{order.quantity}개</div>
        <img src="/icon/next.svg" alt="nextIcon" width="14px" />
      </div>
    </div>
  );
};
