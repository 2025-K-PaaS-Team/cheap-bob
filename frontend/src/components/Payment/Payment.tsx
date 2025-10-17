import { CommonBtn, CommonModal } from "@components/common";
import type {
  CustomerDetailType,
  ItemType,
  PaymentResponseType,
  ProductBaseType,
} from "@interface";
import PortOne from "@portone/browser-sdk/v2";
import { cancelPayment, confrimPayment, initPayment } from "@services";
import { formatErrMsg } from "@utils";
import { useState } from "react";

type PortOneProps = {
  storeId: string;
  product: ProductBaseType;
  customer: CustomerDetailType;
};

const Payment = ({ storeId, product, customer }: PortOneProps) => {
  const [showModal, setShowModal] = useState(false);
  const [modalMsg, setModalMsg] = useState<string>("");

  const item: ItemType = {
    id: product.product_id,
    name: product.product_name,
    price: product.price,
    currency: "KRW",
    currencyLabel: "원",
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
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
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
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
      await cancelPayment(payment_id);
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
        storeId: paymentResult.store_id,
        channelKey: paymentResult.channel_id,
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
          fullName: customer.nickname,
          email: customer.customer_email,
          phoneNumber: customer.phone_number,
        },
        customData: {
          productId: product.product_id,
          quantity: 1,
          storeId: storeId,
        },
      });

      console.log("결제 성공!", response);
    } catch (err: unknown) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    }

    const confirmResult = await handleConfrimPayment(paymentResult.payment_id);
    console.log("confirmResult", confirmResult);
  };

  return (
    <div className="flex flex-col">
      <form onSubmit={handleSubmit}>
        {!item ? (
          <div>결제 정보를 불러오는 중입니다.</div>
        ) : (
          <>
            <CommonBtn
              type="submit"
              category="green"
              width="w-[calc(100%-40px)]"
              notBottom
              className="fixed bottom-10 left-1/2 -translate-x-1/2 z-50"
              label={`${(product.price * product.sale) / 100}원 구매하기 (${
                product.current_stock
              }개 남음)`}
            />
          </>
        )}
      </form>

      {/* show modal */}
      {showModal && (
        <CommonModal
          desc={modalMsg}
          confirmLabel="확인"
          onConfirmClick={() => setShowModal(false)}
          category="green"
        />
      )}
    </div>
  );
};

export default Payment;
