import { useEffect } from "react";

const Map = () => {
  useEffect(() => {
    let map: any;

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
      map = new window.naver.maps.Map("map", {
        center: new window.naver.maps.LatLng(37.5666805, 126.9784147),
        zoom: 10,
        mapTypeId: window.naver.maps.MapTypeId.NORMAL,
      });
    };

    const setCurrentLocation = () => {
      if (!navigator.geolocation) return;
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          const crd = pos.coords;
          const location = new window.naver.maps.LatLng(
            crd.latitude,
            crd.longitude
          );
          map.setCenter(location);
          map.setZoom(10);
        },
        (err) => {
          console.warn(`ERROR(${err.code}): ${err.message}`);
        }
      );
    };

    loadScript().then(() => {
      initMap();
      setCurrentLocation();
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
      <h1>Lab page: Naver Map API</h1>
      <div id="map" style={{ width: "100%", height: "400px" }}></div>;
    </>
  );
};

export default Map;
