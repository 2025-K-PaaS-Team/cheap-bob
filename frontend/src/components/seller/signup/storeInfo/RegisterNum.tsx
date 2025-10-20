import { CommonBtn, CommonModal } from "@components/common";
import type { SellerSignupProps } from "@interface";
import { useSignupStore } from "@store";
import {
  validatePattern,
  validationRules,
  validateUrl,
  normalizeUrl,
  formatPhoneNumber,
} from "@utils";
import { useState } from "react";

const RegisterNum = ({ pageIdx, setPageIdx }: SellerSignupProps) => {
  const { form, setForm } = useSignupStore();
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");
  const { storePhone } = validationRules;

  const handleClickNext = () => {
    if (!validatePattern(form.store_phone, storePhone.pattern)) {
      setModalMsg(storePhone.errorMessage);
      setShowModal(true);
      return;
    }

    const { homepage, instagram, facebook, x } = form.sns_info;
    const invalids: string[] = [];
    if (!validateUrl(homepage ?? "")) invalids.push("홈페이지");
    if (!validateUrl(instagram ?? "")) invalids.push("인스타그램");
    if (!validateUrl(facebook ?? "")) invalids.push("페이스북");
    if (!validateUrl(x ?? "")) invalids.push("X(Twitter)");

    if (invalids.length) {
      setModalMsg(`${invalids.join(", ")} URL을 올바르게 입력해 주세요.`);
      setShowModal(true);
      return;
    }

    setPageIdx(pageIdx + 1);
  };

  const handleClickPrev = () => {
    setPageIdx(pageIdx - 1);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const rawValue = e.target.value.replace(/\D/g, "");
    setForm({ store_phone: rawValue });
  };

  return (
    <div className="mx-[20px] my-[20px] flex flex-col flex-1 gap-y-[40px]">
      <div className="flex flex-1 flex-col gap-y-[40px]">
        {" "}
        <div className="text-main-deep font-bold bodyFont">3/5</div>
        <div className="titleFont">
          <span className="font-bold">매장 연락처</span>를 입력해 주세요.
        </div>
        {/* input box */}
        <div className="gap-y-[11px]">
          <h3>
            매장 전화번호 <span className="text-sub-orange">(필수)</span>
          </h3>
          <input
            className="w-full h-[46px]  border-b border-[#393939] hintFont"
            placeholder="텍스트를 입력하세요"
            value={formatPhoneNumber(form.store_phone)}
            onChange={handleChange}
          />
        </div>
        {/* other sns */}
        <div className="mt-[39px] flex flex-col gap-y-[11px]">
          <h2>다른 SNS도 있나요?</h2>
          <div className="flex flex-row">
            <div className="bodyFont w-[100px]">홈페이지</div>
            <input
              className="h-[33px] flex-1 border-b border-[#393939] hintFont"
              value={form.sns_info.homepage}
              placeholder="텍스트를 입력하세요"
              onChange={(e) =>
                setForm({
                  sns_info: {
                    ...form.sns_info,
                    homepage: e.target.value,
                  },
                })
              }
              onBlur={(e) =>
                setForm({
                  sns_info: {
                    ...form.sns_info,
                    homepage: normalizeUrl(e.target.value),
                  },
                })
              }
            />
          </div>
          <div className="flex flex-row">
            <div className="bodyFont w-[100px]">인스타그램</div>
            <input
              className="h-[33px] flex-1 border-b border-[#393939] hintFont"
              placeholder="텍스트를 입력하세요"
              value={form.sns_info.instagram}
              onChange={(e) =>
                setForm({
                  sns_info: {
                    ...form.sns_info,
                    instagram: e.target.value,
                  },
                })
              }
              onBlur={(e) =>
                setForm({
                  sns_info: {
                    ...form.sns_info,
                    instagram: normalizeUrl(e.target.value),
                  },
                })
              }
            />
          </div>
          <div className="flex flex-row">
            <div className="bodyFont w-[100px]">X (Twitter)</div>
            <input
              className="h-[33px] flex-1 border-b border-[#393939] hintFont"
              value={form.sns_info.x}
              placeholder="텍스트를 입력하세요"
              onChange={(e) =>
                setForm({
                  sns_info: { ...form.sns_info, x: e.target.value },
                })
              }
              onBlur={(e) =>
                setForm({
                  sns_info: {
                    ...form.sns_info,
                    x: normalizeUrl(e.target.value),
                  },
                })
              }
            />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3">
        <CommonBtn
          category="transparent"
          label="이전"
          onClick={() => handleClickPrev()}
          notBottom
        />
        <CommonBtn
          category={
            !validatePattern(form.store_phone, storePhone.pattern)
              ? "grey"
              : "green"
          }
          label="다음"
          onClick={() => handleClickNext()}
          className="col-span-2"
          notBottom
        />
      </div>

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

export default RegisterNum;
