import { CommonBtn, CommonModal } from "@components/common";
import {
  CheckPaymentInfo,
  RegisterPayment,
  UpdateStorePayment,
} from "@services";
import { formatErrMsg } from "@utils";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router";

const BillingChange = () => {
  const navigate = useNavigate();
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");
  const [chId, setChId] = useState<string>("");
  const [storeId, setStoreId] = useState<string>("");
  const [secretKey, setSecretKey] = useState<string>("");
  const [paymentExist, setPaymentExist] = useState<boolean>(true);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const handleCheckPaymentInfo = async () => {
    try {
      const res = await CheckPaymentInfo();
      setPaymentExist(res.is_exist);
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    }
  };

  const handleUpdatePayment = async () => {
    if (!paymentExist) {
      try {
        await RegisterPayment({
          portone_channel_id: chId,
          portone_store_id: storeId,
          portone_secret_key: secretKey,
        });
        navigate(-1);
      } catch (err) {
        setModalMsg(formatErrMsg(err));
        setShowModal(true);
        return;
      }
    } else {
      try {
        await UpdateStorePayment({
          portone_channel_id: chId,
          portone_store_id: storeId,
        });
        navigate(-1);
      } catch (err) {
        setModalMsg(formatErrMsg(err));
        setShowModal(true);
        return;
      }
    }
  };

  useEffect(() => {
    handleCheckPaymentInfo();
    setIsLoading(false);
  }, []);

  if (isLoading) {
    return <div>로딩 중...</div>;
  }

  return (
    <div className="relative h-full flex flex-col m-[20px] gap-y-[10px]">
      {/* id */}
      <div className="flex flex-1 flex-col">
        <div className="bodyFont font-bold mt-[50px]">대표 상점 아이디</div>
        {/* input box */}
        <input
          className="w-full h-[46px] border-b border-black/80 hintFont p-1"
          placeholder="대표 상점 아이디를 입력하세요."
          value={storeId}
          onChange={(e) => setStoreId(e.target.value)}
        />
        <div className="hintFont text-[#6C6C6C]">
          연동 정보 페이지 상단에서 확인할 수 있어요.
        </div>

        {/* channel key */}
        <div className="bodyFont font-bold mt-[15px]">채널 키</div>
        {/* input box */}
        <input
          className="w-full h-[46px] border-b border-black/80 hintFont p-1"
          placeholder="채널 키를 입력하세요."
          value={chId}
          onChange={(e) => setChId(e.target.value)}
        />
        <div className="hintFont text-[#6C6C6C]">
          연동 정보 &gt; 채널 관리 탭에서 확인할 수 있어요.
        </div>
      </div>

      {!paymentExist ? (
        <div className="flex flex-col">
          {/* secret v2 key */}
          <div className="bodyFont font-bold mt-[15px]">시크릿 V2 API</div>
          {/* input box */}
          <input
            className="w-full h-[46px] border-b border-black/80 hintFont p-1"
            placeholder="채널 키를 입력해 주세요"
            value={secretKey}
            onChange={(e) => setSecretKey(e.target.value)}
          />
          <div className="hintFont text-[#6C6C6C]">
            연동 정보 &gt; 식별 코드 · API Keys &gt; V2 API 탭에서 확인하세요.
            <br />
            <br /> ※ 최초 발급 후에는 확인할 수 없으니 주의하세요. <br />※ 만료
            시 변경이 필요해요.
          </div>
        </div>
      ) : (
        // notice
        <div className="w-full hintFont bg-[#E7E7E7] rounded py-[20px] px-[8px]">
          <b>시크릿 V2 API 키 변경</b>이 필요한 경우 <br />
          cheapbob2025@gmail.com으로 문의해 주세요.
        </div>
      )}

      {/* save */}
      <CommonBtn
        label="저장"
        onClick={() => handleUpdatePayment()}
        category="green"
        notBottom
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
