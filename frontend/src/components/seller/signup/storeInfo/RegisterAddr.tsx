import { CommonBtn, CommonModal } from "@components/common";
import { PostalCode } from "@components/seller/dashboard";
import { NearStationList } from "@constant";
import type { SellerSignupProps } from "@interface";
import { useSignupStore } from "@store";
import { validationRules } from "@utils";
import { useState } from "react";

const RegisterAddr = ({ pageIdx, setPageIdx }: SellerSignupProps) => {
  const { form } = useSignupStore();
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");
  const [openStation, setOpenStation] = useState<boolean>(false);
  const [selectedStation, setSelectStation] = useState<string>("");
  const [stationTime, setStationTime] = useState<string>("");
  const { storeAddr } = validationRules;

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
      <div className="flex flex-col gap-y-[20px]">
        <h2>가장 가까운 역은 어디인가요?</h2>
        {selectedStation ? (
          <div className="flex flex-row gap-x-[5px] items-center">
            <CommonBtn
              notBottom
              label={selectedStation}
              category="pale-green"
              className="w-fit h-fit px-[16px] py-[8px] tagFont rounded-sm"
            />
            <div>에서 도보로</div>
            <div className="border-b border-[#393939] w-[30px]">
              <input
                type="text"
                value={stationTime}
                onChange={(e) => setStationTime(e.target.value)}
                className="w-full text-center"
                maxLength={2}
                pattern="[0-9]*"
              />
            </div>

            <div>분 걸려요.</div>
          </div>
        ) : (
          <CommonBtn
            notBottom
            label="역을 선택해주세요."
            category="pale-green"
            className="w-fit h-fit px-[16px] py-[8px] tagFont rounded-sm"
            onClick={() => setOpenStation(true)}
          />
        )}
      </div>

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

      {/* show station modal */}
      {openStation && (
        <CommonModal
          desc="역을 선택해주세요."
          confirmLabel="확인"
          onConfirmClick={() => setOpenStation(false)}
          category="green"
          className="text-start"
        >
          <div className="flex flex-col max-h-[150px] mt-[5px] overflow-y-auto bodyFont">
            {NearStationList.map((station, idx) => (
              <div
                key={idx}
                onClick={() => setSelectStation(station)}
                className={`min-h-[36px] p-1 ${
                  station === selectedStation && "font-bold bg-custom-white"
                }`}
              >
                {station}
              </div>
            ))}
          </div>
        </CommonModal>
      )}

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
