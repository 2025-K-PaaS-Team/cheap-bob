import { CommonBtn, CommonModal, SelectedGrid } from "@components/common";
import CommonLoading from "@components/common/CommonLoading";
import { MenuList } from "@constant";
import { useToast } from "@context";
import { CreatePreferMenu, DeletePreferMenu, GetPreferMenu } from "@services";
import { formatErrMsg } from "@utils";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const ChangeCustomerMenu = () => {
  const { showToast } = useToast();
  const navigate = useNavigate();
  const [selected, setSelected] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");

  const handleGetMenu = async () => {
    try {
      const res = await GetPreferMenu();
      const init = Array.isArray(res.preferred_menus)
        ? res.preferred_menus.map((item) => item.menu_type)
        : [];
      setSelected(init);
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    handleGetMenu();
  }, []);

  const handleClick = async (key: string) => {
    const isSelected = selected.includes(key);

    try {
      if (!isSelected) {
        await CreatePreferMenu(key);
        setSelected((prev) => [...prev, key]);
      } else {
        await DeletePreferMenu(key);
        setSelected((prev) => prev.filter((v) => v !== key));
      }
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    }
  };

  const handleSubmit = () => {
    showToast("선호 메뉴 변경에 성공했어요.", "success");
    navigate(-1);
  };

  if (isLoading) {
    return <CommonLoading type="data" isLoading={isLoading} />;
  }

  return (
    <div className="my-[30px] px-[20px] w-full flex flex-col flex-1 justify-between gap-y-[20px]">
      <div className="flex flex-col gap-y-[20px]">
        <div className="titleFont">
          선호하는 메뉴를 <br />
          선택해주세요
        </div>
        <div className="hintFont]">주문할 때 사장님한테 보여져요</div>
        <SelectedGrid
          data={MenuList}
          selected={selected}
          selectType="menu"
          onClick={handleClick}
        />
      </div>

      <CommonBtn
        label="저장"
        onClick={handleSubmit}
        category="green"
        notBottom
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

export default ChangeCustomerMenu;
