// Payment.tsx
import { CommonBtn, CommonModal } from "@components/common";
import CommonLoading from "@components/common/CommonLoading";
import type {
  CustomerDetailType,
  PaymentResponseType,
  ProductBaseType,
} from "@interface";
import PortOne from "@portone/browser-sdk/v2";
import { confrimPayment, initPayment } from "@services";
import { formatErrMsg, getRoundedPrice } from "@utils";
import { useEffect, useRef, useState } from "react";
import { useLocation, useNavigate, useSearchParams } from "react-router-dom";

type PortOneProps = {
  storeId?: string;
  product?: ProductBaseType;
  customer?: CustomerDetailType;
  qty?: number;
  selectedPayment?: string | null;
};

const Payment = ({
  storeId,
  product,
  customer,
  qty = 1,
  selectedPayment,
}: PortOneProps) => {
  const calledRef = useRef(false);
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { pathname } = useLocation();

  const [showModal, setShowModal] = useState(false);
  const [modalMsg, setModalMsg] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const isMobile = /Mobi|Android/i.test(navigator.userAgent);

  useEffect(() => {
    console.log("hello");
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
        const timer = setTimeout(() => navigate("/c/order"), 3000);
        return () => clearTimeout(timer);
      } catch (err: any) {
        setModalMsg(err?.message || "결제 확정에 실패했습니다.");
        setShowModal(true);
      } finally {
        setIsLoading(false);
      }
    })();
  }, [searchParams, pathname, navigate, isMobile]);

  const canPay = !!(storeId && product && customer && selectedPayment);

  const handleInitPayment = async (): Promise<PaymentResponseType | null> => {
    try {
      return await initPayment({
        product_id: product!.product_id,
        quantity: Math.max(1, qty),
      });
    } catch (err) {
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
      const timer = setTimeout(() => navigate("/c/order"), 3000);
      return () => clearTimeout(timer);
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!canPay) return;

    const phoneRegex = /^01\d-\d{3,4}-\d{4}$/;
    if (!phoneRegex.test(customer!.phone_number)) {
      setModalMsg("010-1234-5678 형식으로 입력해주세요");
      setShowModal(true);
      return;
    }

    setIsLoading(true);

    const paymentInit = await handleInitPayment();
    if (!paymentInit) {
      setIsLoading(false);
      return;
    }

    try {
      await PortOne.requestPayment({
        storeId: paymentInit.store_id,
        channelKey: paymentInit.channel_id,
        paymentId: paymentInit.payment_id,
        orderName: product!.product_name,
        totalAmount:
          getRoundedPrice(product!.price, product!.sale) * Math.max(1, qty),
        currency: "KRW",
        payMethod: "EASY_PAY",
        popup: { center: true },
        redirectUrl: window.location.href,
        customer: {
          fullName: customer!.nickname,
          email: customer!.customer_email,
          phoneNumber: customer!.phone_number.replace(/-/g, ""),
        },
        customData: {
          productId: product!.product_id,
          quantity: Math.max(1, qty),
          storeId,
        },
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
    return <CommonLoading type="data" isLoading />;
  }

  if (!canPay) {
    return (
      <>
        {showModal && (
          <CommonModal
            desc={modalMsg}
            confirmLabel="확인"
            onConfirmClick={() => setShowModal(false)}
            category="green"
          />
        )}
      </>
    );
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
