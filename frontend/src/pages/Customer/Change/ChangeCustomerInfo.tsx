import { CommonBtn, CommonModal } from "@components/common";
import type { CustomerDetailType } from "@interface";
import { GetCustomerDetail, UpdateCustomerDetail } from "@services";
import { formatErrMsg } from "@utils";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router";

const ChangeCustomerInfo = () => {
  const [customer, setCustomer] = useState<CustomerDetailType | null>(null);
  const navigate = useNavigate();
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");

  useEffect(() => {
    const handleGetCustomerDetail = async () => {
      try {
        const res = await GetCustomerDetail();
        setCustomer(res);
      } catch (err) {
        setModalMsg("고객 데이터 가져오기에 실패했습니다.");
        setShowModal(true);
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

  if (!customer) {
    return <div>로딩 중...</div>;
  }

  return (
    <div className="mt-[30px] px-[20px] w-full flex flex-col gap-y-[80px]">
      {/* nickname */}
      <div className="flex flex-col">
        <h1>닉네임</h1>
        {/* input box */}
        <input
          className="w-full  text-[#393939] border-b border-black text-[16px] mt-[30px]"
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
          className="w-full  text-[#393939] border-b border-black text-[16px] mt-[30px]"
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
          className="w-full  text-[#393939] border-b border-black text-[16px] mt-[30px]"
          value={customer?.customer_email}
        />
      </div>

      {/* save */}
      <CommonBtn label="저장" onClick={handleSubmit} category="green" />

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
