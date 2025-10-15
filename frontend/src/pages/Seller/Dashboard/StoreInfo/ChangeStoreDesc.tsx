import { CommonBtn, CommonModal } from "@components/common";
import { UpdateStoreDesc } from "@services";
import { formatErrMsg, validateLength } from "@utils";
import { useState } from "react";
import { useNavigate } from "react-router";

const ChangeStoreDesc = () => {
  const [value, setValue] = useState<string>("");
  const navigate = useNavigate();
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");

  const handleUpdateStoreDesc = async (storeName: string) => {
    const validMsg = "매장 설명은 1~100자여야 합니다.";

    if (!validateLength(value, 1, 100)) {
      setModalMsg(validMsg);
      setShowModal(true);
      return;
    }

    try {
      await UpdateStoreDesc(storeName);
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
    <div className="mt-[80px] px-[20px] w-full">
      {/* question */}
      <div className="text-[24px]">
        변경할 <span className="font-bold">매장 설명</span>을 <br /> 입력해
        주세요.
      </div>
      {/* input box */}
      <input
        className="w-full h-[100px] text-center bg-custom-white text-[16px] mt-[40px]"
        placeholder="매장 설명을 입력해 주세요"
        value={value}
        onChange={(e) => setValue(e.target.value)}
      />

      {/* save */}
      <CommonBtn label="저장" onClick={handleSubmit} category="black" />

      {/* show modal */}
      {showModal && (
        <CommonModal
          desc={modalMsg}
          confirmLabel="확인"
          onConfirmClick={() => setShowModal(false)}
          category="black"
        />
      )}
    </div>
  );
};

export default ChangeStoreDesc;
