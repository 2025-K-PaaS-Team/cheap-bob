import type {
  ItemType,
  PaymentResponseType,
  ProductBaseType,
} from "@interface";
import PortOne from "@portone/browser-sdk/v2";
import { confrimPayment, initPayment } from "@services";

type PortOneLabProps = {
  storeId: string;
  product: ProductBaseType;
};

const PortOneLab = ({ storeId, product }: PortOneLabProps) => {
  const item: ItemType = {
    id: product.product_id,
    name: product.product_name,
    price: product.price,
    currency: "KRW",
    currencyLabel: "원",
    img: "https://velog.velcdn.com/images/gimgyuwon/profile/e18f35d4-46dd-4ea7-859a-53bfaaad629b/image.png",
  };

  const handleInitPayment = async (): Promise<PaymentResponseType | null> => {
    try {
      const res = await initPayment({
        product_id: product.product_id,
        quantity: 1,
      });
      console.log("초기화 성공", res);
      return res;
    } catch (err: unknown) {
      console.error("등록 실패:", err);
      return null;
    }
  };

  const handleConfrimPayment = async (payment_id: string) => {
    console.log("payment_id", payment_id);
    try {
      const confirm = await confrimPayment({
        payment_id: payment_id,
      });
      console.log("결제 확인 성공", confirm);
      return confirm;
    } catch (err: unknown) {
      console.error("결제 확인 실패", payment_id);
      return null;
    }
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    const paymentResult = await handleInitPayment();
    if (!paymentResult) {
      console.log("paymentResult is not existed", paymentResult);
      return;
    }

    try {
      const response = await PortOne.requestPayment({
        storeId: "store-f7494ada-17a2-49c9-bb23-183d354afb27",
        channelKey: "channel-key-2bde6533-669f-4e5a-ae0c-5a471f10a463",
        paymentId: paymentResult?.payment_id,
        orderName: item.name,
        totalAmount: item.price,
        currency: item.currency,
        payMethod: "EASY_PAY",
        popup: {
          center: true,
        },
        redirectUrl: window.location.href,
        customer: {
          fullName: "김규원",
          email: "gimgyuwon2@gmail.com",
          phoneNumber: "01086910510",
        },
        customData: {
          productId: product.product_id,
          quantity: 1,
          userId: "USR_12345",
          storeId: storeId,
        },
      });

      console.log("결제 성공!", response);
    } catch (err: unknown) {
      console.error("결제 요청 실패:", err);
    }

    const confirmResult = await handleConfrimPayment(paymentResult.payment_id);
    console.log("confirmResult", confirmResult);
  };

  return (
    <div className="flex flex-col space-y-2 p-2 w-full p-2">
      <form onSubmit={handleSubmit}>
        {!item ? (
          <div>결제 정보를 불러오는 중입니다.</div>
        ) : (
          <>
            <div className="flex flex-row gap-x-5">
              <button type="submit" className="p-3 bg-orange-300 rounded-xl">
                결제
              </button>
              <button className="p-3 bg-gray-300 rounded-xl">새로고침</button>
            </div>
          </>
        )}
      </form>
    </div>
  );
};

export default PortOneLab;
