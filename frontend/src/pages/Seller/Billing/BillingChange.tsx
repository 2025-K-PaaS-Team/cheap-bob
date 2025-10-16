import { CommonBtn, CommonModal } from "@components/common";
import { UpdateStorePayment } from "@services";
import { formatErrMsg } from "@utils";
import { useState } from "react";

const BillingChange = () => {
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");
  const [chId, setChId] = useState<string>("");
  const [storeId, setStoreId] = useState<string>("");

  const handleUpdatePayment = async () => {
    try {
      await UpdateStorePayment({
        portone_channel_id: chId,
        portone_store_id: storeId,
      });
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
      return;
    }
  };

  return (
    <div className="relative h-full flex flex-col mx-[37px] gap-y-[10px]">
      {/* id */}
      <>
        <div className="bodyFont font-bold mt-[50px]">대표 상점 아이디</div>
        {/* input box */}
        <input
          className="w-full h-[46px] border-b border-black/80 hintFont"
          placeholder="대표 상점 아이디를 입력하세요."
          value={storeId}
          onChange={(e) => setStoreId(e.target.value)}
        />
        <div className="hintFont text-[#6C6C6C]">
          연동 정보 페이지 상단에서 확인할 수 있어요.
        </div>
      </>

      <>
        {/* channel key */}
        <div className="bodyFont font-bold mt-[15px]">채널 키</div>
        {/* input box */}
        <input
          className="w-full h-[46px] border-b border-black/80 hintFont"
          placeholder="채널 키를 입력하세요."
          value={chId}
          onChange={(e) => setChId(e.target.value)}
        />
        <div className="hintFont text-[#6C6C6C]">
          연동 정보 &gt; 채널 관리 탭에서 확인할 수 있어요.
        </div>
      </>

      <>
        {/* notice */}
        <div className="absolute bottom-50 w-full hintFont bg-[#E7E7E7] rounded py-[20px] px-[8px]">
          <b>시크릿 V2 API 키 변경</b>이 필요한 경우 <br />
          cheapbob2025@gmail.com으로 문의해 주세요.
        </div>
      </>

      <>
        {/* secret v2 key */}
        {/* <div className="bodyFont font-bold mt-[15px]">시크릿 V2 API</div> */}
        {/* input box */}
        {/* <input
          className="w-full h-[46px] text-center border-b border-black/80 bodyFont font-bold"
          placeholder="채널 키를 입력해 주세요"
          value={value}
          onChange={(e) => setValue(e.target.value)}
        />
        <div className="hintFont text-[#6C6C6C]">
          연동 정보 &gt; 식별 코드 · API Keys &gt; V2 API 탭에서 확인하세요.
          <br />
          <br /> ※ 최초 발급 후에는 확인할 수 없으니 주의하세요. <br />※ 만료 시
          변경이 필요해요.
        </div> */}
      </>

      {/* save */}
      <CommonBtn
        label="저장"
        onClick={() => handleUpdatePayment()}
        category="green"
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

export default BillingChange;
