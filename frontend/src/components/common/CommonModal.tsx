type ModalProps = {
  cancelLabel?: string;
  confirmLabel?: string;
  onCancelClick?: () => void;
  onConfirmClick?: () => void;
  desc?: string;
  category?: "red" | "black" | "green";
  children?: React.ReactNode;
  className?: string;
};

const CommonModal = ({
  cancelLabel = "취소",
  confirmLabel = "확인",
  onCancelClick,
  onConfirmClick,
  desc,
  category = "green",
  className,
  children,
}: ModalProps) => {
  const confrimBtnClass =
    category === "red"
      ? "bg-sub-red text-white"
      : category === "black"
      ? "bg-black text-white border-black"
      : "bg-main-deep text-white border-none";

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black/40 z-50">
      <div
        className={`${
          className ? className : ""
        } text-center flex flex-col w-[359px] p-[20px] rounded-lg gap-y-[10px] bg-white`}
      >
        {/* description */}
        {desc && (
          <div
            className="bodyFont"
            dangerouslySetInnerHTML={{ __html: desc }}
          />
        )}

        {/* children */}
        {children}

        {/* button */}
        <div className="grid grid-cols-3 gap-x-[20px] btnFont">
          {onCancelClick && (
            <button
              className="bg-custom-white rounded w-full py-[12px]"
              onClick={() => onCancelClick()}
            >
              {cancelLabel}
            </button>
          )}
          {onConfirmClick && (
            <button
              className={`${confrimBtnClass} ${
                onCancelClick ? "col-span-2" : "col-span-3"
              } rounded w-full py-[12px]`}
              onClick={() => onConfirmClick()}
            >
              {confirmLabel}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default CommonModal;
