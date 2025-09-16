import { Agree, Enter, Select } from "@components/customer/signup";
import type { SelectItem } from "@constant";

type BaseProps = {
  title: string;
  onNext: () => void;
  subTitle?: string;
};

type AgreeProps = BaseProps & {
  type: "agree";
};

type EnterProps = BaseProps & {
  type: "enter";
  placeholder?: string;
  value: string;
  setValue: React.Dispatch<React.SetStateAction<string>>;
};

type SelectProps = BaseProps & {
  type: "select";
  data: SelectItem[];
  selectType?: string;
};

type SignupSwiperProps = AgreeProps | EnterProps | SelectProps;

const SignupSwiper = (props: SignupSwiperProps) => {
  const { title, type, onNext, subTitle } = props;

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
          <Enter
            placeholder={props.placeholder ?? ""}
            onNext={onNext}
            setValue={props.setValue}
            value={props.value}
          />
        )}

        {/* type: select */}
        {type === "select" && (
          <Select
            onNext={onNext}
            data={props.data}
            selectType={props.selectType}
          />
        )}
      </div>
    </>
  );
};

export default SignupSwiper;
