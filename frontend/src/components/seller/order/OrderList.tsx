import {
  CommonBtn,
  CommonDropbox,
  CommonModal,
  CommonProfile,
} from "@components/common";
import CommonQR from "@components/common/CommonQR";
import {
  AllergyList,
  CancelOption,
  MenuList,
  NutritionList,
  ToppingList,
} from "@constant";
import { useToast } from "@context";
import type { GetQrCodeType, OrderBaseType } from "@interface";
import type { OptionType } from "@interface/common/types";
import { cancelOrder, GetOrderQr, updateOrderAccept } from "@services";
import { formatErrMsg, getTitleByKey } from "@utils";

import { useState } from "react";

interface OrderListProps {
  orders: OrderBaseType[];
  status: string;
  onRefresh: () => void;
}

const OrderList = ({ orders, status, onRefresh }: OrderListProps) => {
  const { showToast } = useToast();
  const [showModal, setShowModal] = useState<boolean>(false);
  const [showAcceptModal, setShowAcceptModal] = useState<boolean>(false);
  const [openQr, setOpenQr] = useState<boolean>(false);
  const [showCancelModal, setShowCancelModal] = useState<boolean>(false);
  const [qrData, setQrData] = useState<GetQrCodeType | null>(null);
  const [modalMsg, setModalMsg] = useState("");
  const [selectedPaymentId, setSelectedPaymentId] = useState<string | null>(
    null
  );
  const [showProfile, setShowProfile] = useState<boolean>(false);
  const [selectedProfile, setSelectedProfile] = useState<OrderBaseType | null>(
    null
  );
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [reason, setReason] = useState<OptionType | null>(null);

  const cfmLabel = [
    { key: "reservation", title: "픽업 확정하기" },
    { key: "accept", title: "픽업 QR 표시" },
  ];

  const handleClickCancel = async (paymentId: string, reason: string) => {
    if (!paymentId) {
      setModalMsg("주문 정보를 찾을 수 없습니다.");
      setShowModal(true);
      return;
    }

    if (isProcessing) return;
    setIsProcessing(true);

    try {
      await cancelOrder(paymentId, reason);
      onRefresh();
      showToast("주문 취소에 성공했어요.", "success");
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    } finally {
      setIsProcessing(false);
      setShowCancelModal(false);
    }
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
      setQrData(res);
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    }
  };

  const handleAcceptConfirm = async () => {
    if (!selectedPaymentId) return;
    try {
      const res = await updateOrderAccept(selectedPaymentId);
      await onRefresh();
      console.log("픽업 확정 완료:", res);
      showToast("픽업 확정에 성공했어요.", "success");
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    } finally {
      setShowAcceptModal(false);
    }
  };

  const handleOpenProfile = (order: OrderBaseType) => {
    setSelectedProfile(order);
    setShowProfile(true);
  };

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
        return (
          <div
            className="bg-white shadow flex flex-col p-[16px] gap-y-[16px] rounded"
            key={idx}
          >
            {/* first row */}
            <div className="flex flex-row justify-between border-b border-black/10 pb-[16px]">
              {/* time */}
              <h3>{order?.reservation_at.slice(11, 16)}</h3>
              {/* quantity */}
              <h3>
                <span className="font-normal">주문 수량:</span>{" "}
                <span className="text-main-deep">{order?.quantity}</span>개
              </h3>
            </div>
            {/* second row */}
            <div className="flex flex-row justify-between py-[16px]">
              {/* customer name */}
              <h3>
                <span className="font-normal">주문자:</span>{" "}
                {order?.customer_nickname}
              </h3>
              {/* more info */}
              <div
                onClick={() => handleOpenProfile(order)}
                className="tagFont text-[#6C6C6C]"
              >
                정보 더보기
              </div>
            </div>
            {/* third row */}
            <div className="flex flex-row gap-x-[10px] flex-wrap justify-start gap-y-[10px] border-b border-black/10 pb-[16px] tagFont">
              {/* nutrition_types info */}
              <div className="bg-main-pale border border-main-deep rounded py-[7px] px-[16px]">
                {getTitleByKey(order?.nutrition_types[0], NutritionList)}
              </div>
              {/* preferred_menus info */}
              <div className="bg-main-pale border border-main-deep rounded py-[7px] px-[16px]">
                {getTitleByKey(order?.preferred_menus[0], MenuList)}
              </div>
              {/* topping_types info */}
              <div className="bg-main-pale border border-main-deep rounded py-[7px] px-[16px]">
                {getTitleByKey(order?.topping_types[0], ToppingList)}
              </div>
              {/* allergies info */}
              <div className="bg-[#E7E7E7] border border-[#E7E7E7] rounded py-[7px] px-[16px]">
                {getTitleByKey(order?.allergies[0], AllergyList)}
              </div>
            </div>
            {/* fourth row */}
            <div className="grid grid-cols-3">
              <CommonBtn
                label="주문취소"
                notBottom
                category="white"
                className="w-full border-none"
                onClick={() => {
                  setSelectedPaymentId(order?.payment_id);
                  setShowCancelModal(true);
                }}
              />
              <CommonBtn
                label={getTitleByKey(status, cfmLabel) ?? ""}
                notBottom
                className="col-span-2 w-full"
                onClick={() => handleClickConfirm(status, order?.payment_id)}
              />
            </div>

            {/* qr modal */}
            {openQr && qrData && (
              <CommonQR onClick={() => setOpenQr(false)} qrData={qrData} />
            )}
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

      {/* show cancel modal */}
      {showCancelModal && (
        <CommonModal
          desc="주문 취소 사유를 선택하세요."
          confirmLabel="주문 취소하기"
          cancelLabel="취소"
          onConfirmClick={() => {
            !isProcessing &&
              handleClickCancel(selectedPaymentId ?? "", reason?.label ?? "");
          }}
          onCancelClick={() => !isProcessing && setShowCancelModal(false)}
          category="red"
          isProcessing={isProcessing}
        >
          <CommonDropbox
            options={CancelOption}
            value={reason}
            onChange={setReason}
            placeholder="취소 사유를 선택하세요."
          />
        </CommonModal>
      )}

      {/* show profile modal */}
      {showProfile && selectedProfile && (
        <CommonProfile
          nickname={selectedProfile.customer_nickname}
          phone={selectedProfile.customer_phone_number}
          nutrition_goal={selectedProfile.nutrition_types.map((n) =>
            getTitleByKey(n, NutritionList)
          )}
          prefer_menu={selectedProfile.preferred_menus.map((m) =>
            getTitleByKey(m, MenuList)
          )}
          prefer_topping={selectedProfile.topping_types.map((t) =>
            getTitleByKey(t, ToppingList)
          )}
          allergy={selectedProfile.allergies.map((a) =>
            getTitleByKey(a, AllergyList)
          )}
          onCancelClick={() => setShowProfile(false)}
        />
      )}
    </div>
  );
};

export default OrderList;
