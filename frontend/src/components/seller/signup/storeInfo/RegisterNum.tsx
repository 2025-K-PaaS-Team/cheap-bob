import { CommonBtn, CommonModal } from "@components/common";
import type { SellerSignupProps } from "@interface";
import { useSignupStore } from "@store";
import { validatePattern, validationRules, validateUrl } from "@utils";
import { useState } from "react";

const RegisterNum = ({ pageIdx, setPageIdx }: SellerSignupProps) => {
  const { form, setForm } = useSignupStore();
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");

  const normalizeUrl = (raw?: string): string | undefined => {
    const s = (raw ?? "").trim();
    if (!s) return undefined;
    const withScheme = /^https?:\/\//i.test(s) ? s : `https://${s}`;
    try {
      new URL(withScheme);
      return withScheme;
    } catch {
      return undefined;
    }
  };

  const handleClickNext = () => {
    const { storePhone } = validationRules;
    if (!validatePattern(form.store_phone, storePhone.pattern)) {
      setModalMsg(storePhone.errorMessage);
      setShowModal(true);
      return;
    }

    const { homepage, instagram, facebook, x } = form.sns_info;
    const invalids: string[] = [];
    if (!validateUrl(homepage)) invalids.push("홈페이지");
    if (!validateUrl(instagram)) invalids.push("인스타그램");
    if (!validateUrl(facebook)) invalids.push("페이스북");
    if (!validateUrl(x)) invalids.push("X(Twitter)");

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

  return (
    <div className="mx-[20px] mt-[69px] flex flex-col gap-y-[11px]">
      <div className="text-[16px]">4/4</div>
      <div className="text-[24px]">
        <span className="font-bold">매장 연락처</span>를 알려주세요.
      </div>
      <div className="text-[16px]">손님에게 연락이 올 수 있어요.</div>

      {/* input box */}
      <div className="mt-[40px] gap-y-[11px]">
        <div className="text-[16px]">매장 전화번호 (*필수)</div>
        <input
          className="w-full h-[46px] text-center bg-[#D9D9D9] text-[16px]"
          placeholder="매장 전화번호를 입력해 주세요"
          value={form.store_phone}
          onChange={(e) => setForm({ store_phone: e.target.value })}
        />
      </div>

      {/* other sns */}
      <div className="mt-[39px] flex flex-col gap-y-[11px]">
        <div className="text-[20px]">다른 SNS도 있나요?</div>
        <div className="flex flex-row">
          <div className="text-[14px] w-[97px] flex items-center">홈페이지</div>
          <input
            className="w-full h-[40px] text-center bg-[#D9D9D9] text-[16px]"
            value={form.sns_info.homepage}
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
          <div className="text-[14px] w-[97px] flex items-center">
            인스타그램
          </div>
          <input
            className="w-full h-[40px] text-center bg-[#D9D9D9] text-[16px]"
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
          <div className="text-[14px] w-[97px] flex items-center">
            X (Twitter)
          </div>
          <input
            className="w-full h-[40px] text-center bg-[#D9D9D9] text-[16px]"
            value={form.sns_info.x}
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

export default RegisterNum;
