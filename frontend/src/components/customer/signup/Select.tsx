import { CommonBtn } from "@components/common";

type SelectProps = {
  onNext: () => void;
};

const Select = ({ onNext }: SelectProps) => {
  const handleSubmit = () => {
    onNext();
  };
  return (
    <>
      <div className="flex h-full w-full justify-center items-center pb-[207px]">
        <div className="grid grid-cols-2 gap-x-[10px]">
          <div className="bg-[#717171] rounded-[5px] text-white p-[15px] h-[90px] w-[170px]">
            <div className="font-semibold text-[15px]">다이어트</div>
            <div className="font-base text-[11px]">체지방 감소와 활력 증진</div>
          </div>
        </div>
      </div>
      {/* 다음 */}
      <CommonBtn label="다음" onClick={handleSubmit} />
    </>
  );
};

export default Select;
