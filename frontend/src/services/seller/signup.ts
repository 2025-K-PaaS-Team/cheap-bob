import type { CoorBaseType } from "@interface";
import { kakaoApi } from "@services/client";

// GET: GET COORDINATE FROM KAKAO REST API
export const getCoordinate = async (query: string): Promise<CoorBaseType> => {
  const res = await kakaoApi.get(`?query=${query}`);
  const roadAddr = res.data.documents[0].road_address;

  console.log("kakao", res);

  return {
    lng: roadAddr.x,
    lat: roadAddr.y,
  };
};
