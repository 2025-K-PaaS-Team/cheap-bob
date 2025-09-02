import type { ItemType, PaymentStatusType } from "@interface";
import PortOne from "@portone/browser-sdk/v2";
import { useState } from "react";

const PortOneLab = () => {
  const [paymentStatus, setPaymentStatus] = useState<PaymentStatusType>({
    status: "IDLE",
  });

  // const [item, setItem] = useState(null);
  // dummy item
  const item: ItemType = {
    id: 1219,
    name: "행복한하루",
    price: 1000,
    currency: "KRW",
    currencyLabel: "원",
    img: "https://velog.velcdn.com/images/gimgyuwon/profile/e18f35d4-46dd-4ea7-859a-53bfaaad629b/image.png",
  };

  const randomId = () => {
    return [...crypto.getRandomValues(new Uint32Array(2))]
      .map((word) => word.toString(16).padStart(8, "0"))
      .join("");
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setPaymentStatus({ status: "PENDING" });
    console.log("paymentStatus:", paymentStatus);
    const paymentId = randomId();
    const payment = await PortOne.requestPayment({
      storeId: "store-f7494ada-17a2-49c9-bb23-183d354afb27",
      channelKey: "channel-key-2bde6533-669f-4e5a-ae0c-5a471f10a463",
      paymentId,
      orderName: item.name,
      totalAmount: item.price,
      currency: item.currency,
      payMethod: "EASY_PAY",
      customer: {
        fullName: "김규원",
        email: "gimgyuwon2@gmail.com",
        phoneNumber: "01086910510",
      },
      customData: {
        item: item.id,
      },
    });

    if (!payment) {
      setPaymentStatus({ status: "FAILED" });
      return;
    }

    // 실패 케이스
    if (payment.code !== undefined) {
      setPaymentStatus({
        status: "FAILED",
        message: payment?.message,
      });
    }
  };

  return (
    <div className="flex flex-col space-y-2 p-2 w-full p-2">
      <h2>결제 테스트</h2>
      <form onSubmit={handleSubmit}>
        <div className="rounded-xl w-full bg-yellow-200 p-3">
          {!item ? (
            <div>결제 정보를 불러오는 중입니다.</div>
          ) : (
            <>
              {" "}
              <div className="font-bold">{item.name}</div>
              <img src={item.img} alt="" />
              <div>
                {item.price}
                {item.currencyLabel}
              </div>
              <div className="flex flex-row gap-x-5">
                <button type="submit" className="p-3 bg-orange-300 rounded-xl">
                  결제
                </button>
                <button className="p-3 bg-gray-300 rounded-xl">새로고침</button>
              </div>
            </>
          )}
        </div>
      </form>
    </div>
  );
};

export default PortOneLab;
