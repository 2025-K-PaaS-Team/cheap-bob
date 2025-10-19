import type { ProductRequestType } from "@interface";

interface PkgNumProps {
  pkg: ProductRequestType;
  setPkg: React.Dispatch<React.SetStateAction<ProductRequestType>>;
}

const CommonPkgNum = ({ pkg, setPkg }: PkgNumProps) => {
  return (
    <div className="flex flex-col gap-y-[40px]">
      <div className="titleFont">하루에 몇 개 판매할까요?</div>
      <div className="flex flex-col gap-y-[10px]">
        <h3>패키지 판매 기본값</h3>
        <div className="bodyFont">
          평균적으로 하루에 판매 가능한 개수를 입력해 주세요.
        </div>
      </div>

      <div className="flex flex-row items-center justify-center gap-x-[10px]">
        <div className="relative flex flex-row justify-center items-center rounded bg-main-pale w-[114px] h-[64px]">
          <div className="titleFont mr-3">{pkg.initial_stock}</div>
          <div className="flex flex-col gap-y-[5px] text-[10px] absolute right-4">
            <div
              className="bg-white text-main-deep text-center items-center justify-center flex p-1 rounded-full w-5 h-5"
              onClick={() =>
                setPkg((prev) => ({
                  ...prev,
                  initial_stock: Number(prev.initial_stock + 1),
                }))
              }
            >
              ▲
            </div>
            <div
              className="bg-white text-main-deep text-center items-center justify-center flex p-1 rounded-full w-5 h-5"
              onClick={() =>
                setPkg((prev) => ({
                  ...prev,
                  initial_stock: Number(prev.initial_stock - 1),
                }))
              }
            >
              ▼
            </div>
          </div>
        </div>

        <h1>개 판매할게요.</h1>
      </div>

      {/* notice */}
      <div className="hintFont text-center">
        설정한 기본값보다 판매할 재고가 남거나 부족해도 <br /> ‘일일 조정값’으로
        매일 조정할 수 있어요.
      </div>
    </div>
  );
};

export default CommonPkgNum;
