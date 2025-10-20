import type { ProductBase, ProductRequestType } from "@interface";

interface PriceProps {
  pkg: ProductRequestType | ProductBase;
  setPkg: React.Dispatch<React.SetStateAction<ProductRequestType>>;
}

const CommonPrice = ({ pkg, setPkg }: PriceProps) => {
  const discountRate = ["15", "30", "40", "50"];

  return (
    <div className="flex flex-col gap-y-[40px]">
      {/* original price */}
      <div className="flex flex-col gap-y-[10px]">
        <h3>패키지 원가</h3>
        <div className="bodyFont">
          패키지를 구성하는 제품의 원가를 입력해 주세요.
        </div>
        {/* input box */}
        <div className="flex flex-row w-4/5 mx-auto justify-center items-center gap-x-[5px] border-b border-black">
          <input
            className="w-4/5 h-[40px] text-end text-[20px] font-bold"
            placeholder="0"
            value={pkg.price}
            onChange={(e) =>
              setPkg((prev) => ({ ...prev, price: Number(e.target.value) }))
            }
          />{" "}
          <h1>원</h1>
        </div>
      </div>

      {/* discount rate */}
      <div className="flex flex-col gap-y-[10px]">
        <h3>패키지 할인율</h3>
        <div className="bodyFont">패키지를 얼마나 할인할까요?</div>
        {/* input box */}
        <div className="flex flex-row w-4/5 mx-auto justify-center items-center gap-x-[5px] border-b border-black">
          <input
            className="w-4/5 h-[40px] text-end text-[20px] text-main-deep font-bold"
            placeholder="0"
            value={pkg.sale}
            onChange={(e) =>
              setPkg((prev) => ({ ...prev, sale: Number(e.target.value) }))
            }
          />{" "}
          <h1>%</h1>
        </div>

        {/* input assistance btn */}
        <div className="flex flex-row gap-x-[10px] justify-center">
          {discountRate.map((discount) => {
            const discountNum = Number(discount);
            const isSelected = pkg.sale === discountNum;

            return (
              <div
                key={discount}
                className={`w-[55px] h-[30px] flex items-center justify-center text-center tagFont rounded cursor-pointer
          ${
            isSelected
              ? "shadow bg-main-deep text-white"
              : "shadow text-custom-black"
          }
        `}
                onClick={() =>
                  setPkg((prev) => ({ ...prev, sale: discountNum }))
                }
              >
                {discount}%
              </div>
            );
          })}
        </div>
      </div>

      {/* divider */}
      <hr className="w-full border-0 bg-black/10 h-[1px]" />

      {/* sale price */}
      <div className="flex flex-row justify-between items-center">
        <div className="btnFont">패키지 판매가</div>
        <div className="titleFont font-bold">
          <span className="text-main-deep">
            {Math.floor(((pkg.price * (100 - pkg.sale)) / 100 + 9) / 10) * 10}
          </span>{" "}
          원
        </div>
      </div>
    </div>
  );
};

export default CommonPrice;
