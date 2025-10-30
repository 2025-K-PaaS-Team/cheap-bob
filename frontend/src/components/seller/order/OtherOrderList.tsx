import { orderStatus } from "@constant";
import type { OrderBaseType } from "@interface";

interface OtherOrderListProps {
  orders: OrderBaseType[];
  status: string;
  onRefresh: () => void;
}

const OtherOrderList = ({ orders }: OtherOrderListProps) => {
  if (orders.length == 0 || !orders) {
    return (
      <div className="bg-custom-white flex flex-col flex-1 gap-y-[20px] justify-center items-center px-[20px]">
        <img src="/icon/angrySalad.svg" alt="angrySaladIcon" width="116px" />
        <div>
          <h1>주문 내역이 비어있어요.</h1>
          <div className="tagFont">다양한 랜덤팩을 주문하고 픽업해보세요.</div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-custom-white flex flex-col flex-1 px-[16px] py-[20px] gap-y-[16px]">
      {/* summary */}
      <div className="hintFont justify-between flex flex-row">
        <div>
          <span className="text-main-deep font-bold">
            {orders?.length ?? "0"}
          </span>{" "}
          건의 주문 내역이 있습니다.
        </div>
        <div>주문 시간 순 ▽</div>
      </div>

      {orders.map((order, idx) => {
        const doneOrCanceledAt = order.completed_at ?? order.canceled_at ?? "";

        return (
          <div
            className="bg-white shadow flex flex-col p-[16px] gap-y-[16px] rounded"
            key={idx}
          >
            {/* first row */}
            <div className="flex flex-row justify-between border-b border-black/10 pb-[16px]">
              {/* time */}
              <h3>
                {order?.reservation_at
                  ? new Date(order.reservation_at).toLocaleTimeString("ko-KR", {
                      hour: "2-digit",
                      minute: "2-digit",
                      hour12: false,
                      timeZone: "Asia/Seoul",
                    })
                  : "--:--"}
              </h3>
              {/* quantity */}
              <h3>
                <span className="font-normal">주문 수량:</span>{" "}
                <span className="text-main-deep">{order.quantity}</span>개
              </h3>
            </div>
            {/* second row */}
            <div className="flex flex-row justify-end gap-x-[16px] bodyFont">
              <div>
                {doneOrCanceledAt ? doneOrCanceledAt.slice(11, 16) : "--:--"}
              </div>
              <div
                className={`font-bold ${
                  order.status == "cancel"
                    ? "text-sub-orange"
                    : "text-main-deep"
                }`}
              >
                {orderStatus[order.status as keyof typeof orderStatus] ?? ""}
                {order.status == "cancel" && " - "}
                {order.cancel_reason}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default OtherOrderList;
