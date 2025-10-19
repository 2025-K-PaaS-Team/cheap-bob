import { CommonBtn, CommonModal } from "@components/common";
import { CommonPuTime } from "@components/seller/common";
import type { SellerSignupProps } from "@interface";
import { useSignupStore } from "@store";
import { useState } from "react";

const RegisterPuTime = ({ pageIdx, setPageIdx }: SellerSignupProps) => {
  const {
    form,
    setForm,
    pickupStartOffset,
    setPickupStartOffset,
    pickupDiscardOffset,
    setPickupDiscardOffset,
  } = useSignupStore();
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");

  const handleClickNext = () => {
    const hasEmptyTime = form.operation_times.some(
      (t) => !t.pickup_start_time || !t.pickup_end_time
    );

    if (hasEmptyTime) {
      setModalMsg("픽업 시간을 설정해 주세요.");
      setShowModal(true);
      return;
    }
    setPageIdx(pageIdx + 1);
  };

  const handleClickPrev = () => {
    setPageIdx(pageIdx - 1);
  };

  return (
    <div className="flex mx-[20px] flex-col mt-[20px]  gap-y-[20px]">
      {/* progress */}
      <div className="text-main-deep font-bold bodyFont">2/2</div>

      {/* pu time */}
      <CommonPuTime
        form={form.operation_times}
        setForm={(times) =>
          setForm((prev) => ({
            ...prev,
            operation_times: times,
          }))
        }
        pickupStartOffset={pickupStartOffset}
        setPickupStartOffset={setPickupStartOffset}
        pickupDiscardOffset={pickupDiscardOffset}
        setPickupDiscardOffset={setPickupDiscardOffset}
      />

      <CommonBtn
        category="grey"
        label="이전"
        onClick={() => handleClickPrev()}
        notBottom
        className="absolute left-[20px] bottom-[38px]"
        width="w-[100px]"
      />
      <CommonBtn
        category="green"
        label="다음"
        onClick={() => handleClickNext()}
        notBottom
        className="absolute right-[20px] bottom-[38px]"
        width="w-[250px]"
      />
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

export default RegisterPuTime;
