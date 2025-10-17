import { CommonBtn, CommonModal, SelectedGrid } from "@components/common";
import { ToppingList } from "@constant";
import { CreateTopping, DeleteTopping, GetTopping } from "@services";
import { formatErrMsg } from "@utils";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router";

const ChangeCustomerTopping = () => {
  const navigate = useNavigate();
  const [selected, setSelected] = useState<string[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");

  const handleGetTopping = async () => {
    try {
      const res = await GetTopping();
      const init = Array.isArray((res as any).topping_types)
        ? res.topping_types.map((item) => item.topping_type)
        : [];
      setSelected(init);
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    handleGetTopping();
  }, []);

  const handleClick = async (key: string) => {
    const isSelected = selected.includes(key);

    try {
      if (!isSelected) {
        await CreateTopping(key);
        setSelected((prev) => [...prev, key]);
      } else {
        await DeleteTopping(key);
        setSelected((prev) => prev.filter((v) => v !== key));
      }
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    }
  };

  const handleSubmit = () => {
    navigate(-1);
  };

  if (loading) return <div className="mt-[30px] px-[20px]">로딩중…</div>;

  return (
    <div className="relative mt-[30px]  px-[20px] w-full flex flex-col gap-y-[20px]">
      <div className="titleFont">
        선호하는 토핑을 <br />
        선택해주세요
      </div>
      <div className="hintFont]">주문할 때 사장님한테 보여져요</div>

      <div className="mb-[130px]">
        <SelectedGrid
          data={ToppingList}
          selected={selected}
          selectType="topping"
          onClick={handleClick}
        />
      </div>

      <CommonBtn label="저장" onClick={handleSubmit} category="green" />

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

export default ChangeCustomerTopping;
