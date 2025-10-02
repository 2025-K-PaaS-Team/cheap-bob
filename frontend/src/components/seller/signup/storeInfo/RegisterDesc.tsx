import { CommonBtn, CommonModal } from "@components/common";
import type { SellerSignupProps } from "@interface";
import { useSignupStore } from "@store";
import { validateLength, validationRules } from "@utils";
import { useRef, useState } from "react";

const RegisterDesc = ({ pageIdx, setPageIdx }: SellerSignupProps) => {
  const { form, setForm } = useSignupStore();
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [previews, setPreviews] = useState<string[]>([]);

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
    if (!files) return;

    const selectedFiles = Array.from(files).slice(0, 5 - previews.length); // 최대 5개
    const urls = selectedFiles.map((file) => URL.createObjectURL(file));
    setPreviews((prev) => [...prev, ...urls]);
  };

  const handleRemovePreview = (index: number) => {
    setPreviews((prev) => prev.filter((_, i) => i !== index));
  };

  return (
    <div className="mx-[20px] mt-[69px] flex flex-col gap-y-[11px] min-h-screen">
      <div className="text-[16px]">2/4</div>
      <div className="text-[24px]">
        <span className="font-bold">매장</span>에 대해{" "}
        <span className="font-bold">소개</span>해 주세요.
      </div>

      {/* input box */}
      <input
        className="w-full h-[100px] text-center bg-[#D9D9D9] text-[16px] mt-[40px]"
        placeholder="매장 설명을 입력해 주세요"
        value={form.store_introduction}
        onChange={(e) => setForm({ store_introduction: e.target.value })}
      />

      {/* upload picture button */}
      <div className="w-full flex justify-center">
        <CommonBtn
          label="(사진 업로드)"
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

      {/* preview */}
      {previews.length > 0 && (
        <div className="grid grid-cols-4 gap-2 mt-[29px]">
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

      <CommonBtn
        category="grey"
        label="이전"
        onClick={() => handleClickPrev()}
        notBottom
        className="absolute left-[20px] bottom-[38px]"
        width="w-[100px]"
      />
      <CommonBtn
        category="black"
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
          onConfirmClcik={() => setShowModal(false)}
          category="black"
        />
      )}
    </div>
  );
};

export default RegisterDesc;
