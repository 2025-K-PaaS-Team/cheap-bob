import { CommonBtn } from "@components/common";
import CommonQR from "@components/common/CommonQR";
import type { OrderBaseType } from "@interface";
import { useState } from "react";

interface OrderListProps {
  orders: OrderBaseType[];
}

const OrderList = ({ orders }: OrderListProps) => {
  const [openQr, setOpenQr] = useState<boolean>(false);

  const handleClickCancel = () => {
    console.log("click cancel button");
  };

  const handleClickConfirm = () => {
    setOpenQr(true);
  };

  return (
    <div className="flex flex-col mx-[16px] gap-y-[16px]">
      {orders.length == 0 && (
        <div className="flex flex-col bg-[#d9d9d9] rounded-[8px] py-[22px] px-[15px] gap-y-[16px]">
          {/* first row */}
          <div className="flex flex-row justify-between items-center">
            <div className="flex flex-row gap-x-[12px] items-center">
              <div className="font-bold text-[16px]">13:22</div>
              <div className="text-[20px]">
                수량: <span className="font-bold">1개</span>
              </div>
            </div>
            <div className="text-[16px]">주문자 정보 더보기 &gt;</div>
          </div>

          {/* second row */}

          <div className="ml-[40px] bg-white rounded-[8px] flex flex-col py-[9.5px] px-[14px]">
            <div className="text-[16px]">영양목표: 균형있게</div>
            <div className="text-[16px]">선호 메뉴: 포케</div>
            <div className="text-[16px]">알레르기 정보: 갑각류</div>
          </div>

          {/* third row - btn */}
          <div className="flex flex-row ml-[40px]">
            <CommonBtn
              label="주문 취소"
              onClick={() => handleClickCancel()}
              notBottom
              category="transparent"
              width="w-1/3"
            />
            <CommonBtn
              label="픽업 확정하기"
              onClick={() => handleClickConfirm()}
              notBottom
              category="black"
              width="w-2/3"
            />
          </div>
        </div>
      )}

      <div className="">
        {openQr && <CommonQR onClick={() => setOpenQr(false)} />}
      </div>
    </div>
  );
};

export default OrderList;
