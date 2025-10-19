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
  validate: (val: string) => string | null;
};

type SelectProps = BaseProps & {
  type: "select";
  data: SelectItem[];
  selectType?: string;
  selected: string[];
  setSelected: React.Dispatch<React.SetStateAction<string[]>>;
  validate?: (val: string[]) => string | null;
};

type SignupSwiperProps = AgreeProps | EnterProps | SelectProps;

const SignupSwiper = (props: SignupSwiperProps) => {
  const { title, type, onNext, subTitle } = props;

  return (
    <div className="flex flex-col h-full">
      <div className="flex flex-col pt-[42px] pb-[80px] overflow-y-auto">
        <div className="mx-[20px]">
          {" "}
          {/* title */}
          <div className="titleFont flex-1">
            {title.split("\n").map((line, idx) => (
              <div key={idx}>{line}</div>
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
              validate={props.validate}
            />
          )}
          {/* type: select */}
          {type === "select" && (
            <Select
              onNext={onNext}
              data={props.data}
              selected={props.selected}
              setSelected={props.setSelected}
              selectType={props.selectType}
              validate={props.validate}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default SignupSwiper;
