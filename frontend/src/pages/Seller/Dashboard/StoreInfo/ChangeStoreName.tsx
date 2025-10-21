import { CommonBtn, CommonModal } from "@components/common";
import CommonLoading from "@components/common/CommonLoading";
import { GetStoreDetail, UpdateStoreName } from "@services";
import { formatErrMsg, validateLength } from "@utils";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router";

const ChangeStoreName = ({}) => {
  const [value, setValue] = useState<string>("");
  const navigate = useNavigate();
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");
  const [isLoading, setIsLoading] = useState<boolean>(true);

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

  useEffect(() => {
    const handleGetStore = async () => {
      try {
        const res = await GetStoreDetail();
        setValue(res.store_name);
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

  return (
    <div className="my-[30px] px-[20px] w-full flex-1 flex flex-col">
      <div className="flex flex-col flex-1 gap-y-[40px]">
        {/* question */}
        <div className="titleFont">
          변경할 <span className="font-bold">매장 이름</span>을 <br /> 입력해
          주세요.
        </div>
        {/* input box */}
        <input
          className="w-full h-[46px] border-b  border-[#393939] text-[16px]"
          placeholder="매장 이름을 입력해 주세요"
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

export default ChangeStoreName;
