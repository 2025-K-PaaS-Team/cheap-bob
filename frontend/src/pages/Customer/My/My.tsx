import { CommonModal } from "@components/common";
import CommonLoading from "@components/common/CommonLoading";
import { BottomList, MyInfo, NutritionGoal } from "@components/customer/my";

import type { PreferNutritionBaseType, CustomerDetailType } from "@interface";
import { GetCustomerDetail, GetNutrition, WithdrawCustomer } from "@services";
import { formatErrMsg } from "@utils";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const My = () => {
  const navigate = useNavigate();
  const [showWarn, setShowWarn] = useState<boolean>(false);
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");

  const [customer, setCustomer] = useState<CustomerDetailType | null>(null);
  const [nutrition, setNutrition] = useState<PreferNutritionBaseType[] | null>(
    null
  );
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const handlePostWithdraw = async () => {
    setShowWarn(false);
    try {
      await WithdrawCustomer();
      navigate("/withdraw");
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    }
  };

  // get customer detail
  const handleGetCustomerDetail = async () => {
    try {
      const res = await GetCustomerDetail();
      setCustomer(res);
    } catch {
      setModalMsg("고객 데이터 가져오기에 실패했습니다.");
      setShowModal(true);
    }
  };
  // get customer nutrition
  const handleGetCustomerNutrition = async () => {
    try {
      const res = await GetNutrition();
      setNutrition(res.nutrition_types);
    } catch {
      setModalMsg("영양 데이터 가져오기에 실패했습니다.");
      setShowModal(true);
    }
  };

  useEffect(() => {
    const init = async () => {
      await handleGetCustomerDetail();
      await handleGetCustomerNutrition();
      setIsLoading(false);
    };
    init();
  }, []);

  if (isLoading) {
    return <CommonLoading type="data" isLoading={isLoading} />;
  }

  return (
    <div className="px-[20px] w-full h-full flex flex-col gap-y-[31px]">
      {/* my info */}
      <MyInfo customer={customer} />

      {/* nutrition goal */}
      <NutritionGoal nutrition={nutrition} />

      {/* bottom list */}
      <BottomList
        setModalMsg={setModalMsg}
        setShowModal={setShowModal}
        setShowWarn={setShowWarn}
      />

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
