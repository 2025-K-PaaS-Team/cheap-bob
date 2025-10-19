import { CommonBtn, CommonModal } from "@components/common";
import type { SellerSignupProps } from "@interface";
import { useSignupImageStore, useSignupStore } from "@store";
import { validateLength, validationRules } from "@utils";
import { useEffect, useRef, useState } from "react";

const RegisterStoreRepImg = ({ pageIdx, setPageIdx }: SellerSignupProps) => {
  const { form } = useSignupStore();
  const { form: imgForm, setForm: setImgForm } = useSignupImageStore();
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    console.log(imgForm);
  }, [imgForm]);

  console.log(imgForm);

  const handleClickNext = () => {
    const { storeDesc } = validationRules;
    if (
      !validateLength(
        form.store_introduction,
        storeDesc.minLength,
        storeDesc.maxLength
      )
    ) {
      setModalMsg(storeDesc.errorMessage);
      setShowModal(true);
      return;
    }
    setPageIdx(pageIdx + 1);
  };

  const handleClickPrev = () => {
    setPageIdx(pageIdx - 1);
  };

  const handleClickUpload = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    const file = files[0];
    const ALLOWED = ["image/jpeg", "image/jpg", "image/png", "image/webp"];
    const MAX = 10 * 1024 * 1024;

    if (!ALLOWED.includes(file.type)) {
      setModalMsg("지원 형식: JPG, JPEG, PNG, WEBP");
      setShowModal(true);
      return;
    }

    if (file.size > MAX) {
      setModalMsg("최대 크기 10MB를 초과했습니다.");
      setShowModal(true);
      return;
    }

    setImgForm({ images: [{ file, preview: URL.createObjectURL(file) }] });
  };

  useEffect(() => {
    return () => {
      imgForm.images.forEach((it) => URL.revokeObjectURL(it.preview));
    };
  }, []);

  return (
    <div className="mx-[20px] mt-[20px] flex flex-col gap-y-[40px]">
      <div className="text-main-deep font-bold bodyFont">5/5</div>
      <div className="titleFont">
        <span className="font-bold">매장 대표 이미지</span>를 등록해 주세요.
        <div className="bodyFont">
          대표 이미지는 손님들이 가게를 더 잘 찾아오실 수 있도록{" "}
          <span className="font-bold">가게의 외부 사진</span>을 등록해 주세요.
        </div>
      </div>

      {/* preview */}
      {imgForm?.images[0]?.preview ? (
        <div className="relative h-[125px]">
          <img
            src={imgForm?.images[0]?.preview}
            alt={`storeRepImg`}
            className="w-full h-full object-cover"
          />
        </div>
      ) : (
        <div className="relative h-[125px] bg-custom-white">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 flex flex-col">
            <div className="hintFont text-custom-black">
              등록된 사진이 없습니다.
            </div>
            <div className="tagFont text-[#6C6C6C]">권장 크기 350x125 (px)</div>
          </div>
        </div>
      )}

      {/* upload picture button */}
      <div className="w-full flex justify-center">
        <CommonBtn
          label="대표 사진 등록"
          category="white"
          notBottom
          onClick={handleClickUpload}
          className="border-1 border-[#999999] font-normal"
        />
      </div>

      <input
        type="file"
        accept="image/*"
        ref={fileInputRef}
        className="hidden"
        onChange={handleFileChange}
      />

      <CommonBtn
        category="transparent"
        label="이전"
        onClick={() => handleClickPrev()}
        notBottom
        className="absolute left-[20px] bottom-[38px]"
        width="w-[100px]"
      />
      <CommonBtn
        category={form.store_introduction ? "green" : "grey"}
        label="다음"
        onClick={() => handleClickNext()}
        notBottom
        className="absolute right-[20px] bottom-[38px]"
        width="w-[250px]"
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

export default RegisterStoreRepImg;
