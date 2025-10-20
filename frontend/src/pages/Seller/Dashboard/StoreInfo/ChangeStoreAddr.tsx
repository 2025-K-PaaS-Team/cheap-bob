import { CommonBtn, CommonModal } from "@components/common";
import { useEffect, useState } from "react";
import { PostalCode } from "@components/seller/dashboard";
import { useNavigate } from "react-router";
import { GetStoreDetail, UpdateStoreAddr } from "@services";
import { formatErrMsg } from "@utils";
import type { AddressInfoType } from "@interface";
import { NearStationList } from "@constant";

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
    nearest_station: "",
    walking_time: 0,
  };

  const navigate = useNavigate();
  const [addr, setAddr] = useState<AddressInfoType>(initialAddr);

  // 모달들
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");
  const [openStation, setOpenStation] = useState<boolean>(false);

  const [selectedStation, setSelectStation] = useState<string>("");
  const [stationTime, setStationTime] = useState<string>("");

  useEffect(() => {
    const handleGetStore = async () => {
      try {
        const res = await GetStoreDetail();
        const a: AddressInfoType = res.address ?? initialAddr;
        setAddr(a);
        setSelectStation(a.nearest_station || "");
        setStationTime(a.walking_time ? String(a.walking_time) : "");
      } catch (err) {
        console.error(formatErrMsg(err));
      }
    };
    handleGetStore();
  }, []);

  const handleStationTimeChange = (raw: string) => {
    const onlyNum = raw.replace(/\D/g, "").slice(0, 2);
    setStationTime(onlyNum);
  };

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

        <div className="flex flex-col gap-y-[20px]">
          <h2>가장 가까운 역은 어디인가요?</h2>

          {selectedStation ? (
            <div className="flex flex-row gap-x-[5px] items-center hintFont">
              <div className="max-w-[122px]">
                <CommonBtn
                  notBottom
                  onClick={() => setOpenStation(true)}
                  label={selectedStation}
                  category="pale-green"
                  className="w-fit h-fit px-[16px] py-[8px] tagFont rounded-sm"
                />
              </div>
              <div>에서 도보로</div>
              <div className="border-b border-[#393939] w-[30px]">
                <input
                  type="text"
                  value={stationTime}
                  onChange={(e) => handleStationTimeChange(e.target.value)}
                  className="w-full text-center"
                  maxLength={2}
                  inputMode="numeric"
                  pattern="[0-9]*"
                />
              </div>
              <div>분 걸려요.</div>
            </div>
          ) : (
            <div className="max-w-[122px]">
              <CommonBtn
                notBottom
                label="역을 선택해주세요."
                category="pale-green"
                className="w-fit h-fit p-[8px] tagFont rounded-sm"
                onClick={() => setOpenStation(true)}
              />
            </div>
          )}
        </div>
      </div>

      {/* save */}
      <CommonBtn
        label="저장"
        onClick={handleSubmit}
        notBottom
        category="green"
      />

      {/* 역 선택 모달 */}
      {openStation && (
        <CommonModal
          confirmLabel="확인"
          onConfirmClick={() => {
            setOpenStation(false);
            setAddr((prev) => ({
              ...prev,
              nearest_station: selectedStation || "",
              walking_time: stationTime ? Number(stationTime) : 0,
            }));
          }}
          onCancelClick={() => setOpenStation(false)}
          category="green"
          className="text-start"
        >
          <div className="flex flex-col max-h-[150px] mt-[5px] overflow-y-auto bodyFont gap-y-[10px]">
            <div className="font-bold">역을 선택해주세요</div>
            <div className="flex flex-col">
              {NearStationList.map((station, idx) => (
                <div
                  key={idx}
                  onClick={() => setSelectStation(station)}
                  className={`min-h-[36px] p-1 cursor-pointer ${
                    station === selectedStation
                      ? "font-bold bg-custom-white"
                      : ""
                  }`}
                >
                  {station}
                </div>
              ))}
            </div>
          </div>
        </CommonModal>
      )}

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
