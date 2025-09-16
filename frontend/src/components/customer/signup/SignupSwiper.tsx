import { Agree, Enter, Select } from "@components/customer/signup";
import type { SelectItem } from "@constant";

type SignupSwiperProps = {
  title: string;
  type: "agree" | "enter" | "select";
  placeholder?: string;
  subTitle?: string;
  onNext: () => void;
  data?: SelectItem[];
};

const SignupSwiper = ({
  title,
  type,
  onNext,
  placeholder,
  subTitle,
  data,
}: SignupSwiperProps) => {
  return (
    <>
      <div className="relative h-full px-[20px] pt-[42px]">
        {/* title */}
        <div className="font-bold text-2xl">
          {title.split("\n").map((line, idx) => (
            <p key={idx}>{line}</p>
          ))}
          {subTitle && (
            <p className="text-[#6C6C6C] mt-[25px] text-base font-medium">
              {subTitle}
            </p>
          )}
        </div>

        {/* type: agree */}
        {type === "agree" && <Agree onNext={onNext} />}
        {/* type: enter */}
        {type === "enter" && (
          <Enter placeholder={placeholder ?? ""} onNext={onNext} />
        )}
        {/* type: select */}
        {type === "select" && <Select onNext={onNext} data={data} />}
      </div>
    </>
  );
};

export default SignupSwiper;
