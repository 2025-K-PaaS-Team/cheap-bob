import { useNavigate } from "react-router-dom";

const ChangeStoreInfo = () => {
  const navigate = useNavigate();
  const items = [
    { label: "매장 이름 변경", to: "/s/change/store/name" },
    { label: "매장 소개 변경", to: "/s/change/store/desc" },
    { label: "매장 연락처 변경", to: "/s/change/store/num" },
    { label: "매장 주소 변경", to: "/s/change/store/addr" },
    { label: "이미지 등록 및 변경", to: "/s/change/store/img" },
  ];

  return (
    <div className="mx-[35px]">
      {items.map((item, idx) => (
        <div key={idx}>
          <div
            className="text-[16px] py-[20px] border-b-[1px] border-black/10"
            onClick={() => navigate(item.to)}
          >
            {item.label}
          </div>
        </div>
      ))}
    </div>
  );
};

export default ChangeStoreInfo;
