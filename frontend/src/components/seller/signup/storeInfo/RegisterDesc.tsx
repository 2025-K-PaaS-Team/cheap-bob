import { CommonBtn, CommonModal } from "@components/common";
import type { SellerSignupProps } from "@interface";
import { useSignupImageStore, useSignupStore } from "@store";
import { validateLength, validationRules } from "@utils";
import { useEffect, useRef, useState } from "react";

const RegisterDesc = ({ pageIdx, setPageIdx }: SellerSignupProps) => {
  const { form, setForm } = useSignupStore();
  const { form: imgForm, setForm: setImgForm } = useSignupImageStore();
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    console.log(imgForm);
  }, [imgForm]);

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

    const remain = Math.max(0, 5 - imgForm.images.length);
    const selected = Array.from(files).slice(0, remain);

    const ALLOWED = ["image/jpeg", "image/jpg", "image/png", "image/webp"];
    const MAX = 10 * 1024 * 1024;
    for (const f of selected) {
      if (!ALLOWED.includes(f.type)) {
        setModalMsg("지원 형식: JPG, JPEG, PNG, WEBP");
        setShowModal(true);
        return;
      }
      if (f.size > MAX) {
        setModalMsg("최대 크기 10MB를 초과했습니다.");
        setShowModal(true);
        return;
      }
    }

    const newItems = selected.map((file) => ({
      file,
      preview: URL.createObjectURL(file),
    }));

    setImgForm({ images: [...imgForm.images, ...newItems] });
  };

  const handleRemovePreview = (index: number) => {
    const target = imgForm.images[index];
    if (target) URL.revokeObjectURL(target.preview);
    setImgForm({ images: imgForm.images.filter((_, i) => i !== index) });
  };

  useEffect(() => {
    return () => {
      imgForm.images.forEach((it) => URL.revokeObjectURL(it.preview));
    };
  }, []);

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
      {imgForm.images.length > 0 && (
        <div className="grid grid-cols-4 gap-2 mt-[29px]">
          {imgForm.images.map((img, idx) => (
            <div key={idx} className="relative">
              <img
                src={img.preview}
                alt={`preview-${idx}`}
                className="w-full h-[100px] object-contain"
              />
              <button
                type="button"
                onClick={() => handleRemovePreview(idx)}
                className="absolute top-0 right-0 text-custom-black text-xs w-5 h-5 flex items-center justify-center rounded-full"
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
          onConfirmClick={() => setShowModal(false)}
          category="black"
        />
      )}
    </div>
  );
};

export default RegisterDesc;
