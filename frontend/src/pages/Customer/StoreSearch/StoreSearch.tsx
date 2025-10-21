import { useEffect, useState } from "react";
import {
  DeleteSearchByName,
  GetSearchHistory,
  GetStoreByName,
} from "@services";
import { CommonModal } from "@components/common";
import { StoreBox } from "@components/customer/storeList";
import type { StoreSearchType } from "@interface";

let debounceTimer: NodeJS.Timeout;

const StoreSearch = () => {
  const [history, setHistory] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [modalMsg, setModalMsg] = useState("");
  const [nameResult, setNameResult] = useState<StoreSearchType | null>(null);
  const [value, setValue] = useState("");

  const handleGetNameSearch = async (name: string, pageIdx: number) => {
    if (isLoading || !name.trim()) return;
    try {
      setIsLoading(true);
      const res = await GetStoreByName(name, pageIdx);
      setNameResult(res);
    } catch {
      setModalMsg("검색에 실패했습니다.");
      setShowModal(true);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    clearTimeout(debounceTimer);

    if (!value.trim()) {
      setNameResult(null);
      handleGetHistory();
      return;
    }

    debounceTimer = setTimeout(() => {
      handleGetNameSearch(value, 0);
    }, 1000);
  }, [value]);

  const handleDeleteSearch = async (word: string) => {
    if (isLoading) return;
    try {
      setIsLoading(true);
      await DeleteSearchByName(word);
      handleGetHistory();
    } catch {
      setModalMsg("검색 기록 삭제에 실패했습니다.");
      setShowModal(true);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGetHistory = async () => {
    if (isLoading) return;
    try {
      setIsLoading(true);
      const res = await GetSearchHistory();
      setHistory(res?.search_names ?? []);
    } catch {
      setModalMsg("검색 기록 불러오기에 실패했습니다.");
      setShowModal(true);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    handleGetHistory();
  }, []);

  return (
    <div className="flex flex-col px-[20px]">
      {/* search bar */}
      <div className="border border-1 border-main-deep flex flex-row justify-between px-[18px] py-[16px] h-[54px] rounded-[50px]">
        <input
          type="text"
          className="focus:outline-none w-full"
          placeholder="가게명, 랜덤팩명을 검색하세요"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              handleGetNameSearch(value, 0);
            }
          }}
        />
        <img
          src="/icon/search.svg"
          alt="searchIcon"
          className="cursor-pointer"
          onClick={() => handleGetNameSearch(value, 0)}
        />
      </div>

      {/* search history */}
      <div className="flex flex-col gap-y-[23px] mt-[40px]">
        {nameResult ? (
          nameResult.stores && nameResult.stores.length > 0 ? (
            <StoreBox stores={nameResult.stores} />
          ) : (
            <div className="bodyFont text-center flex flex-col justify-center items-center gap-y-[24px] pt-[100px]">
              <img src="/icon/angrySalad.svg" alt="angrySald" width="116px" />
              <div>검색 결과가 없어요</div>
            </div>
          )
        ) : (
          <>
            <div className="bodyFont font-bold">최근 검색</div>
            {history.length === 0 ? (
              <div className="bodyFont text-center flex flex-col justify-center items-center gap-y-[24px] pt-[100px]">
                <img src="/icon/angrySalad.svg" alt="angrySald" width="116px" />
                <div>검색 기록이 없어요</div>
              </div>
            ) : (
              <div className="flex flex-col gap-y-[12px]">
                {history.map((word, idx) => (
                  <div
                    key={idx}
                    className="cursor-pointer text-custom-black justify-between flex flex-row"
                  >
                    <div onClick={() => handleGetNameSearch(word, 0)}>
                      {word}
                    </div>
                    <img
                      src="/icon/crossGrey.svg"
                      alt="cross"
                      onClick={() => handleDeleteSearch(word)}
                    />
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>

      {/* modal */}
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

export default StoreSearch;
