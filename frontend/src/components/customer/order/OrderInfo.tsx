import type { OrderBaseType } from "@interface";

interface OrderInfoType {
  order: OrderBaseType;
  isAll: boolean;
}

export const OrderInfo = ({ order, isAll }: OrderInfoType) => {
  return (
    <div className="grid grid-cols-5 gap-x-[11px]">
      <img
        src={order.main_image_url}
        alt="storeImg"
        className="rounded object-cover col-span-2"
      />
      <div className="col-span-3 flex flex-col">
        <div className="bodyFont font-bold pb-[8px]">{order.store_name}</div>
        <div className="tagFont pb-[22px]">
          {Number(order.total_amount).toLocaleString()}원
        </div>
        {isAll ? (
          <div className="font-bold tagFont">{order.product_name}</div>
        ) : (
          <div className="font-bold tagFont">
            픽업: {order.pickup_start_time} ~ {order.pickup_end_time}
          </div>
        )}
      </div>
    </div>
  );
};
