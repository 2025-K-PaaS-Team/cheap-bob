import { useNavigate } from "react-router";
import dummy from "../../assets/dummy.jpg";

const StoreList = () => {
  const navigate = useNavigate();
  const handleClick = (link: string) => {
    navigate(link);
  };

  return (
    <div
      className="flex flex-col justify-center p-8"
      onClick={() => handleClick("/store-detail")}
    >
      {/* list */}
      <div className="border-1 border-gray-400 shadow-md rounded-lg flex flex-col">
        {/* img */}
        <img src={dummy} alt="dummyStoreImg" />
        {/* desc */}
        <div className="flex flex-row justify-between items-center p-4">
          {/* store info left */}
          <div>
            <div className="font-bold">김가네 갈비찜</div>
            <div>서울 광화문 어쩌구1로 3길</div>
            <div>4.2km</div>
          </div>
          {/* store info right */}
          <div className="text-end">
            <div className="text-gray-700">26000원</div>
            <div className="font-bold text-2xl">8282원</div>
          </div>
        </div>
      </div>
    </div>
  );
  0;
};

export default StoreList;
