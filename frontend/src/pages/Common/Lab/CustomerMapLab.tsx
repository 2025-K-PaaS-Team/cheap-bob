import type { CoordBaseType } from "@interface/common/types";
import { useEffect, useState } from "react";

const CustomerMapLab = () => {
  const [startCoord, setStartCoord] = useState<CoordBaseType>({
    lat: "",
    lng: "",
  });
  const endCoord = {
    endLat: 37.2974415,
    endLng: 126.8355968,
  };
  const directionUrl = `http://map.naver.com/index.nhn?slng=${startCoord.lng}&slat=${startCoord.lat}&stext=내위치&elng=${endCoord.endLng}&elat=${endCoord.endLat}&etext=도착가게&menu=route&pathType=1`;

  const handleClickDirection = () => {
    if (!startCoord) return;
    window.open(directionUrl, "_blank");
  };

  useEffect(() => {
    // Get current coord
    navigator.geolocation.getCurrentPosition(
      (success) => {
        const crd = success.coords;
        setStartCoord({
          lat: String(crd.latitude),
          lng: String(crd.longitude),
        });
      },
      (err) => {
        console.warn(`ERROR(${err.code}): ${err.message}`);
      }
    );
  }, []);

  return (
    <>
      <img
        src="/icon/direction.svg"
        alt="directionIcon"
        onClick={handleClickDirection}
      />
    </>
  );
};

export default CustomerMapLab;
