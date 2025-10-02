import { CommonBtn, CommonModal } from "@components/common";
import type { SellerSignupProps } from "@interface";
import { useSignupStore } from "@store";
import { validatePattern, validationRules } from "@utils";
import { useState } from "react";

const RegisterNum = ({ pageIdx, setPageIdx }: SellerSignupProps) => {
  const { form, setForm } = useSignupStore();
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");

  const handleClickNext = () => {
    const { storePhone } = validationRules;
    if (!validatePattern(form.store_phone, storePhone.pattern)) {
      setModalMsg(storePhone.errorMessage);
      setShowModal(true);
      return;
    }
    setPageIdx(pageIdx + 1);
  };

  const handleClickPrev = () => {
    setPageIdx(pageIdx - 1);
  };

  return (
    <div className="mx-[20px] mt-[69px] flex flex-col gap-y-[11px]">
      <div className="text-[16px]">4/4</div>
      <div className="text-[24px]">
        <span className="font-bold">매장 연락처</span>를 알려주세요.
      </div>
      <div className="text-[16px]">손님에게 연락이 올 수 있어요.</div>

      {/* input box */}
      <div className="mt-[40px] gap-y-[11px]">
        <div className="text-[16px]">매장 전화번호 (*필수)</div>
        <input
          className="w-full h-[46px] text-center bg-[#D9D9D9] text-[16px]"
          placeholder="매장 전화번호를 입력해 주세요"
          value={form.store_phone}
          onChange={(e) => setForm({ store_phone: e.target.value })}
        />
      </div>

      {/* other sns */}
      <div className="mt-[39px] flex flex-col gap-y-[11px]">
        <div className="text-[20px]">다른 SNS도 있나요?</div>
        <div className="flex flex-row">
          <div className="text-[14px] w-[97px] flex items-center">홈페이지</div>
          <input
            className="w-full h-[40px] text-center bg-[#D9D9D9] text-[16px]"
            value={form.sns_InfoType.homepage}
            onChange={(e) =>
              setForm({
                sns_InfoType: {
                  ...form.sns_InfoType,
                  homepage: e.target.value,
                },
              })
            }
          />
        </div>
        <div className="flex flex-row">
          <div className="text-[14px] w-[97px] flex items-center">
            인스타그램
          </div>
          <input
            className="w-full h-[40px] text-center bg-[#D9D9D9] text-[16px]"
            value={form.sns_InfoType.instagram}
            onChange={(e) =>
              setForm({
                sns_InfoType: {
                  ...form.sns_InfoType,
                  instagram: e.target.value,
                },
              })
            }
          />
        </div>
        <div className="flex flex-row">
          <div className="text-[14px] w-[97px] flex items-center">
            X (Twitter)
          </div>
          <input
            className="w-full h-[40px] text-center bg-[#D9D9D9] text-[16px]"
            value={form.sns_InfoType.x}
            onChange={(e) =>
              setForm({
                sns_InfoType: { ...form.sns_InfoType, x: e.target.value },
              })
            }
          />
        </div>
      </div>

      <CommonBtn
        category="grey"
        label="이전"
        onClick={() => handleClickPrev()}
        notBottom
        className="absolute left-[20px] bottom-[38px]"
        width="w-[100px]"
      />
      <CommonBtn
        category="black"
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
          onConfirmClcik={() => setShowModal(false)}
          category="black"
        />
      )}
    </div>
  );
};

export default RegisterNum;
