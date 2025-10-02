import { postcodeTheme } from "@constant";
import type { AddressInfoType } from "@interface";
import { getCoordinate } from "@services";
import { useEffect, useRef } from "react";

interface DaumPostcodeProps {
  zonecode: string;
  roadAddress: string;
  sido: string;
  sigungu: string;
  bname: string;
  [key: string]: any;
}

interface PostalCodeProps {
  form: AddressInfoType;
  setForm: (form: Partial<AddressInfoType>) => void;
}

const PostalCode = ({ form, setForm }: PostalCodeProps) => {
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

  // get coordinate + move to map center
  const handleGetCoordinate = async (addr: string) => {
    const coor = await getCoordinate(addr);
    if (mapRef.current) {
      const newCenter = new window.naver.maps.LatLng(coor.lat, coor.lng);
      mapRef.current.setCenter(newCenter);
      mapRef.current.setZoom(16, true);
      // set coordinate form
      setForm({ lng: coor.lng, lat: coor.lat });
    } else {
      console.warn("mapRef가 존재하지 않습니다");
    }

    return coor;
  };

  const openPostalCode = async () => {
    await loadDaumPostcode();

    new window.daum.Postcode({
      oncomplete: (data: DaumPostcodeProps) => {
        handleGetCoordinate(data.roadAddress);
        // set zonecode and roadaddress form
        setForm({
          postal_code: data.zonecode,
          address: data.roadAddress,
          sido: data.sido,
          sigungu: data.sigungu,
          bname: data.bname,
        });
      },
      theme: postcodeTheme,
      width: "100%",
    }).open();
  };

  useEffect(() => {
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
  }, []);

  return (
    <div className="flex flex-col mt-[37px] gap-y-[11px]">
      {/* postal code */}
      <div className="flex flex-row gap-x-[10px] h-[37px]">
        <input
          className="bg-[#D9D9D9] text-[16px] w-full p-3"
          id="postCode"
          readOnly
          value={form.postal_code}
        />
        <button
          className="bg-[#D9D9D9] text-[16px] w-[180px] px-3"
          onClick={() => openPostalCode()}
        >
          우편 번호 찾기
        </button>
      </div>
      {/* road address */}
      <input
        className="bg-[#D9D9D9] text-[16px] w-full h-[37px] p-3"
        id="roadAddr"
        readOnly
        value={form.address}
      />
      {/* detail address */}
      <input
        className="bg-[#D9D9D9] text-[16px] w-full h-[37px] p-3"
        id="detailAddr"
        value={form.detail_address}
        // set detail addr form
        onChange={(e) => setForm({ detail_address: e.target.value })}
      />
      <div
        id="map"
        style={{ width: "100%", height: "250px" }}
        className="mt-[34px]"
      />
    </div>
  );
};

export default PostalCode;
