import { CommonBtn, CommonModal } from "@components/common";
import { useState } from "react";
import { PostalCode } from "@components/seller/dashboard";
import { useNavigate } from "react-router";
import { UpdateStoreAddr } from "@services";
import { formatErrMsg } from "@utils";
import type { AddressInfoType } from "@interface";

const ChangeStoreAddr = () => {
  const initialAddr: AddressInfoType = {
    postal_code: "",
    address: "",
    detail_address: "",
    sido: "",
    sigungu: "",
    bname: "",
    lat: "",
    lng: "",
  };
  const navigate = useNavigate();
  const [addr, setAddr] = useState<AddressInfoType>(initialAddr);
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");

  const validateAddr = (a: AddressInfoType) => {
    if (!a.address || !a.postal_code) {
      setModalMsg("우편번호 찾기로 주소를 선택해 주세요.");
      setShowModal(true);
      return false;
    }
    if (!a.detail_address?.trim()) {
      setModalMsg("상세 주소를 입력해 주세요.");
      setShowModal(true);
      return false;
    }
    return true;
  };

  const handleSubmit = async () => {
    if (!validateAddr(addr)) return;
    try {
      await UpdateStoreAddr(addr);
      navigate(-1);
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    }
  };

  return (
    <div className="mt-[80px] px-[20px] w-full">
      {/* question */}
      <div className="text-[24px]">
        변경할 <span className="font-bold">매장 주소</span>를 <br /> 입력해
        주세요.
      </div>
      {/* postal code */}
      <PostalCode
        form={addr}
        setForm={(next) =>
          setAddr((prev) => ({
            ...prev,
            ...(typeof next === "function" ? next(prev ?? {}) : next),
          }))
        }
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

export default ChangeStoreAddr;
