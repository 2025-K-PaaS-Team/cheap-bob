import { CommonBtn, CommonModal } from "@components/common";
import CommonLoading from "@components/common/CommonLoading";
import type { CustomerDetailType } from "@interface";
import { GetCustomerDetail, UpdateCustomerDetail } from "@services";
import { formatErrMsg } from "@utils";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const ChangeCustomerInfo = () => {
  const [customer, setCustomer] = useState<CustomerDetailType | null>(null);
  const navigate = useNavigate();
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const handleGetCustomerDetail = async () => {
      try {
        const res = await GetCustomerDetail();
        setCustomer(res);
      } catch (err) {
        setModalMsg("고객 데이터 가져오기에 실패했습니다.");
        setShowModal(true);
      } finally {
        setIsLoading(false);
      }
    };
    handleGetCustomerDetail();
  }, []);

  const handleUpdateCustomerProfile = async (customer: CustomerDetailType) => {
    try {
      await UpdateCustomerDetail({
        nickname: customer?.nickname ?? "",
        phone_number: customer?.phone_number ?? "",
      });
      navigate(-1);
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    }
  };

  const handleSubmit = () => {
    if (!customer) return;
    handleUpdateCustomerProfile(customer);
  };

  if (isLoading || !customer) {
    return <CommonLoading type="data" isLoading={isLoading} />;
  }

  return (
    <div className="my-[30px] px-[20px] w-full flex flex-col flex-1 justify-between gap-y-[20px]">
      <div className="flex flex-col gap-y-[20px]">
        {/* nickname */}
        <div className="flex flex-col">
          <h1>닉네임</h1>
          {/* input box */}
          <input
            className="w-full  text-[#393939] border-b border-black text-[16px] mt-[30px] pb-1"
            value={customer?.nickname}
            onChange={(e) =>
              setCustomer((prev) =>
                prev
                  ? { ...prev, nickname: e.target.value }
                  : ({
                      nickname: e.target.value,
                      phone_number: "",
                    } as CustomerDetailType)
              )
            }
          />
        </div>
        {/* phone */}
        <div className="flex flex-col">
          <h1>전화번호</h1>
          {/* input box */}
          <input
            className="w-full  text-[#393939] border-b border-black text-[16px] mt-[30px] pb-1"
            value={customer?.phone_number}
            onChange={(e) =>
              setCustomer((prev) =>
                prev
                  ? { ...prev, phone_number: e.target.value }
                  : ({
                      phone_number: e.target.value,
                      nickname: "",
                    } as CustomerDetailType)
              )
            }
          />
        </div>
        {/* email addr */}
        <div className="flex flex-col">
          <h1>이메일 주소</h1>
          {/* input box */}
          <input
            className="w-full  text-[#393939] border-b border-black text-[16px] mt-[30px] pb-1"
            value={customer?.customer_email}
          />
        </div>
      </div>

      {/* save */}
      <CommonBtn
        label="저장"
        onClick={handleSubmit}
        category="green"
        notBottom
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
    </div>
  );
};

export default ChangeCustomerInfo;
