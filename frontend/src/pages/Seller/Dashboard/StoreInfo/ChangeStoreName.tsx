import { CommonBtn, CommonModal } from "@components/common";
import { UpdateStoreName } from "@services";
import { formatErrMsg, validateLength } from "@utils";
import { useState } from "react";
import { useNavigate } from "react-router";

const ChangeStoreName = ({}) => {
  const [value, setValue] = useState<string>("");
  const navigate = useNavigate();
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");

  const handleUpdateStoreName = async (storeName: string) => {
    const validMsg = "매장 이름은 1~7자여야 합니다.";

    if (!validateLength(value, 1, 7)) {
      setModalMsg(validMsg);
      setShowModal(true);
      return;
    }

    try {
      await UpdateStoreName(storeName);
      navigate(-1);
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    }
  };

  const handleSubmit = () => {
    handleUpdateStoreName(value);
  };

  return (
    <div className="mt-[80px] px-[20px] w-full">
      {/* question */}
      <div className="text-[24px]">
        변경할 <span className="font-bold">매장 이름</span>을 <br /> 입력해
        주세요.
      </div>
      {/* input box */}
      <input
        className="w-full h-[46px] text-center bg-[#D9D9D9] text-[16px] mt-[40px]"
        placeholder="매장 이름을 입력해 주세요"
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

export default ChangeStoreName;
