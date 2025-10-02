import { CommonBtn } from "@components/common";
import type { SellerSignupProps } from "@interface";
import { useSignupStore } from "@store";

const RegisterName = ({ pageIdx, setPageIdx }: SellerSignupProps) => {
  const { form, setForm } = useSignupStore();

  return (
    <div className="mx-[20px] mt-[69px] flex flex-col gap-y-[11px]">
      <div className="text-[16px]">1/4</div>
      <div className="text-[24px]">
        <span className="font-bold">매장 이름</span>을 <br />
        입력해 주세요.
      </div>

      {/* input box */}
      <input
        className="w-full h-[46px] text-center bg-[#D9D9D9] text-[16px] mt-[40px]"
        placeholder="매장 이름을 입력해 주세요"
        value={form.store_name}
        onChange={(e) => setForm({ store_name: e.target.value })}
      />

      <CommonBtn
        category="black"
        label="다음"
        onClick={() => setPageIdx(pageIdx + 1)}
      />
    </div>
  );
};

export default RegisterName;
