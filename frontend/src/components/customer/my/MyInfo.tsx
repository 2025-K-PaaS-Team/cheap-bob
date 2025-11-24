import type { CustomerDetailType } from "@interface";
import { useNavigate } from "react-router-dom";

interface MyInfoType {
  customer: CustomerDetailType | null;
}

export const MyInfo = ({ customer }: MyInfoType) => {
  const navigate = useNavigate();

  return (
    <div
      onClick={() => navigate("/c/change/info")}
      className="flex flex-col gap-y-[10px]"
    >
      <div className="flex flex-row justify-between items-center">
        <div className="titleFont">{customer?.nickname} 님</div>{" "}
        <img src="/icon/next.svg" alt="nextIcon" />
      </div>
      <div className="bodyFont">{customer?.customer_email}</div>
    </div>
  );
};
