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
import { useEffect, useRef, useState } from "react";
import { useLocation, useNavigate, useSearchParams } from "react-router";

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
  const calledRef = useRef(false);
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [showModal, setShowModal] = useState(false);
  const [modalMsg, setModalMsg] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const { pathname } = useLocation();
  const isMobile = /Mobi|Android/i.test(navigator.userAgent);

  const unitPrice = getRoundedPrice(product.price, product.sale);
  const totalAmount = unitPrice * Math.max(1, qty);

  useEffect(() => {
    const paymentId = searchParams.get("paymentId");
    const txId = searchParams.get("txId");
    const transactionType = searchParams.get("transactionType");

    if (!paymentId || !txId) return;

    if (!isMobile) return;

    if (sessionStorage.getItem(`confirmed:${txId}`)) return;
    if (calledRef.current) return;
    calledRef.current = true;

    if (transactionType && transactionType !== "PAYMENT") return;

    (async () => {
      try {
        setIsLoading(true);
        await confrimPayment({ payment_id: paymentId });

        sessionStorage.setItem(`confirmed:${txId}`, "1");

        navigate(pathname, { replace: true });

        setModalMsg(
          "결제가 정상적으로 완료되었습니다. <br/> 3초 후 주문 현황 페이지로 이동합니다."
        );
        setShowModal(true);
        setTimeout(() => navigate("/c/order"), 3000);
      } catch (err: any) {
        setModalMsg(err?.message || "결제 확정에 실패했습니다.");
        setShowModal(true);
      } finally {
        setIsLoading(false);
      }
    })();
  }, [searchParams, pathname, isMobile]);

  const handleInitPayment = async (): Promise<PaymentResponseType | null> => {
    try {
      const res = await initPayment({
        product_id: product.product_id,
        quantity: Math.max(1, qty),
      });
      return res;
    } catch (err: unknown) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
      return null;
    }
  };

  const handleConfirmPayment = async (payment_id: string) => {
    try {
      setIsLoading(true);
      await confrimPayment({ payment_id });
      setModalMsg(
        "결제가 정상적으로 완료되었습니다. <br/> 3초 후 주문 현황 페이지로 이동합니다."
      );
      setShowModal(true);
      setTimeout(() => navigate("/c/order"), 3000);
    } catch (err: unknown) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (!selectedPayment) {
      setModalMsg("결제 수단을 선택해주세요.");
      setShowModal(true);
      return;
    }

    const phoneRegex = /^01\d-\d{3,4}-\d{4}$/;
    if (!phoneRegex.test(customer.phone_number)) {
      setModalMsg("010-1234-5678 형식으로 입력해주세요");
      setShowModal(true);
      return;
    }

    setIsLoading(true);

    const sanitizedPhone = customer.phone_number.replace(/-/g, "");
    const paymentInit = await handleInitPayment();
    if (!paymentInit) {
      setIsLoading(false);
      return;
    }

    const item: ItemType = {
      id: product.product_id,
      name: product.product_name,
      price: unitPrice,
      currency: "KRW",
      currencyLabel: "원",
    };

    try {
      await PortOne.requestPayment({
        storeId: paymentInit.store_id,
        channelKey: paymentInit.channel_id,
        paymentId: paymentInit.payment_id,
        orderName: item.name,
        totalAmount,
        currency: item.currency,
        payMethod: "EASY_PAY",
        popup: { center: true },
        redirectUrl: window.location.href,
        customer: {
          fullName: customer.nickname,
          email: customer.customer_email,
          phoneNumber: sanitizedPhone,
        },
        customData: {
          productId: product.product_id,
          quantity: Math.max(1, qty),
          storeId,
        },
        easyPay: { easyPayProvider: "KAKAOPAY" },
      });

      if (!isMobile) {
        await handleConfirmPayment(paymentInit.payment_id);
      }
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
        <CommonBtn type="submit" category="green" notBottom label="결제하기" />
      </form>

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
