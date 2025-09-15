import { postcodeTheme } from "@constant";
import { getCoordinate } from "@services";
import { useEffect, useRef } from "react";

const SellerMapLab = () => {
  const containerRef = useRef<HTMLDivElement | null>(null);

  const loadDaumPostcode = () => {
    return new Promise<void>((resolve) => {
      if (window.daum && window.daum.Postcode) {
        resolve();
        return;
      }
      const script = document.createElement("script");
      script.src =
        "//t1.daumcdn.net/mapjsapi/bundle/postcode/prod/postcode.v2.js";
      script.async = true;
      script.onload = () => resolve();
      document.body.appendChild(script);
    });
  };

  const handleGetCoordinate = async (addr: string) => {
    const res = await getCoordinate(addr);
    alert(
      `빌딩 이름: ${res.building_name} 위도: ${res.lat} 경도: ${res.lng} 도로명주소: ${res.road_address}`
    );

    return res;
  };

  useEffect(() => {
    loadDaumPostcode().then(() => {
      if (
        containerRef.current &&
        containerRef.current?.childNodes.length === 0
      ) {
        new window.daum.Postcode({
          oncomplete: (data: any) => {
            handleGetCoordinate(String(data.roadAddress));

            return false;
          },
          theme: postcodeTheme,
          width: "100%",
        }).embed(containerRef.current, {
          autoClose: false,
        });
      }
    });
  }, []);

  return (
    <>
      <h1>Postal Code</h1>
      <div ref={containerRef} className="w-full h-[400px]"></div>
    </>
  );
};

export default SellerMapLab;
