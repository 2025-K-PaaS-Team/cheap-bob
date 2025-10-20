import Payment from "@components/Payment/Payment";
import type { CustomerDetailType, StoreSearchBaseType } from "@interface";
import { useEffect, useState } from "react";
import { useLocation } from "react-router";

const StorePayment = () => {
  const location = useLocation();
  const { store } = location.state as { store: StoreSearchBaseType };
  const { customer } = location.state as { customer: CustomerDetailType };

  const [qty, setQty] = useState<number>(1);
  const [selectedPayment, setSelectedPayment] = useState<string | null>(null);
  const [myPhone, setMyPhone] = useState<string>("");

  useEffect(() => {
    const digits = customer.phone_number.replace(/-/g, "").slice(0, 11);
    let formatted = digits;
    if (digits.length > 3 && digits.length <= 7) {
      formatted = `${digits.slice(0, 3)}-${digits.slice(3)}`;
    } else if (digits.length > 7) {
      formatted = `${digits.slice(0, 3)}-${digits.slice(3, 7)}-${digits.slice(
        7
      )}`;
    }
    setMyPhone(formatted);
  }, []);

  return (
    <div className="relative h-full flex flex-col p-[20px] gap-y-[39px]">
      {/* 픽업 시간 */}
      <div className="grid grid-cols-3 bodyFont">
        <div className="font-bold">픽업 시간</div>
        <div className="flex flex-row gap-x-[5px]">
          <div>{store.operation_times[0].pickup_start_time.slice(0, 5)}</div>
          <div>~</div>
          <div>{store.operation_times[0].pickup_end_time.slice(0, 5)}</div>
        </div>
      </div>

      {/* 가게 이름 */}
      <div className="grid grid-cols-3 bodyFont">
        <div className="font-bold">가게 이름</div>
        <div>{store.store_name}</div>
      </div>

      {/* 내 연락처 */}
      <div className="grid grid-cols-3 bodyFont">
        <div className="font-bold">내 연락처</div>
        <input
          className="col-span-2 border-b border-black"
          value={myPhone}
          onChange={(e) => {
            const val = e.target.value;
            if (/^[0-9-]*$/.test(val)) {
              const digits = val.replace(/-/g, "").slice(0, 11);
              let formatted = digits;
              if (digits.length > 3 && digits.length <= 7) {
                formatted = `${digits.slice(0, 3)}-${digits.slice(3)}`;
              } else if (digits.length > 7) {
                formatted = `${digits.slice(0, 3)}-${digits.slice(
                  3,
                  7
                )}-${digits.slice(7)}`;
              }
              setMyPhone(formatted);
            }
          }}
        />
      </div>

      {/* 패키지 명 */}
      <div className="grid grid-cols-3 bodyFont">
        <div className="font-bold">패키지 명</div>
        <div>{store.products[0].product_name}</div>
      </div>

      {/* 수량 */}
      <div className="flex flex-row justify-between bodyFont items-center">
        <div className="font-bold">수량</div>
        <div className="flex flex-row items-center gap-x-[30px]">
          <div className="titleFont">{qty}</div>
          <div className="flex flex-col text-main-deep text-[15px]">
            <div onClick={() => setQty((prev) => prev + 1)}>▲</div>
            <div onClick={() => setQty((prev) => Math.max(prev - 1, 1))}>▼</div>
          </div>
        </div>
      </div>

      {/* 결제 수단 */}
      <div className="flex flex-col gap-y-[20px]">
        <div className="font-bold bodyFont">결제 수단</div>
        <div className="flex flex-row gap-x-[10px]">
          <input
            type="checkbox"
            checked={selectedPayment === "kakaopay"}
            onChange={() =>
              setSelectedPayment((prev) =>
                prev === "kakaopay" ? null : "kakaopay"
              )
            }
          />
          <img src="/icon/kakaopay.svg" alt="kakaopay" width="35px" />
          <div className="tagFont">카카오페이</div>
        </div>
      </div>

      {/* 최종 결제 금액 */}
      <h3 className="absolute bottom-30 right-5">
        최종 결제금액:{" "}
        {Math.floor(
          ((store.products[0].price * (100 - store.products[0].sale)) / 100 +
            9) /
            10
        ) * 10}
        원
      </h3>

      <Payment
        storeId={store.store_id}
        product={store.products[0]}
        customer={{ ...customer, phone_number: myPhone }}
        qty={qty}
        selectedPayment={selectedPayment}
      />
    </div>
  );
};

export default StorePayment;
