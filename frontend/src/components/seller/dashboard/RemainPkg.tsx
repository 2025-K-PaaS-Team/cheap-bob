import type { DashboardBaseType } from "@interface";
import { DecreaseProductStock, IncreaseProductStock } from "@services";
import { formatErrMsg } from "@utils";

interface RemainPkgProps {
  remainPkg: DashboardBaseType;
  setShowModal: React.Dispatch<React.SetStateAction<boolean>>;
  setModalMsg: React.Dispatch<React.SetStateAction<string>>;
  onChanged: () => Promise<void> | void;
}
const RemainPkg = ({
  remainPkg,
  setShowModal,
  setModalMsg,
  onChanged,
}: RemainPkgProps) => {
  const handleIncreaseStock = async () => {
    try {
      await IncreaseProductStock(remainPkg.product_id);
      await onChanged?.();
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    }
  };

  const handleDecreaseStock = async () => {
    try {
      await DecreaseProductStock(remainPkg.product_id);
      await onChanged?.();
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    }
  };

  return (
    <div className="mx-[20px] flex flex-col mt-[24px] bg-custom-white rounded-[8px] py-[23px] px-[19px] text-custom-black">
      <div className="text-[24px] mb-[7px]">
        현재 패키지 잔여 수량은 <br />{" "}
        <span className="font-bold">{remainPkg.current_stock}개</span> 입니다.
      </div>
      <div className="grid grid-cols-4 text-center gap-x-[11px]">
        <div className="flex flex-col py-[14px]">
          <div className="text-[14px]">판매 기본값</div>
          <div className="text-[24px]">{remainPkg.initial_stock}</div>
        </div>
        <div className="flex flex-col py-[14px]">
          <div className="text-[14px]">- 주문 수량</div>
          <div className="text-[24px]">{remainPkg.purchased_stock}</div>
        </div>
        <div className="relative py-[14px] flex flex-row col-span-2 bg-main-pale rounded-[8px] justify-center">
          <div className="flex flex-col justify-center">
            <div className="text-[14px]">+ 일일 조정값</div>
            <div className="text-[24px]">{remainPkg.adjustment_stock}</div>
          </div>
          <div className="absolute right-[10px] top-[31px] flex flex-col justify-center gap-y-[4px]">
            <div
              className="bg-custom-white w-[20px] aspect-square flex items-center justify-center text-[10px] rounded-full"
              onClick={() => handleIncreaseStock()}
            >
              ▲
            </div>
            <div
              className="bg-custom-white w-[20px] aspect-square flex items-center justify-center text-[10px] rounded-full"
              onClick={() => handleDecreaseStock()}
            >
              ▼
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RemainPkg;
