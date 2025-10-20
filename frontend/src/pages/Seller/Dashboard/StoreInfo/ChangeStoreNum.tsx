import { CommonBtn, CommonModal } from "@components/common";
import type { SnsInfoType } from "@interface";
import { GetStoreDetail, UpdateStorePhone, UpdateStoreSns } from "@services";
import { formatErrMsg, normalizeUrl, validatePattern } from "@utils";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router";

const ChangeStoreNum = () => {
  const [value, setValue] = useState<string>("");
  const [sns, setSns] = useState<SnsInfoType>({});
  const navigate = useNavigate();
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");

  useEffect(() => {
    const handleGetStore = async () => {
      try {
        const res = await GetStoreDetail();
        setValue(res.store_phone);
        setSns(res.sns);
      } catch (err) {
        console.error(formatErrMsg(err));
      }
    };

    handleGetStore();
  }, []);

  const handleUpdateStoreDesc = async (storePhone: string) => {
    const validMsg = "01012345678 형식으로 입력해 주세요.";
    const validPattern = /^0\d{1,2}\d{3,4}\d{4}$/;

    if (!validatePattern(value, validPattern)) {
      setModalMsg(validMsg);
      setShowModal(true);
      return;
    }

    try {
      await UpdateStorePhone(storePhone);
      return true;
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
      return false;
    }
  };

  const handleUpdateStoreSns = async (sns: SnsInfoType) => {
    try {
      await UpdateStoreSns(sns);
      return true;
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
      return false;
    }
  };

  const handleSubmit = async () => {
    try {
      const okDesc = await handleUpdateStoreDesc(value);
      if (!okDesc) return;

      const okSns = await handleUpdateStoreSns(sns);
      if (!okSns) return;

      navigate(-1);
    } catch {
      return;
    }
  };

  return (
    <div className="mt-[30px] px-[20px] w-full">
      {/* question */}
      <div className="titleFont">
        변경할 <span className="font-bold">매장 연락처</span>를 <br /> 입력해
        주세요.
      </div>
      {/* input box */}
      <div className="mt-[40px] gap-y-[11px]">
        <h3>
          매장 전화번호 <span className="text-sub-orange">(필수)</span>
        </h3>
        <input
          className="w-full h-[46px] border-b  border-[#393939] text-[16px]"
          placeholder="매장 전화번호를 입력해 주세요"
          value={value}
          onChange={(e) => setValue(e.target.value)}
        />
      </div>

      {/* other sns */}
      <div className="mt-[39px] flex flex-col gap-y-[11px]">
        <div className="text-[20px]">다른 연락처도 있나요?</div>
        <div className="flex flex-row">
          <div className="text-[14px] w-[97px] flex items-center">홈페이지</div>
          <input
            className="w-full h-[46px] border-b  border-[#393939] text-[16px]"
            value={sns?.homepage}
            onChange={(e) =>
              setSns((prev) => ({ ...prev, homepage: e.target.value }))
            }
            onBlur={(e) =>
              setSns((prev) => ({
                ...prev,
                homepage: normalizeUrl(e.target.value),
              }))
            }
          />
        </div>
        <div className="flex flex-row">
          <div className="text-[14px] w-[97px] flex items-center">
            인스타그램
          </div>
          <input
            className="w-full h-[46px] border-b  border-[#393939] text-[16px]"
            value={sns?.instagram}
            onChange={(e) =>
              setSns((prev) => ({ ...prev, instagram: e.target.value }))
            }
            onBlur={(e) =>
              setSns((prev) => ({
                ...prev,
                instagram: normalizeUrl(e.target.value),
              }))
            }
          />
        </div>
        <div className="flex flex-row">
          <div className="text-[14px] w-[97px] flex items-center">
            X (Twitter)
          </div>
          <input
            className="w-full h-[46px] border-b  border-[#393939] text-[16px]"
            value={sns?.x}
            onChange={(e) => setSns((prev) => ({ ...prev, x: e.target.value }))}
            onBlur={(e) =>
              setSns((prev) => ({
                ...prev,
                x: normalizeUrl(e.target.value),
              }))
            }
          />
        </div>
      </div>

      {/* save */}
      <CommonBtn label="저장" onClick={handleSubmit} category="green" />

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

export default ChangeStoreNum;
