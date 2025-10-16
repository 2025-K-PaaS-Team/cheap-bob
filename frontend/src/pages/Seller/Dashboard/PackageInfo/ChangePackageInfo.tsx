import { useNavigate } from "react-router";

const ChangePackageInfo = () => {
  const navigate = useNavigate();
  const items = [
    { label: "패키지 이름 변경", to: "/s/change/package/name" },
    { label: "패키지 소개 변경", to: "/s/change/package/desc" },
    { label: "영양목표 변경", to: "/s/change/package/nutrition" },
    { label: "패키지 가격 변경", to: "/s/change/package/price" },
    { label: "판매 기본값 변경", to: "/s/change/package/num" },
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

export default ChangePackageInfo;
