type EnterProps = {
  placeholder: string;
};
const Enter = ({ placeholder }: EnterProps) => {
  return (
    <>
      <input
        type="text"
        placeholder={placeholder}
        className="border border-[1px] w-[350px] h-[54px] flex items-center justify-center px-[12px] rounded-[10px] mt-[45px]"
      />
    </>
  );
};

export default Enter;
