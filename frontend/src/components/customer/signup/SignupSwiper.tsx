import { CommonBtn } from "@components/common";
import { Agree } from "@components/customer/signup";

type SignupSwiperProps = {
  title: string;
  type: "agree" | "enter" | "select";
};

const SignupSwiper = ({ title, type }: SignupSwiperProps) => {
  return (
    <>
      <div className="relative h-full px-[20px] pt-[42px]">
        {/* title */}
        <div className="font-bold text-2xl">
          {title.split("\n").map((line, idx) => (
            <p key={idx}>{line}</p>
          ))}
        </div>

        {/* type: agree */}
        {type === "agree" && <Agree />}
        {/* type: enter */}
        {/* type: select */}
        <CommonBtn label="다음" />
      </div>
    </>
  );
};

export default SignupSwiper;
