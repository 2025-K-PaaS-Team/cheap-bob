type BtnProps = {
  category?:
    | "transparent"
    | "white"
    | "grey"
    | "black"
    | "red"
    | "green"
    | "pale-green";
  label: string;
  notBottom?: boolean;
  className?: string;
  width?: string;
  icon?: string;
  onClick?: () => void;
  type?: "button" | "submit" | "reset";
  disabled?: boolean;
};

const CommonBtn = ({
  category = "green",
  type,
  label,
  onClick,
  className,
  width,
  disabled,
  icon,
  notBottom = false,
}: BtnProps) => {
  const colorClass = {
    transparent: "bg-transparent text-[#6C6C6C] border-0",
    white: "bg-white text-custom-black border border-main-deep",
    grey: "bg-[#EDEDED] text-[#6C6C6C] border-0",
    black: "bg-black text-white border border-black",
    red: "bg-white text-[#FF0000] border border-[#FF0000]",
    green: "bg-main-deep text-white border border-0",
    "pale-green": "bg-main-pale text-main-deep border border-main-deep",
  }[category];

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`font-bold rounded text-base h-[54px] flex justify-center items-center
        ${notBottom ? "" : "fixed-action"} 
        ${colorClass}
        ${disabled ? "cursor-not-allowed" : className ? className : ""}
        ${icon ? "flex-row gap-x-[8px]" : ""}
        ${width ? width : "w-full"}`}
    >
      {label}
      <img src={icon} />
    </button>
  );
};

export default CommonBtn;
