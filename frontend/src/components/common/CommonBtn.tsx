type BtnProps = {
  category?: "transparent" | "white" | "grey" | "black" | "red";
  label: string;
  notBottom?: boolean;
  className?: string;
  width?: string;
  onClick: () => void;
};

const CommonBtn = ({
  category = "white",
  label,
  onClick,
  className,
  width,
  notBottom = false,
}: BtnProps) => {
  const colorClass = {
    transparent: "bg-transparent text-black border-0",
    white: "bg-white text-black border border-[#222222]",
    grey: "bg-[#EDEDED] text-black border-0",
    black: "bg-black text-white border border-black",
    red: "bg-white text-[#FF0000] border border-[#FF0000]",
  }[category];

  return (
    <button
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
