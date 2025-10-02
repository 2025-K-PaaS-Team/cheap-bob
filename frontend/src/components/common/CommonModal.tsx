type ModalProps = {
  cancelLabel?: string;
  confirmLabel?: string;
  onCancelClick?: () => void;
  onConfirmClcik: () => void;
  desc: string;
  category?: "red" | "black";
};

const CommonModal = ({
  cancelLabel = "취소",
  confirmLabel = "확인",
  onCancelClick,
  onConfirmClcik,
  desc,
  category,
}: ModalProps) => {
  const confrimBtnClass =
    category === "red"
      ? "bg-white border-[#FF0000]"
      : "bg-black text-white border-black";

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black/50 z-50">
      <div className="flex flex-col w-[359px] p-[20px] rounded-[16px] gap-y-[10px] border-[1px] border-black bg-white">
        <div className="text-[16px]">{desc}</div>
        <div className="flex flex-row gap-x-[20px] text-[18px] text-center">
          {cancelLabel && onCancelClick && (
            <button
              className="bg-white border-[1px] border-black rounded-[50px] w-full py-[12px]"
              onClick={() => onCancelClick()}
            >
              {cancelLabel}
            </button>
          )}

          <button
            className={`${confrimBtnClass} border-white rounded-[50px] w-full py-[12px]`}
            onClick={() => onConfirmClcik()}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
};

export default CommonModal;
