import { CommonBtn, CommonModal } from "@components/common";
import CommonLoading from "@components/common/CommonLoading";
import { CommonPrice } from "@components/seller/common";
import type { ProductBase } from "@interface";
import { GetProduct, UpdateProduct } from "@services";
import { useDashboardStore } from "@store";
import { formatErrMsg, getRoundedPrice } from "@utils";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const ChangePackagePrice = () => {
  const repProductId = useDashboardStore((s) => s.repProductId); // string | null
  const [product, setProduct] = useState<ProductBase | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const [showModal, setShowModal] = useState(false);
  const [modalMsg, setModalMsg] = useState("");
  const navigate = useNavigate();

  const load = async (productId: string) => {
    try {
      const res = await GetProduct(productId);
      // 서버 응답이 ProductBase 형태라고 가정
      setProduct(res as ProductBase);
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (!repProductId) {
      setModalMsg("패키지를 찾을 수 없습니다.");
      setShowModal(true);
      setIsLoading(false);
      return;
    }
    load(repProductId);
  }, [repProductId]);

  const handleSubmit = async () => {
    if (!repProductId) {
      setModalMsg("대표 패키지 ID가 없습니다.");
      setShowModal(true);
      return;
    }
    if (!product) {
      setModalMsg("패키지 정보를 불러오지 못했습니다.");
      setShowModal(true);
      return;
    }

    if (getRoundedPrice(product.price, product.sale) < 1000 || !product.price) {
      setModalMsg("최소 패키지 판매가는 1000원입니다.");
      setShowModal(true);
      return;
    }

    if (product.sale > 99 || product.sale < 1) {
      setModalMsg("할인율은 1~99% 사이여야 합니다.");
      setShowModal(true);
      return;
    }

    try {
      await UpdateProduct(repProductId, {
        ...product,
        price: Math.floor(product.price),
        sale: Math.floor(product.sale),
      });
      navigate(-1);
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    }
  };

  if (isLoading) {
    return <CommonLoading type="data" isLoading={isLoading} />;
  }
  return (
    <div className="my-[30px] px-[20px] w-full flex flex-1 flex-col gap-y-[20px]">
      <div className="flex flex-col flex-1">
        {product && (
          <CommonPrice
            pkg={product}
            setPkg={(next) =>
              setProduct((prev) =>
                typeof next === "function" ? (next as any)(prev) : next
              )
            }
          />
        )}
      </div>

      <CommonBtn
        label="저장"
        onClick={handleSubmit}
        notBottom
        category="green"
      />

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

export default ChangePackagePrice;
