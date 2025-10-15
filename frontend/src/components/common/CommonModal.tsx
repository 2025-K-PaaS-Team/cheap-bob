type ModalProps = {
  cancelLabel?: string;
  confirmLabel?: string;
  onCancelClick?: () => void;
  onConfirmClick: () => void;
  desc: string;
  category?: "red" | "black" | "green";
  children?: React.ReactNode;
};

const CommonModal = ({
  cancelLabel = "취소",
  confirmLabel = "확인",
  onCancelClick,
  onConfirmClick,
  desc,
  category = "green",
  children,
}: ModalProps) => {
  const confrimBtnClass =
    category === "red"
      ? "bg-custom-white border-[#FF0000]"
      : category === "black"
      ? "bg-black text-white border-black"
      : "bg-main-deep text-white border-none";

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black/50 z-50">
      <div className="flex flex-col w-[359px] p-[20px] rounded-lg gap-y-[10px] border-[1px] border-black bg-custom-white">
        {/* description */}
        {desc && <div className="text-[16px]">{desc}</div>}

        {/* children */}
        {children}

        {/* button */}
        <div className="flex flex-row gap-x-[20px] text-[18px] text-center">
          {cancelLabel && onCancelClick && (
            <button
              className="bg-custom-white border-[1px] border-black rounded-[50px] w-full py-[12px]"
              onClick={() => onCancelClick()}
            >
              {cancelLabel}
            </button>
          )}

          <button
            className={`${confrimBtnClass} border-white rounded-[50px] w-full py-[12px]`}
            onClick={() => onConfirmClick()}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
};

export default CommonModal;
