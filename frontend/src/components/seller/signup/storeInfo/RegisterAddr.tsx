import { CommonBtn, CommonModal } from "@components/common";
import { NearStation, PostalCode } from "@components/seller/dashboard";
import type { AddressInfoType, SellerSignupProps } from "@interface";
import { useSignupStore } from "@store";
import { validationRules } from "@utils";
import { useState } from "react";

const RegisterAddr = ({ pageIdx, setPageIdx }: SellerSignupProps) => {
  const { form } = useSignupStore();
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");
  const [selectedStation, setSelectStation] = useState<string>("");
  const [stationTime, setStationTime] = useState<string>("");
  const { storeAddr } = validationRules;

  const setAddr: React.Dispatch<React.SetStateAction<AddressInfoType>> = (
    next
  ) => {
    useSignupStore.getState().setForm((prev) => ({
      address_info:
        typeof next === "function"
          ? (next as (p: AddressInfoType) => AddressInfoType)(prev.address_info)
          : { ...prev.address_info, ...next },
    }));
  };

  const handleClickNext = () => {
    if (!form.address_info.address || !form.address_info.postal_code) {
      setModalMsg(storeAddr.errorMessage);
      setShowModal(true);
      return;
    }

    if (!form.address_info.detail_address?.trim()) {
      setModalMsg("상세 주소를 입력해 주세요.");
      setShowModal(true);
      return;
    }

    setPageIdx(pageIdx + 1);
  };

  const handleClickPrev = () => {
    setPageIdx(pageIdx - 1);
  };

  return (
    <div className="mx-[20px] mt-[20px] flex flex-col gap-y-[40px]">
      <div className="text-main-deep font-bold bodyFont">4/5</div>
      <div className="titleFont">
        <span className="font-bold">매장 위치</span>를 입력해 주세요.
      </div>

      {/* postal code */}
      <PostalCode
        form={form.address_info}
        setForm={(addrForm) => {
          useSignupStore.getState().setForm((prev) => ({
            address_info: {
              ...prev.address_info,
              ...(typeof addrForm === "function"
                ? addrForm(prev.address_info)
                : addrForm),
            },
          }));
        }}
      />

      {/* near station */}
      <NearStation
        setAddr={setAddr}
        setStationTime={setStationTime}
        stationTime={stationTime}
        selectedStation={selectedStation}
        setSelectStation={setSelectStation}
      />

      <CommonBtn
        category="transparent"
        label="이전"
        onClick={() => handleClickPrev()}
        notBottom
        className="absolute left-[20px] bottom-[38px]"
        width="w-[100px]"
      />
      <CommonBtn
        category={
          !form.address_info.address ||
          !form.address_info.detail_address ||
          !selectedStation ||
          !stationTime
            ? "grey"
            : "green"
        }
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
          onConfirmClick={() => setShowModal(false)}
          category="green"
        />
      )}
    </div>
  );
};

export default RegisterAddr;
