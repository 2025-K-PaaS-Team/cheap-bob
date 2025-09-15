import type { MapBaseType } from "@interface";
import { kakaoApi } from "@services/client";

// GET: GET COORDINATE FROM KAKAO REST API
export const getCoordinate = async (query: string): Promise<MapBaseType> => {
  const res = await kakaoApi.get(`?query=${query}`);
  const roadAddr = res.data.documents[0].road_address;

  return {
    road_address: roadAddr.address_name,
    building_name: roadAddr.building_name,
    lng: roadAddr.x,
    lat: roadAddr.y,
  };
};
