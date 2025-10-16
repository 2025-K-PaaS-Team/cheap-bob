import { CommonBtn } from "@components/common";
import { dongData, siDoData, siGunGuData } from "@constant";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router";

const Location = () => {
  const navigate = useNavigate();
  const [selectedSiDo, setSelectedSiDo] = useState<string | null>(null);
  const [selectedSiGunGu, setSelectedSiGunGu] = useState<string | null>(null);
  const [selectedDongs, setSelectedDongs] = useState<Record<string, boolean>>(
    {}
  );

  useEffect(() => {
    const savedSiDo = localStorage.getItem("sido");
    const savedSiGunGu = localStorage.getItem("sigungu");
    const savedDongs = localStorage.getItem("dongs");

    if (savedSiDo) setSelectedSiDo(savedSiDo);
    if (savedSiGunGu) setSelectedSiGunGu(savedSiGunGu);
    if (savedDongs) setSelectedDongs(JSON.parse(savedDongs));
  }, []);

  // 로컬스토리지 저장
  const handleSelectLoc = () => {
    localStorage.setItem("sido", selectedSiDo || "");
    localStorage.setItem("sigungu", selectedSiGunGu || "");
    localStorage.setItem("dongs", JSON.stringify(selectedDongs));
    navigate(-1);
  };

  const allDongOption = "관악구 전체";

  // 현재 선택 가능한 동 리스트
  const currentDongs =
    selectedSiGunGu && dongData[selectedSiGunGu]
      ? [allDongOption, ...dongData[selectedSiGunGu]]
      : [];

  // 선택한 동 개수 (관악구 전체는 1로 카운트)
  const selectedDongKeys = Object.keys(selectedDongs).filter(
    (d) => selectedDongs[d]
  );

  // 동 선택 토글
  const handleDongClick = (dong: string) => {
    // 관악구 전체 선택 시
    if (dong === allDongOption) {
      setSelectedDongs({ [allDongOption]: true });
      return;
    }

    // 최대 10개 제한
    const currentSelectedCount = selectedDongKeys.filter(
      (d) => d !== allDongOption
    ).length;
    if (!selectedDongs[dong] && currentSelectedCount >= 10) return;

    setSelectedDongs((prev) => {
      const newSelected = { ...prev, [dong]: !prev[dong] };

      // 모든 동 선택 시 관악구 전체 자동 체크
      const allSelected = currentDongs
        .filter((d) => d !== allDongOption)
        .every((d) => newSelected[d]);
      if (allSelected) newSelected[allDongOption] = true;
      else newSelected[allDongOption] = false;

      // 관악구 전체 선택 상태에서 다른 동 선택 시 전체 해제
      if (newSelected[allDongOption] && dong !== allDongOption) {
        newSelected[allDongOption] = false;
      }

      return newSelected;
    });
  };

  // 개별 동 선택 제거
  const removeDong = (dong: string) => {
    setSelectedDongs((prev) => {
      const newSelected = { ...prev, [dong]: false };
      return newSelected;
    });
  };

  const maxRows = currentDongs.length || 1;
  const fillEmptyRows = (count: number) =>
    Array.from({ length: count }, (_, i) => (
      <div key={i} className="py-3"></div>
    ));

  return (
    <div className="flex w-full flex-col relative h-full">
      {/* notice */}
      <div className="bg-[#F0F0F0] text-[#6C6C6C] py-4 px-3 rounded mx-[20px] mb-[23px]">
        현재는 관악구 지역만 서비스하고 있어요.
      </div>

      {/* Header */}
      <div className="grid grid-cols-3">
        {["시 · 도", "시 · 군 · 구", "동 · 읍 · 면"].map((header, idx) => (
          <div
            key={idx}
            className={`text-center py-2 bg-[#F0F0F0] text-[11px] ${
              idx < 2 ? "border-r border-[#BFBFBF]" : ""
            }`}
          >
            {header}
          </div>
        ))}
      </div>

      {/* Content */}
      <div
        className={`grid grid-cols-3 ${
          Object.values(selectedDongs).some((v) => v)
            ? "max-h-[400px] overflow-y-auto"
            : "h-full"
        }`}
      >
        {/* 시·도 */}
        <div className="flex flex-col border-r border-[#BFBFBF]">
          {siDoData.map((si) => {
            const isActive = selectedSiDo === si;
            return (
              <div
                key={si}
                className={`flex items-center cursor-pointer w-full h-[32px] p-[10px] ${
                  isActive
                    ? "bg-main-deep font-bold text-white"
                    : "text-[#393939]"
                }`}
                onClick={() => {
                  setSelectedSiDo(si);
                  setSelectedSiGunGu(null);
                  setSelectedDongs({});
                }}
              >
                {si}
              </div>
            );
          })}
          {fillEmptyRows(maxRows - siDoData.length)}
        </div>

        {/* 시·군·구 */}
        <div className="flex flex-col border-r border-[#BFBFBF]">
          {selectedSiDo &&
            siGunGuData[selectedSiDo]?.map((gu) => {
              const isActive = selectedSiGunGu === gu;
              return (
                <div
                  key={gu}
                  className={`flex items-center cursor-pointer w-full h-[32px] p-[10px] ${
                    isActive
                      ? "bg-main-pale text-main-deep font-bold"
                      : "text-[#393939]"
                  }`}
                  onClick={() => {
                    setSelectedSiGunGu(gu);
                    setSelectedDongs({});
                  }}
                >
                  {gu}
                </div>
              );
            })}
          {fillEmptyRows(
            maxRows -
              (selectedSiDo ? siGunGuData[selectedSiDo]?.length || 0 : 0)
          )}
        </div>

        {/* 동·읍·면 */}
        <div className="flex flex-col">
          {currentDongs.map((dong) => {
            const isActive = selectedDongs[dong];
            return (
              <div
                key={dong}
                className={`flex items-center justify-between cursor-pointer w-full h-[32px] p-[10px] ${
                  isActive ? "text-main-deep font-bold" : "text-[#393939]"
                }`}
                onClick={() => handleDongClick(dong)}
              >
                <span>{dong}</span>
                {isActive && (
                  <img src="/icon/check.svg" alt="check" className="w-4 h-4" />
                )}
              </div>
            );
          })}
          {fillEmptyRows(maxRows - currentDongs.length)}
        </div>
      </div>

      {/* 선택한 동 하단 표시 */}
      {selectedDongKeys.length > 0 && (
        <div className="m-[20px] flex flex-col gap-[23px]">
          <div className="tagFont">
            {selectedDongs[allDongOption]
              ? "1 / 10"
              : `${Math.min(selectedDongKeys.length, 10)} / 10`}
          </div>
          <div className="flex flex-wrap gap-2 hintFont">
            {selectedDongs[allDongOption] ? (
              <div className="flex items-center gap-1 bg-main-pale text-main-deep border rounded px-3 py-1">
                {allDongOption}
                <img
                  src="/icon/crossGreen.svg"
                  alt="remove"
                  className="w-3 h-3 cursor-pointer"
                  onClick={() => removeDong(allDongOption)}
                />
              </div>
            ) : (
              selectedDongKeys.map((dong) => (
                <div
                  key={dong}
                  className="flex items-center gap-1 bg-main-pale text-main-deep border rounded px-3 py-1"
                >
                  {dong}
                  <img
                    src="/icon/cross.svg"
                    alt="remove"
                    className="w-3 h-3 cursor-pointer"
                    onClick={() => removeDong(dong)}
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
          notBottom
          category="white"
          className="w-full col-span-2"
          onClick={() => navigate(-1)}
        />
        <CommonBtn
          label="매장 고르기 (N개)"
          notBottom
          className="w-full col-span-3"
          onClick={() => handleSelectLoc()}
        />
      </div>
    </div>
  );
};

export default Location;
