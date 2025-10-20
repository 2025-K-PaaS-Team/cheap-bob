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
    const hasEmptyTime = form.operation_times.some(
      (t) => !t.pickup_start_time || !t.pickup_end_time
    );

    if (hasEmptyTime) {
      setModalMsg("픽업 시간을 설정해 주세요.");
      setShowModal(true);
      return;
    }

    // register api
    try {
      await handleRegisterStore();
      await handleRegisterStoreImg();
      // setPageIdx(pageIdx + 1);
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    }
    setPageIdx(pageIdx + 1);
  };

  const handleClickPrev = () => {
    setPageIdx(pageIdx - 1);
  };

  return (
    <div className="flex mx-[20px] flex-col my-[20px]  gap-y-[20px]">
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
          width="w-[100px]"
        />
        <CommonBtn
          label="다음"
          onClick={() => handleClickNext()}
          width="w-[250px]"
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
