import { CommonBtn } from "@components/common";
import { Agree, Enter, Select } from "@components/customer/signup";

type SignupSwiperProps = {
  title: string;
  type: "agree" | "enter" | "select";
  placeholder?: string;
  subTitle?: string;
};

const SignupSwiper = ({
  title,
  type,
  placeholder,
  subTitle,
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
        {type === "agree" && <Agree />}
        {/* type: enter */}
        {type === "enter" && <Enter placeholder={placeholder ?? ""} />}
        {/* type: select */}
        {type === "select" && <Select />}
        <CommonBtn label="다음" />
      </div>
    </>
  );
};

export default SignupSwiper;
