import { CommonBtn, CommonModal } from "@components/common";
import CommonLoading from "@components/common/CommonLoading";
import type {
  CustomerDetailType,
  ItemType,
  PaymentResponseType,
  ProductBaseType,
} from "@interface";
import PortOne from "@portone/browser-sdk/v2";
import { confrimPayment, initPayment } from "@services";
import { formatErrMsg, getRoundedPrice } from "@utils";
import { useState } from "react";
import { useNavigate } from "react-router";

type PortOneProps = {
  storeId: string;
  product: ProductBaseType;
  customer: CustomerDetailType;
  qty: number;
  selectedPayment: string | null;
};

const Payment = ({
  storeId,
  product,
  customer,
  qty,
  selectedPayment,
}: PortOneProps) => {
  const navigate = useNavigate();
  const [showModal, setShowModal] = useState(false);
  const [modalMsg, setModalMsg] = useState<string>("");
  const roundedPrice = getRoundedPrice(product.price, product.sale);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const item: ItemType = {
    id: product.product_id,
    name: product.product_name,
    price: roundedPrice,
    currency: "KRW",
    currencyLabel: "원",
  };

  const handleInitPayment = async (): Promise<PaymentResponseType | null> => {
    try {
      const res = await initPayment({
        product_id: product.product_id,
        quantity: qty,
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
      setModalMsg(
        "결제가 정상적으로 완료되었습니다. <br/> 3초 후 주문 현황 페이지로 이동합니다."
      );
      setShowModal(true);
      setTimeout(() => navigate("/c/order"), 3000);
    } catch (err: unknown) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    }
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (!selectedPayment) {
      setModalMsg("결제 수단을 선택해주세요.");
      setShowModal(true);
      return;
    }

    setIsLoading(true);

    const phoneRegex = /^01\d-\d{3,4}-\d{4}$/;
    if (!phoneRegex.test(customer.phone_number)) {
      setModalMsg("010-1234-5678 형식으로 입력해주세요");
      setShowModal(true);
      return;
    }

    const sanitizedPhone = customer.phone_number.replace(/-/g, "");

    const paymentResult = await handleInitPayment();
    if (!paymentResult) {
      console.log("paymentResult is not existed", paymentResult);
      return;
    }

    try {
      await PortOne.requestPayment({
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
          phoneNumber: sanitizedPhone,
        },
        customData: {
          productId: product.product_id,
          quantity: 1,
          storeId: storeId,
        },
      });

      await handleConfrimPayment(paymentResult.payment_id);
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return <CommonLoading type="data" isLoading={isLoading} />;
  }

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
              notBottom
              // className="absolute bottom-5 left-1/2 -translate-x-1/2 z-50"
              label="결제하기"
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
