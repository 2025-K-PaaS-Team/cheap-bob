import { CommonBtn, CommonModal } from "@components/common";
import type { ImageInfoType } from "@interface";
import { GetStoreImg } from "@services";
import { formatErrMsg } from "@utils";
import React, { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router";

const ChangeStoreImg = () => {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const navigate = useNavigate();
  const [previews, setPreviews] = useState<string[]>([]);
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");
  const [imgs, setImgs] = useState<ImageInfoType[]>([]);

  const handleSubmit = () => {
    navigate(-1);
  };

  const handleGetStoreImg = async () => {
    try {
      const res = await GetStoreImg();
      setImgs(res.images);
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    }
  };

  const handleClickUpload = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files) return;

    const selectedFiles = Array.from(files).slice(0, 5 - previews.length); // 최대 5개
    const urls = selectedFiles.map((file) => URL.createObjectURL(file));
    setPreviews((prev) => [...prev, ...urls]);
  };

  const handleRemovePreview = (index: number) => {
    setPreviews((prev) => prev.filter((_, i) => i !== index));
  };

  useEffect(() => {
    handleGetStoreImg();
  }, []);

  return (
    <div className="mt-[80px] px-[20px] w-full">
      {/* question */}
      <div className="text-[24px] mb-[44px]">
        변경할 <span className="font-bold">이미지</span>를 <br /> 새로 업로드해
        주세요.
      </div>

      {/* upload picture button */}
      <div className="w-full flex justify-center">
        <CommonBtn
          label="(사진 업로드)"
          notBottom
          onClick={handleClickUpload}
          className="border-[#999999] font-normal"
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
      {(previews.length > 0 || imgs.length > 0) && (
        <div className="grid grid-cols-4 gap-2 mt-[29px]">
          {imgs.map((img, idx) => (
            <img key={idx} src={img.image_url} />
          ))}
          {previews.map((src, idx) => (
            <div key={idx} className="relative">
              <img
                src={src}
                alt={`preview-${idx}`}
                className="w-full h-[100px] object-contain"
              />
              <button
                type="button"
                onClick={() => handleRemovePreview(idx)}
                className="absolute top-0 right-0 text-black text-xs w-5 h-5 flex items-center justify-center rounded-full"
              >
                X
              </button>
            </div>
          ))}
        </div>
      )}

      {/* save */}
      <CommonBtn label="저장" onClick={handleSubmit} category="black" />

      {/* show modal */}
      {showModal && (
        <CommonModal
          desc={modalMsg}
          confirmLabel="확인"
          onConfirmClick={() => setShowModal(false)}
          category="black"
        />
      )}
    </div>
  );
};

export default ChangeStoreImg;
