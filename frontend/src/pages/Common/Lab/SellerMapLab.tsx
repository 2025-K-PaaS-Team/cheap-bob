import { postcodeTheme } from "@constant";
import { getCoordinate } from "@services";
import { useEffect, useRef } from "react";

const SellerMapLab = () => {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<any>(null);

  // load postal code
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

  // 좌표 불러오기 + 네이버 지도 이동
  const handleGetCoordinate = async (addr: string) => {
    const res = await getCoordinate(addr);
    alert(
      `빌딩 이름: ${res.building_name} 위도: ${res.lat} 경도: ${res.lng} 도로명주소: ${res.road_address}`
    );
    if (mapRef.current) {
      const newCenter = new window.naver.maps.LatLng(res.lat, res.lng);
      alert(newCenter);
      mapRef.current.setCenter(newCenter);
      mapRef.current.setZoom(16, true);
    } else {
      console.warn("mapRef가 존재하지 않습니다");
    }

    return res;
  };

  useEffect(() => {
    // Get kakao postal code
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

    // Get naver map
    const loadScript = () => {
      return new Promise<void>((resolve) => {
        const script = document.createElement("script");
        script.src = `https://oapi.map.naver.com/openapi/v3/maps.js?ncpKeyId=${
          import.meta.env.VITE_NAVER_MAP_CLIENT_ID
        }`;
        script.async = true;
        script.onload = () => resolve();
        document.body.appendChild(script);
      });
    };

    const initMap = () => {
      mapRef.current = new window.naver.maps.Map("map", {
        center: new window.naver.maps.LatLng(37.5666805, 126.9784147),
        zoom: 10,
        mapTypeId: window.naver.maps.MapTypeId.NORMAL,
      });
    };

    loadScript().then(() => {
      initMap();
    });

    return () => {
      const scripts = document.querySelectorAll(
        'script[src*="oapi.map.naver.com"]'
      );
      scripts.forEach((s) => s.remove());
    };
  }, []);

  return (
    <>
      <h1>매장 위치 등록 실험실</h1>
      <div ref={containerRef} className="w-full h-[500px] overflow-y-auto" />
      <div id="map" style={{ width: "100%", height: "250px" }} />;
    </>
  );
};

export default SellerMapLab;
