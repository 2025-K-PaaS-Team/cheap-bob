import { CommonBtn, CommonModal } from "@components/common";
import { CommonPuTime } from "@components/seller/common";
import type { SellerSignupProps } from "@interface";
import { registerStore, registerStoreImg } from "@services";
import { useSignupImageStore, useSignupStore } from "@store";
import { formatErrMsg } from "@utils";
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
  const { form: imgForm } = useSignupImageStore();
  const startOffsetMin =
    (pickupStartOffset?.hour ?? 0) * 60 + (pickupStartOffset?.min ?? 0);

  const handleRegisterStore = async () => {
    try {
      const res = await registerStore(form);
      console.log("등록 성공:", res);
    } catch (err: unknown) {
      console.error("등록 실패:", err);
      throw err;
    }
  };

  const handleRegisterStoreImg = async () => {
    try {
      const files = imgForm.images.map((it) => it.file);
      const res = await registerStoreImg(files);
      console.log("이미지 업로드 성공:", res);
    } catch (err: any) {
      console.error("이미지 업로드 실패:", err);
      throw err;
    }
  };

  const handleClickNext = async () => {
    if (startOffsetMin < 90) {
      setModalMsg(`픽업 시작은 마감 기준 1시간 30분 이상 전이어야 합니다.`);
      setShowModal(true);
      return;
    }

    try {
      await handleRegisterStore();
      await handleRegisterStoreImg();
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
      // return;
    }

    setPageIdx(pageIdx + 1);
  };

  const handleClickPrev = () => {
    setPageIdx(pageIdx - 1);
  };

  return (
    <div className="flex mx-[20px] flex-col flex-1 my-[20px]  gap-y-[20px]">
      <div className="flex flex-1 flex-col gap-y-[40px]">
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
      </div>

      <div className="grid grid-cols-3">
        <CommonBtn
          category="transparent"
          label="이전"
          onClick={() => handleClickPrev()}
          notBottom
        />
        <CommonBtn
          label="다음"
          onClick={() => handleClickNext()}
          className="col-span-2"
          notBottom
        />
      </div>

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
