import { CommonBtn, CommonModal } from "@components/common";
import CommonQR from "@components/common/CommonQR";
import { AllergyList, MenuList, NutritionList, ToppingList } from "@constant";
import type { OrderBaseType } from "@interface";
import { GetOrderQr, updateOrderAccept } from "@services";
import { formatErrMsg, getTitleByKey } from "@utils";
import { useState } from "react";

interface OrderListProps {
  orders: OrderBaseType[];
  status: string;
}

const OrderList = ({ orders, status }: OrderListProps) => {
  const [showModal, setShowModal] = useState<boolean>(false);
  const [showAcceptModal, setShowAcceptModal] = useState<boolean>(false);
  const [openQr, setOpenQr] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");
  const [selectedPaymentId, setSelectedPaymentId] = useState<string | null>(
    null
  );

  const cfmLabel = [
    { key: "reservation", title: "픽업 확정하기" },
    { key: "accepted", title: "픽업 QR 표시" },
  ];

  const handleClickCancel = () => {
    console.log("click cancel button");
  };

  const handleClickConfirm = async (status: string, payment_id: string) => {
    if (status === "reservation") {
      // 픽업 확정 모달 오픈
      setSelectedPaymentId(payment_id);
      setShowAcceptModal(true);
      return;
    }

    // QR 표시
    setOpenQr(true);
    try {
      const res = await GetOrderQr(payment_id);
      console.log("QR data:", res);
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    }
  };

  const handleAcceptConfirm = async () => {
    if (!selectedPaymentId) return;
    try {
      const res = await updateOrderAccept(selectedPaymentId);
      console.log("픽업 확정 완료:", res);
      setShowAcceptModal(false);
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    }
  };

  if (orders.length == 0 || !orders) {
    return (
      <div className="flex flex-col flex-1 gap-y-[20px] justify-center items-center mx-[20px]">
        <img src="/icon/angrySalad.svg" alt="angrySaladIcon" width="116px" />
        <div>
          <h1>주문 내역이 비어있어요.</h1>
          <div className="tagFont">다양한 랜덤팩을 주문하고 픽업해보세요.</div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col mx-[16px] gap-y-[16px] pb-[50px]">
      {orders.map((order, idx) => {
        return (
          <div
            className="bg-white shadow flex flex-col p-[16px] gap-y-[16px]"
            key={idx}
          >
            {/* first row */}
            <div className="flex flex-row justify-between border-b border-black/10 pb-[16px]">
              {/* time */}
              <h3>{order.reservation_at.slice(11, 16)}</h3>
              {/* quantity */}
              <h3>
                <span className="font-normal">주문 수량:</span>{" "}
                <span className="text-main-deep">{order.quantity}</span>개
              </h3>
            </div>
            {/* second row */}
            <div className="flex flex-row justify-between py-[16px]">
              {/* customer name */}
              <h3>
                <span className="font-normal">주문자:</span>{" "}
                {order.customer_nickname}
              </h3>
              {/* more info */}
              <div className="tagFont text-[#6C6C6C]">정보 더보기</div>
            </div>
            {/* third row */}
            <div className="flex flex-row gap-x-[10px] flex-wrap justify-start gap-y-[10px] border-b border-black/10 pb-[16px] tagFont">
              {/* nutrition_types info */}
              <div className="bg-main-pale border border-main-deep rounded py-[7px] px-[16px]">
                {getTitleByKey(order.nutrition_types[0], NutritionList)}
              </div>
              {/* preferred_menus info */}
              <div className="bg-main-pale border border-main-deep rounded py-[7px] px-[16px]">
                {getTitleByKey(order.preferred_menus[0], MenuList)}
              </div>
              {/* topping_types info */}
              <div className="bg-main-pale border border-main-deep rounded py-[7px] px-[16px]">
                {getTitleByKey(order.topping_types[0], ToppingList)}
              </div>
              {/* allergies info */}
              <div className="bg-[#E7E7E7] border border-[#E7E7E7] rounded py-[7px] px-[16px]">
                {getTitleByKey(order.allergies[0], AllergyList)}
              </div>
            </div>
            {/* fourth row */}
            <div className="grid grid-cols-3 pt-[16px]">
              <CommonBtn
                label="주문취소"
                notBottom
                category="white"
                className="w-full border-none"
                onClick={handleClickCancel}
              />
              <CommonBtn
                label={getTitleByKey(status, cfmLabel) ?? ""}
                notBottom
                className="col-span-2 w-full"
                onClick={() => handleClickConfirm(status, order.payment_id)}
              />
            </div>

            {/* qr modal */}
            {openQr && <CommonQR onClick={() => setOpenQr(false)} />}
          </div>
        );
      })}

      {/* show modal */}
      {showModal && (
        <CommonModal
          desc={modalMsg}
          confirmLabel="확인"
          onConfirmClick={() => setShowModal(false)}
          category="green"
        />
      )}

      {/* show accept modal */}
      {showAcceptModal && (
        <CommonModal
          desc="이 주문의 픽업을 확정할까요?"
          confirmLabel="픽업 확정하기"
          cancelLabel="취소"
          onConfirmClick={() => handleAcceptConfirm()}
          onCancelClick={() => setShowAcceptModal(false)}
          category="green"
        />
      )}
    </div>
  );
};

export default OrderList;
