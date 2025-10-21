import { useEffect, useMemo } from "react";
import { createPortal } from "react-dom";

type ModalProps = {
  cancelLabel?: string;
  confirmLabel?: string;
  onCancelClick?: () => void;
  onConfirmClick?: () => void;
  desc?: string;
  category?: "red" | "black" | "green";
  children?: React.ReactNode;
  className?: string;
  container?: string | Element;
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
  container,
}: ModalProps) => {
  const confrimBtnClass =
    category === "red"
      ? "bg-sub-red text-white"
      : category === "black"
      ? "bg-black text-white border-black"
      : "bg-main-deep text-white border-none";

  const portalTarget = useMemo<HTMLElement | null>(() => {
    if (typeof container === "string") {
      return (
        (document.querySelector(container) as HTMLElement) ??
        document.querySelector(".app-frame") ??
        document.body
      );
    }
    if (container instanceof Element) {
      return container as HTMLElement;
    }
    return (
      (document.querySelector(".app-frame") as HTMLElement) ?? document.body
    );
  }, [container]);

  useEffect(() => {
    if (!portalTarget) return;
    const prevOverflow = portalTarget.style.overflow;
    portalTarget.style.overflow = "hidden";
    return () => {
      portalTarget.style.overflow = prevOverflow;
    };
  }, [portalTarget]);

  const modal = (
    <div
      className="absolute inset-0 z-[1000] flex items-center justify-center bg-black/20"
      aria-modal
      role="dialog"
    >
      <div
        className={`${
          className ?? ""
        } text-center flex flex-col w-[359px] max-w-[90%] p-[20px] rounded-lg gap-y-[10px] bg-white mx-[20px]`}
      >
        {desc && (
          <div
            className="bodyFont"
            dangerouslySetInnerHTML={{ __html: desc }}
          />
        )}
        {children}

        <div className="grid grid-cols-3 gap-x-[20px] btnFont mt-[10px]">
          {onCancelClick && (
            <button
              className="bg-custom-white rounded w-full py-[12px]"
              onClick={onCancelClick}
            >
              {cancelLabel}
            </button>
          )}
          {onConfirmClick && (
            <button
              className={`${confrimBtnClass} ${
                onCancelClick ? "col-span-2" : "col-span-3"
              } rounded w-full py-[12px]`}
              onClick={onConfirmClick}
            >
              {confirmLabel}
            </button>
          )}
        </div>
      </div>
    </div>
  );

  return portalTarget ? createPortal(modal, portalTarget) : null;
};

export default CommonModal;
