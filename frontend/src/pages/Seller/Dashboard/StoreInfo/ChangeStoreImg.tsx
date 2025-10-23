import { CommonBtn, CommonModal } from "@components/common";
import CommonLoading from "@components/common/CommonLoading";
import { useToast } from "@context";
import type { ImageInfoType } from "@interface";
import {
  AddStoreImg,
  ChangeStoreMainImg,
  DeleteStoreImg,
  GetStoreImg,
} from "@services";
import { formatErrMsg } from "@utils";
import React, { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

const ChangeStoreImg = () => {
  const { showToast } = useToast();
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const navigate = useNavigate();
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");
  const [imgs, setImgs] = useState<ImageInfoType[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const handleSubmit = () => {
    showToast("이미지 등록에 성공했어요.", "success");
    navigate(-1);
  };

  const handleGetStoreImg = async () => {
    try {
      const res = await GetStoreImg();
      setImgs(res.images ?? []);
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    }
  };

  const handleClickUpload = (isMain = false) => {
    fileInputRef.current!.dataset.isMain = isMain ? "true" : "false";
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    setIsLoading(true);
    const files = e.target.files ? Array.from(e.target.files).slice(0, 5) : [];
    if (files.length === 0) return;

    const isMain = fileInputRef.current?.dataset.isMain === "true";

    // 일반 사진일 경우 10개 제한 체크
    if (!isMain) {
      const currentCount = imgs.length - 1;
      if (currentCount + files.length > 10) {
        setModalMsg("제품 사진은 최대 10장까지 등록 가능합니다.");
        setShowModal(true);
        e.target.value = "";
        return;
      }
    }

    const ALLOWED = ["image/jpeg", "image/jpg", "image/png", "image/webp"];
    const MAX = 5 * 1024 * 1024;

    for (const f of files) {
      if (!ALLOWED.includes(f.type)) {
        setModalMsg("지원 형식: JPG, JPEG, PNG, WEBP");
        setShowModal(true);
        e.target.value = "";
        return;
      }
      if (f.size > MAX) {
        setModalMsg("최대 크기 10MB를 초과했습니다.");
        setShowModal(true);
        e.target.value = "";
        return;
      }
    }

    // 업로드 전 기존 이미지 리스트 저장
    const oldImgs = [...imgs];

    // 업로드
    try {
      const res = await AddStoreImg(files);
      const newImgs = res.images ?? [];
      setImgs(newImgs);

      // 선택한 파일이 대표 사진 변경용이면 새로 추가된 이미지 찾기
      if (fileInputRef.current?.dataset.isMain === "true") {
        const newImage = newImgs.find(
          (img) => !oldImgs.some((old) => old.image_id === img.image_id)
        );
        if (newImage) {
          try {
            await ChangeStoreMainImg(newImage.image_id);
            await handleGetStoreImg();
          } catch (err) {
            setModalMsg(formatErrMsg(err));
            setShowModal(true);
          }
        }
      }
    } catch (err) {
      console.log(err);
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    } finally {
      setIsLoading(false);
      e.target.value = "";
    }
  };

  const handleClickDelete = async (image_id: string) => {
    try {
      await DeleteStoreImg(image_id);
      await handleGetStoreImg();
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    }
  };

  useEffect(() => {
    const init = async () => {
      await handleGetStoreImg();
      setIsLoading(false);
    };
    init();
  }, []);

  if (isLoading || !imgs || imgs.length == 0) {
    return <CommonLoading type="data" isLoading={isLoading} />;
  }

  return (
    <div className="mt-[30px] px-[20px] w-full gap-y-[40px] flex flex-col">
      {/* question */}
      <div className="titleFont">
        변경할 <span className="font-bold">이미지</span>를 <br /> 등록해 주세요.
      </div>

      {/* represent image */}
      <div className="flex flex-col gap-y-[20px]">
        <div className="w-full h-[125px] overflow-hidden">
          <img
            src={imgs[0].image_url}
            alt="representImg"
            className="w-full h-full object-cover object-center"
          />
        </div>

        <div className="w-full flex justify-center">
          <CommonBtn
            label="대표 사진 변경"
            notBottom
            onClick={() => handleClickUpload(true)}
            className="btnFont"
            category="white"
          />
        </div>
      </div>

      {/* notice */}
      <div className="hintFont bg-[#E7E7E7] rounded py-[20px] px-[8px]">
        <span className="font-bold">가게 외부 사진</span>을 대표 사진으로
        등록하면
        <br /> 손님들이 가게를 더 잘 찾아오실 수 있어요.
      </div>

      {/* other image */}
      <div className="flex flex-col gap-y-[20px]">
        <h2>다른 사진도 있나요?</h2>
        {/* preview */}
        {imgs.length > 1 && imgs ? (
          <div className="grid grid-cols-3 gap-2">
            {imgs.slice(1).map((img, idx) => (
              <div className="relative" key={idx}>
                <img
                  key={idx}
                  src={img.image_url}
                  alt={`img-${idx}`}
                  className="w-full h-[100px] object-cover"
                />
                <button
                  type="button"
                  onClick={() => handleClickDelete(img.image_id)}
                  className="absolute top-1 right-1 text-white text-xs w-5 h-5 flex items-center justify-center"
                >
                  <img src="/icon/crossWhite.svg" alt="crossIcon" />
                </button>
              </div>
            ))}
          </div>
        ) : (
          <div className="relative h-[100px]">
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 flex flex-col">
              <div className="hintFont text-custom-black">
                등록된 사진이 없어요.
              </div>
            </div>
          </div>
        )}
        {/* upload picture button */}
        <div className="w-full flex justify-center">
          <CommonBtn
            label={`제품 사진 등록 (${imgs.length - 1}/10)`}
            notBottom
            onClick={() => handleClickUpload(false)}
            className="btnFont"
            category="white"
          />
        </div>
        <input
          type="file"
          accept="image/*"
          ref={fileInputRef}
          className="hidden"
          onChange={handleFileChange}
        />
      </div>

      {/* save */}
      <CommonBtn
        label="저장"
        onClick={handleSubmit}
        category="green"
        notBottom
        className="w-[350px] flex w-full justify-center mb-[50px]"
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

export default ChangeStoreImg;
