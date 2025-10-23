import { CommonBtn, CommonModal } from "@components/common";
import CommonLoading from "@components/common/CommonLoading";
import { useToast } from "@context";
import type { ProductBase } from "@interface";
import { GetProduct, UpdateProduct } from "@services";
import { useDashboardStore } from "@store";
import { formatErrMsg, validateLength } from "@utils";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const ChangePackageName = () => {
  const { showToast } = useToast();
  const navigate = useNavigate();

  const repProductId = useDashboardStore((s) => s.repProductId); // string | null
  const [product, setProduct] = useState<ProductBase | null>(null);
  const [name, setName] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const [showModal, setShowModal] = useState(false);
  const [modalMsg, setModalMsg] = useState("");

  const load = async (productId: string) => {
    try {
      const res = await GetProduct(productId);
      setProduct(res);
      setName((res as any).product_name ?? "");
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (!repProductId) {
      setIsLoading(false);
      setModalMsg("패키지를 찾을 수 없습니다.");
      setShowModal(true);
      navigate(-1);
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
    if (!validateLength(name.trim(), 1, 15)) {
      setModalMsg("패키지 이름은 1~15자여야 합니다.");
      setShowModal(true);
      return;
    }

    const payload: ProductBase = {
      ...product,
      product_name: name.trim(),
    } as ProductBase;

    try {
      await UpdateProduct(repProductId, payload);
      showToast("패키지 이름 변경에 성공했어요.", "success");
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
    <div className="my-[30px] px-[20px] w-full flex flex-col flex-1">
      <div className="flex flex-col flex-1 gap-y-[40px]">
        <div className="titleFont">
          변경할 <span className="font-bold">패키지의 이름</span>을 <br />{" "}
          입력해 주세요.
        </div>

        <input
          className="w-full h-[46px] border-b  border-[#393939] text-[16px]"
          placeholder="패키지의 이름을 입력해 주세요"
          value={name}
          onChange={(e) => setName(e.target.value)}
          maxLength={15}
        />
      </div>

      <CommonBtn
        label="저장"
        notBottom
        onClick={() => handleSubmit()}
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

export default ChangePackageName;
