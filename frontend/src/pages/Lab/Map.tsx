import { useEffect } from "react";

const Map = () => {
  useEffect(() => {
    const script = document.createElement("script");
    script.src = `https://oapi.map.naver.com/openapi/v3/maps.js?ncpKeyId=${
      import.meta.env.VITE_NAVER_MAP_CLIENT_ID
    }`;
    script.async = true;
    document.body.appendChild(script);

    script.onload = () => {
      const _map = new window.naver.maps.Map("map", {
        center: new window.naver.maps.LatLng(37.5666805, 126.9784147),
        zoom: 10,
      });
    };

    return () => {
      document.body.removeChild(script);
    };
  }, []);

  return (
    <>
      <div id="map" style={{ width: "100%", height: "400px" }}></div>;
      <div>this is map page</div>
    </>
  );
};

export default Map;
