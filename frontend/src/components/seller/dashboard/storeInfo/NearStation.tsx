import { CommonBtn, CommonModal } from "@components/common";
import { NearStationList } from "@constant";
import type { AddressInfoType } from "@interface";
import { useState } from "react";

interface NearStationProps {
  setStationTime: (time: string) => void;
  stationTime: string;
  selectedStation: string;
  setSelectStation: (station: string) => void;
  setAddr: React.Dispatch<React.SetStateAction<AddressInfoType>>;
}

const NearStation = ({
  setStationTime,
  stationTime,
  selectedStation,
  setSelectStation,
  setAddr,
}: NearStationProps) => {
  const [openStation, setOpenStation] = useState<boolean>(false);

  const handleStationTimeChange = (raw: string) => {
    const onlyNum = raw.replace(/\D/g, "").slice(0, 2);
    setStationTime(onlyNum);
  };

  return (
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
    </div>
  );
};

export default NearStation;
