import { siDoData, siGunGuData, dongData, ALL_DONG_OPTION } from "@constant";
import { CommonBtn, CommonLoading } from "@components/common";
import { useToast } from "@context";
import { useNavigate } from "react-router-dom";
import { useLocationState } from "@hooks/Customer/Location";
import { LocationHeader } from "@components/customer/location/LocationHeader";
import { LocationList } from "@components/customer/location/LocationList";
import { DongList } from "@components/customer/location/DongList";

const Location = () => {
  const { showToast } = useToast();
  const navigate = useNavigate();
  const {
    selectedSiDo,
    setSelectedSiDo,
    selectedSiGunGu,
    setSelectedSiGunGu,
    selectedDongs,
    setSelectedDongs,
    isLoading,
  } = useLocationState();

  const handleSelectLoc = () => {
    localStorage.setItem("sido", selectedSiDo || "");
    localStorage.setItem("sigungu", selectedSiGunGu || "");
    localStorage.setItem("dongs", JSON.stringify(selectedDongs));
    showToast("위치 설정에 성공했어요.", "success");
    navigate(-1);
  };

  const currentDongs =
    selectedSiGunGu && dongData[selectedSiGunGu]
      ? [ALL_DONG_OPTION, ...dongData[selectedSiGunGu]]
      : [];

  const selectedDongKeys = Object.keys(selectedDongs).filter(
    (d) => selectedDongs[d]
  );
  const maxRows = currentDongs.length || siDoData.length;

  const handleDongToggle = (dong: string) => {
    if (selectedDongs[ALL_DONG_OPTION] && dong !== ALL_DONG_OPTION) return;
    if (dong === ALL_DONG_OPTION) {
      setSelectedDongs({ [ALL_DONG_OPTION]: !selectedDongs[ALL_DONG_OPTION] });
      return;
    }
    const cnt = Object.keys(selectedDongs).filter(
      (d) => d !== ALL_DONG_OPTION && selectedDongs[d]
    ).length;
    if (!selectedDongs[dong] && cnt >= 10) return;
    setSelectedDongs((prev) => ({
      ...prev,
      [dong]: !prev[dong],
      [ALL_DONG_OPTION]: false,
    }));
  };

  const removeDong = (dong: string) =>
    setSelectedDongs((prev) => ({ ...prev, [dong]: false }));

  if (isLoading) return <CommonLoading type="data" isLoading={isLoading} />;

  return (
    <div className="flex w-full flex-col relative h-full">
      <div className="bg-[#F0F0F0] text-[#6C6C6C] py-4 px-3 rounded mx-[20px] mb-[23px]">
        현재는 관악구 지역만 서비스하고 있어요.
      </div>

      <LocationHeader />

      <div
        className={`grid grid-cols-3 overflow-y-scroll ${
          selectedDongKeys.length ? "max-h-[400px]" : "h-full"
        }`}
      >
        <LocationList
          items={siDoData}
          selected={selectedSiDo}
          onSelect={(si) => {
            setSelectedSiDo(si);
            setSelectedSiGunGu(null);
            setSelectedDongs({});
          }}
          maxRows={maxRows}
        />
        <LocationList
          items={selectedSiDo ? siGunGuData[selectedSiDo] || [] : []}
          selected={selectedSiGunGu}
          onSelect={(gu) => {
            setSelectedSiGunGu(gu);
            setSelectedDongs({});
          }}
          maxRows={maxRows}
        />
        <DongList
          dongs={currentDongs}
          selectedDongs={selectedDongs}
          onToggle={handleDongToggle}
          maxRows={maxRows}
        />
      </div>

      {selectedDongKeys.length > 0 && (
        <div className="m-[20px] flex flex-col gap-[23px]">
          <div className="tagFont">
            {selectedDongs[ALL_DONG_OPTION]
              ? "1 / 10"
              : `${selectedDongKeys.length} / 10`}
          </div>
          <div className="flex flex-wrap gap-2 hintFont">
            {selectedDongs[ALL_DONG_OPTION] ? (
              <div className="flex items-center gap-2 bg-main-pale text-main-deep border rounded px-3 py-1">
                <span>{ALL_DONG_OPTION}</span>
                <img
                  src="/icon/crossGreen.svg"
                  alt="remove"
                  className="w-3 h-3 cursor-pointer"
                  onClick={() => removeDong(ALL_DONG_OPTION)}
                />
              </div>
            ) : (
              selectedDongKeys.map((d) => (
                <div
                  key={d}
                  className="flex items-center gap-2 bg-main-pale text-main-deep border rounded px-3 py-1"
                >
                  <span>{d}</span>
                  <img
                    src="/icon/crossGreen.svg"
                    alt="remove"
                    className="w-3 h-3 cursor-pointer"
                    onClick={() => removeDong(d)}
                  />
                </div>
              ))
            )}
          </div>
        </div>
      )}

      <div className="grid grid-cols-5 mx-[20px] gap-x-[10px] my-[30px]">
        <CommonBtn
          label="이전"
          category="white"
          className="w-full col-span-2"
          onClick={() => navigate(-1)}
        />
        <CommonBtn
          label="위치 설정"
          className="w-full col-span-3"
          onClick={handleSelectLoc}
        />
      </div>
    </div>
  );
};

export default Location;
