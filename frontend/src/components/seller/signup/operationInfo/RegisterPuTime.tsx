import { CommonBtn, CommonModal } from "@components/common";
import type { SellerSignupProps } from "@interface";
import { useSignupStore } from "@store";
import { validationRules } from "@utils";
import { useState } from "react";

const RegisterPuTime = ({ pageIdx, setPageIdx }: SellerSignupProps) => {
  const { form } = useSignupStore();
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");

  const handleClickNext = () => {
    const { storeAddr } = validationRules;
    if (!form.address_InfoType.address || !form.address_InfoType.postal_code) {
      setModalMsg(storeAddr.errorMessage);
      setShowModal(true);
      return;
    }
    setPageIdx(pageIdx + 1);
  };

  const handleClickPrev = () => {
    setPageIdx(pageIdx - 1);
  };

  return (
    <div className="flex mx-[20px] flex-col mt-[69px] gap-y-[11px]">
      <div className="text-[16px]">2/4</div>
      <div className="text-[24px]">
        할인팩
        <span className="font-bold">픽업 시간</span>을 <br /> 설정해주세요.
      </div>

      {/* pickup time */}
      <div className="text-[14px] font-bold">픽업 시간</div>
      <div className="text-[14px]">
        마감 세일을 시작할 시간을 입력해 주세요.
      </div>
      <div className="text-center w-full justify-center">
        {/* before time */}
        <div className="flex flex-row text-[20px] justify-center items-center gap-x-[10px]">
          <div className="bg-[#d9d9d9] rounded-[8px] w-[50px] h-[44px] flex items-center justify-center">
            2
          </div>
          <div>시</div>
          <div className="bg-[#d9d9d9] rounded-[8px] w-[50px] h-[44px] flex items-center justify-center">
            30
          </div>
          <div>분 전부터</div>
        </div>
        <div className="text-[14px] mt-[10px]">
          19시부터 사용자들은 매장에 방문하여 <br /> 패키지를 픽업할 수
          있습니다.
        </div>
      </div>

      {/* after time */}
      <div className="text-[14px] font-bold mt-[40px]">픽업 마감 시간</div>
      <div className="text-[14px]">픽업을 마감할 시간을 입력해 주세요.</div>
      <div className="text-center w-full justify-center">
        {/* before time */}
        <div className="flex flex-row text-[20px] justify-center items-center gap-x-[10px]">
          <div className="bg-[#d9d9d9] rounded-[8px] w-[50px] h-[44px] flex items-center justify-center">
            2
          </div>
          <div>시</div>
          <div className="bg-[#d9d9d9] rounded-[8px] w-[50px] h-[44px] flex items-center justify-center">
            30
          </div>
          <div>분 전부터</div>
        </div>
        <div className="text-[14px] mt-[10px]">
          19시부터 사용자들은 매장에 방문하여 <br /> 패키지를 픽업할 수
          있습니다.
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

export default RegisterPuTime;
