import { CommonBtn, CommonModal } from "@components/common";
import { CommonPuTime } from "@components/seller/common";
import type { SellerSignupProps } from "@interface";
import { useSignupStore } from "@store";
import { validationRules } from "@utils";
import { useEffect, useState } from "react";

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
    const { storeAddr } = validationRules;
    if (!form.address_info.address || !form.address_info.postal_code) {
      setModalMsg(storeAddr.errorMessage);
      setShowModal(true);
      return;
    }
    setPageIdx(pageIdx + 1);
  };

  const handleClickPrev = () => {
    setPageIdx(pageIdx - 1);
  };

  useEffect(() => {
    console.log(form);
  }, [form]);

  return (
    <div className="flex mx-[20px] flex-col mt-[69px] gap-y-[11px]">
      <div className="text-[16px]">2/4</div>
      <div className="text-[24px]">
        할인팩 <span className="font-bold">픽업 시간</span>을 <br />{" "}
        설정해주세요.
      </div>

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
