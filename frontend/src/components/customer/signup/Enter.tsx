import { CommonBtn } from "@components/common";

type EnterProps = {
  placeholder: string;
  onNext: () => void;
  setValue: React.Dispatch<React.SetStateAction<string>>;
  value: string;
  validate: (val: string) => string | null;
};
const Enter = ({
  placeholder,
  onNext,
  setValue,
  value,
  validate,
}: EnterProps) => {
  const handleSubmit = () => {
    const error = validate(value);
    if (error) {
      alert(error);
      return;
    }
    onNext();
  };

  return (
    <>
      <input
        type="text"
        placeholder={placeholder}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        className="border border-[1px] w-[350px] h-[54px] flex items-center justify-center px-[12px] rounded-[10px] mt-[45px]"
      />
      {/* 다음 */}
      <CommonBtn label="다음" onClick={handleSubmit} />
    </>
  );
};

export default Enter;
