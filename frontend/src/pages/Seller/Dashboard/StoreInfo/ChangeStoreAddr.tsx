import { CommonBtn, CommonModal } from "@components/common";
import { useEffect, useState } from "react";
import { NearStation, PostalCode } from "@components/seller/dashboard";
import { useNavigate } from "react-router-dom";
import { GetStoreDetail, UpdateStoreAddr } from "@services";
import { formatErrMsg } from "@utils";
import type { AddressInfoType } from "@interface";
import CommonLoading from "@components/common/CommonLoading";
import { useToast } from "@context";

const ChangeStoreAddr = () => {
  const { showToast } = useToast();
  const initialAddr: AddressInfoType = {
    postal_code: "",
    address: "",
    detail_address: "",
    sido: "",
    sigungu: "",
    bname: "",
    lat: "",
    lng: "",
    nearest_station: "",
    walking_time: 0,
  };

  const navigate = useNavigate();
  const [addr, setAddr] = useState<AddressInfoType>(initialAddr);

  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");

  const [selectedStation, setSelectStation] = useState<string>("");
  const [stationTime, setStationTime] = useState<string>("");

  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const handleGetStore = async () => {
      try {
        const res = await GetStoreDetail();
        const a: AddressInfoType = res.address ?? initialAddr;
        setAddr(a);
        setSelectStation(a.nearest_station || "");
        setStationTime(a.walking_time ? String(a.walking_time) : "");
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
    const payload: AddressInfoType = {
      ...addr,
      nearest_station: selectedStation || "",
      walking_time: stationTime ? Number(stationTime) : 0,
    };

    if (!validateAddr(payload)) return;

    try {
      await UpdateStoreAddr(payload);
      showToast("주소 변경에 성공했어요.", "success");
      navigate(-1);
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    }
  };

  return (
    <div className="my-[30px] px-[20px] w-full flex flex-col flex-1">
      <div className="flex flex-col gap-y-[40px] flex-1">
        {/* question */}
        <div className="titleFont">
          변경할 <span className="font-bold">매장 주소</span>를 <br /> 입력해
          주세요.
        </div>

        {/* postal code */}
        <PostalCode
          form={addr}
          setForm={(next) =>
            setAddr((prev) => ({
              ...prev,
              ...(typeof next === "function"
                ? next(prev ?? ({} as AddressInfoType))
                : next),
            }))
          }
        />

        <NearStation
          setAddr={setAddr}
          setStationTime={setStationTime}
          stationTime={stationTime}
          selectedStation={selectedStation}
          setSelectStation={setSelectStation}
        />
      </div>

      {/* save */}
      <CommonBtn
        label="저장"
        onClick={handleSubmit}
        notBottom
        category="green"
      />

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

export default ChangeStoreAddr;
