import { CommonBtn, CommonModal } from "@components/common";
import type { ImageInfoType } from "@interface";
import { AddStoreImg, DeleteStoreImg, GetStoreImg } from "@services";
import { formatErrMsg } from "@utils";
import axios from "axios";
import React, { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router";

const ChangeStoreImg = () => {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const navigate = useNavigate();
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");
  const [imgs, setImgs] = useState<ImageInfoType[]>([]);

  const handleSubmit = () => {
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

  const handleAddStoreImg = async (files: File[]) => {
    try {
      const res = await AddStoreImg(files);
      setImgs(res.images ?? []);
    } catch (err) {
      if (axios.isAxiosError(err)) {
        setModalMsg(
          "업로드 중 에러가 발생했습니다. 파일 크기를 확인해 주세요.(최대 10MB)"
        );
        setShowModal(true);
        return;
      }
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    }
  };

  const handleClickUpload = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const list = e.target.files;
    if (!list) return;

    const files = Array.from(list).slice(0, 5);

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

    await handleAddStoreImg(files);
    e.target.value = "";
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
    handleGetStoreImg();
  }, []);

  return (
    <div className="mt-[30px] px-[20px] w-full">
      {/* question */}
      <div className="text-[24px] mb-[44px]">
        변경할 <span className="font-bold">이미지</span>를 <br /> 등록해 주세요.
      </div>

      {/* represent image */}
      <img src="" alt="" />

      <div className="w-full flex justify-center">
        <CommonBtn
          label="대표 사진 변경"
          notBottom
          onClick={handleClickUpload}
          className="border-[#999999] font-normal"
          category="white"
        />
      </div>

      {/* notice */}
      <div className="hint bg-[#E7E7E7] rounded py-[20px] px-[8px] mt-[20px] mb-[40px]">
        <span className="font-bold">가게 외부 사진</span>을 대표 사진으로
        등록하면
        <br /> 손님들이 가게를 더 잘 찾아오실 수 있어요.
      </div>

      {/* other image */}
      <h2>다른 사진도 있나요?</h2>

      {/* upload picture button */}
      <div className="w-full flex justify-center py-[20px]">
        <CommonBtn
          label="제품 사진 등록 (0/10)"
          notBottom
          onClick={handleClickUpload}
          className="border-[#999999] font-normal"
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

      {/* preview */}
      {imgs.length > 0 && (
        <div className="grid grid-cols-3 gap-2 mt-[29px]">
          {imgs.map((img, idx) => (
            <div className="relative" key={idx}>
              <img
                key={idx}
                src={img.image_url}
                alt={`img-${idx}`}
                className="w-full h-[100px] object-contain"
              />
              {img.is_main && (
                <span className="absolute left-1 top-1 z-10 px-2 py-0.5 text-[11px] bg-custom-white text-custom-black rounded-full shadow">
                  대표
                </span>
              )}
              <button
                type="button"
                onClick={() => handleClickDelete(img.image_id)}
                className="absolute top-0 right-0 text-custom-black text-xs w-5 h-5 flex items-center justify-center rounded-full"
              >
                X
              </button>
            </div>
          ))}
        </div>
      )}

      {/* save */}
      <CommonBtn
        label="저장"
        onClick={handleSubmit}
        category="green"
        notBottom
        className="w-[350px] flex w-full justify-center my-[50px]"
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
