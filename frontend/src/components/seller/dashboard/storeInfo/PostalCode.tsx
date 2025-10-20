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
  setForm: (
    form:
      | Partial<AddressInfoType>
      | ((prev: AddressInfoType) => Partial<AddressInfoType>)
  ) => void;
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

  const handleComplete = async (data: DaumPostcodeProps) => {
    const coor = await getCoordinate(data.roadAddress);
    // get coordinate + move to map center
    if (mapRef.current) {
      const newCenter = new window.naver.maps.LatLng(coor.lat, coor.lng);
      mapRef.current.setCenter(newCenter);
      mapRef.current.setZoom(17, true);
      // set form
      setForm({
        postal_code: data.zonecode,
        address: data.roadAddress,
        sido: data.sido,
        sigungu: data.sigungu,
        bname: data.bname,
        lng: coor.lng,
        lat: coor.lat,
      });
      console.warn(form);
    } else {
      console.warn("mapRef가 존재하지 않습니다");
    }

    return coor;
  };

  const openPostalCode = async () => {
    await loadDaumPostcode();

    new window.daum.Postcode({
      oncomplete: (data: DaumPostcodeProps) => {
        handleComplete(data);
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
        {/* road address */}
        <input
          className="hint w-full h-[37px] p-1 border-b  border-[#393939]"
          id="roadAddr"
          readOnly
          value={form.address}
          placeholder="주소를 입력하세요."
        />
        <button
          className="border border-main-deep border-1 rounded hint w-[180px] px-3 text-nowrap"
          onClick={() => openPostalCode()}
        >
          우편번호 찾기
        </button>
      </div>
      {/* detail address */}
      <input
        className="hint w-full h-[37px] p-1 border-b  border-[#393939]"
        id="detailAddr"
        value={form.detail_address}
        placeholder="상세주소를 입력하세요."
        // set detail addr form
        onChange={(e) => setForm({ detail_address: e.target.value })}
      />
      <div id="map" style={{ width: "100%", height: "201px", zIndex: 0 }} />
    </div>
  );
};

export default PostalCode;
