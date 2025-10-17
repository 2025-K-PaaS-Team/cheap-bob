import { CommonModal } from "@components/common";
import { NutritionList } from "@constant";
import type { PreferNutritionBaseType, CustomerDetailType } from "@interface";
import { GetCustomerDetail, GetNutrition, WithdrawCustomer } from "@services";
import { formatErrMsg, getTitleByKey } from "@utils";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router";

const My = () => {
  const navigate = useNavigate();
  const [showWarn, setShowWarn] = useState<Boolean>(false);
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");

  const [customer, setCustomer] = useState<CustomerDetailType | null>(null);
  const [nutrition, setNutrition] = useState<PreferNutritionBaseType[] | null>(
    null
  );

  const handlePostWithdraw = async () => {
    setShowWarn(false);
    try {
      await WithdrawCustomer();
      navigate("withdraw");
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
      return;
    }
  };

  // get customer detail
  const handleGetCustomerDetail = async () => {
    try {
      const res = await GetCustomerDetail();
      setCustomer(res);
    } catch (err) {
      setModalMsg("고객 데이터 가져오기에 실패했습니다.");
      setShowModal(true);
    }
  };
  // get customer nutrition
  const handleGetCustomerNutrition = async () => {
    try {
      const res = await GetNutrition();
      setNutrition(res.nutrition_types);
    } catch (err) {
      setModalMsg("영양 데이터 가져오기에 실패했습니다.");
      setShowModal(true);
    }
  };

  useEffect(() => {
    handleGetCustomerDetail();
    handleGetCustomerNutrition();
  }, []);

  return (
    <div className="px-[20px] w-full flex flex-col gap-y-[31px]">
      {/* my info */}
      <div
        onClick={() => navigate("/c/change/info")}
        className="flex flex-col gap-y-[10px]"
      >
        <div className="titleFont">{customer?.nickname} 님</div>
        <div className="bodyFont">{customer?.customer_email}</div>
      </div>

      {/* nutrition goal */}
      <div
        onClick={() => navigate("/c/change/nutrition")}
        className="bg-main-pale border border-main-deep rounded w-full py-[20px] px-[15px]"
      >
        <h1 className="pb-[21px]">영양 목표</h1>
        <div className="flex flex-row">
          {nutrition?.map((n, idx) => (
            <div
              key={idx}
              className="tagFont font-bold bg-black rounded text-white px-[10px] py-[7px]"
            >
              {getTitleByKey(n.nutrition_type, NutritionList)}
            </div>
          ))}
        </div>
      </div>

      {/* bottom list */}
      <div className="flex flex-col">
        {/* prefer menu */}
        <div className="bodyFont font-bold py-[20px] flex flex-row justify-between border-b border-black/10">
          <div onClick={() => navigate("/c/change/menu")}>선호 메뉴</div>
          <div>&gt;</div>
        </div>
        {/* prefer topping */}
        <div className="bodyFont font-bold py-[20px] flex flex-row justify-between border-b border-black/10">
          <div onClick={() => navigate("/c/change/topping")}>선호 토핑</div>
          <div>&gt;</div>
        </div>
        {/* allergy */}
        <div className="bodyFont font-bold py-[20px] flex flex-row justify-between border-b border-black/10">
          <div onClick={() => navigate("/c/change/allergy")}>못먹는 음식</div>
          <div>&gt;</div>
        </div>
        {/* order */}
        <div className="bodyFont font-bold py-[20px] flex flex-row justify-between border-b border-black/10">
          <div onClick={() => navigate("/c/order")}>주문 내역</div>
          <div>&gt;</div>
        </div>
        {/* policy */}
        <div className="bodyFont font-bold py-[20px] flex flex-row justify-between border-b border-black/10">
          <div>서비스 이용약관</div>
          <div>&gt;</div>
        </div>
        {/* logout */}
        <div className="bodyFont font-bold py-[20px] border-b border-black/10">
          <div onClick={() => navigate("/c")}>로그아웃</div>
        </div>
        {/* withdraw */}
        <div
          className="bodyFont font-bold text-sub-red py-[20px]"
          onClick={() => setShowWarn(true)}
        >
          <div>계정 탈퇴</div>
        </div>
      </div>

      {/* show modal */}
      {showModal && (
        <CommonModal
          desc={modalMsg}
          confirmLabel="확인"
          onConfirmClick={() => setShowModal(false)}
          category="green"
        />
      )}

      {/* show warn modal */}
      {showWarn && (
        <CommonModal
          desc="계정 탈퇴 시, <b>가게 정보는 유지</b>되지만<br/> <b>가게가 더이상 타 사용자에게 노출되지 않습니다.</b> <br/> <br/> 탈퇴하시겠습니까?"
          confirmLabel="네, 탈퇴합니다."
          onConfirmClick={handlePostWithdraw}
          onCancelClick={() => setShowWarn(false)}
          category="red"
          className="text-start"
        />
      )}
    </div>
  );
};

export default My;
