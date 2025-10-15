type BtnProps = {
  category?: "transparent" | "white" | "grey" | "black" | "red" | "green";
  label: string;
  notBottom?: boolean;
  className?: string;
  width?: string;
  onClick?: () => void;
  type?: "button" | "submit" | "reset";
};

const CommonBtn = ({
  category = "green",
  type,
  label,
  onClick,
  className,
  width,
  notBottom = false,
}: BtnProps) => {
  const colorClass = {
    transparent: "bg-transparent text-custom-black border-0",
    white: "bg-custom-white text-custom-black border border-[#222222]",
    grey: "bg-[#EDEDED] text-custom-black border-0",
    black: "bg-black text-white border border-black",
    red: "bg-custom-white text-[#FF0000] border border-[#FF0000]",
    green: "bg-main-normal text-white border border-0",
  }[category];

  return (
    <button
      type={type}
      onClick={onClick}
      className={`font-bold rounded-[10px] text-base h-[54px] flex justify-center items-center
        ${notBottom ? "" : "absolute bottom-[38px] left-1/2 -translate-x-1/2"} 
        ${colorClass}
        ${className ? className : ""}
        ${width ? width : "w-[350px]"}`}
    >
      {label}
    </button>
  );
};

export default CommonBtn;
