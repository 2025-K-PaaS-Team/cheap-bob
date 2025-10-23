import { CommonBtn, CommonModal } from "@components/common";
import CommonLoading from "@components/common/CommonLoading";
import { useToast } from "@context";
import { GetStoreDetail, UpdateStoreDesc } from "@services";
import { formatErrMsg, validateLength } from "@utils";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const ChangeStoreDesc = () => {
  const { showToast } = useToast();
  const [value, setValue] = useState<string>("");
  const navigate = useNavigate();
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const handleGetStore = async () => {
      try {
        const res = await GetStoreDetail();
        setValue(res.store_introduction);
        setIsLoading(false);
      } catch (err) {
        console.error(formatErrMsg(err));
      }
    };

    handleGetStore();
  }, []);

  if (isLoading) {
    return <CommonLoading type="data" isLoading={isLoading} />;
  }

  const handleUpdateStoreDesc = async (storeName: string) => {
    const validMsg = "매장 설명은 1~100자여야 합니다.";

    if (!validateLength(value, 1, 100)) {
      setModalMsg(validMsg);
      setShowModal(true);
      return;
    }

    try {
      await UpdateStoreDesc(storeName);
      showToast("매장 소개 변경에 성공했어요.", "success");
      navigate(-1);
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    }
  };

  const handleSubmit = () => {
    handleUpdateStoreDesc(value);
  };

  return (
    <div className="my-[30px] px-[20px] w-full flex flex-1 flex-col">
      <div className="flex flex-col flex-1 gap-y-[40px]">
        {/* question */}
        <div className="titleFont">
          변경할 <span className="font-bold">매장 설명</span>을 <br /> 입력해
          주세요.
        </div>
        {/* input box */}
        <textarea
          className="w-full h-[145px] rounded border border-[#E7E7E7] text-[16px] p-[8px]"
          placeholder="매장 설명을 입력해 주세요"
          value={value}
          onChange={(e) => setValue(e.target.value)}
        />
      </div>

      {/* save */}
      <CommonBtn
        label="저장"
        onClick={handleSubmit}
        notBottom
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

export default ChangeStoreDesc;
