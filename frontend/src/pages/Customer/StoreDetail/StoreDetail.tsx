import { CommonModal } from "@components/common";
import Payment from "@components/Payment/Payment";
import { idxToDow, NutritionList } from "@constant";
import type {
  CustomerDetailType,
  ProductType,
  StoreSearchBaseType,
} from "@interface";
import type { CoordBaseType } from "@interface/common/types";
import {
  AddFavoriteStore,
  GetCustomerDetail,
  getStoreProduct,
  RemoveFavoriteStore,
} from "@services";
import { formatErrMsg } from "@utils";
import dayjs from "dayjs";
import { useEffect, useState } from "react";
import { useLocation, useParams } from "react-router";

const StoreDetail = () => {
  const location = useLocation();
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");
  const { store } = location.state as { store: StoreSearchBaseType };
  const { storeId } = useParams<{ storeId: string }>();
  const [product, setProduct] = useState<ProductType | null>(null);
  const [isFavor, setIsFavor] = useState<boolean>(store.is_favorite);
  const [customer, setCustomer] = useState<CustomerDetailType | null>(null);
  const [startCoord, setStartCoord] = useState<CoordBaseType>({
    lat: "",
    lng: "",
  });
  const [endCoord, setEndCoord] = useState({
    endLat: 0,
    endLng: 0,
  });
  const [descOpen, setDescOpen] = useState<boolean>(false);
  const todayDow = dayjs().day();

  const directionUrl = `http://map.naver.com/index.nhn?slng=${startCoord.lng}&slat=${startCoord.lat}&stext=내위치&elng=${endCoord.endLng}&elat=${endCoord.endLat}&etext=도착가게&menu=route&pathType=1`;
  const handleClickDirection = () => {
    if (!startCoord) return;
    window.open(directionUrl, "_blank");
  };

  // get customer detail
  const handleGetCustomerDetail = async () => {
    try {
      const res = await GetCustomerDetail();
      setCustomer(res);
    } catch (err) {
      setModalMsg("고객 데이터 가져오기에 실패했습니다.");
      setShowModal(true);
    }
  };

  const handleGetProducts = async (id: string) => {
    try {
      const res = await getStoreProduct(id);
      setProduct(res);
    } catch (err: unknown) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    }
  };

  useEffect(() => {
    handleGetCustomerDetail();

    if (storeId) {
      handleGetProducts(storeId);
    }

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
        setModalMsg(formatErrMsg(err));
        setShowModal(true);
      }
    );

    // set end coord
    setEndCoord({
      endLat: Number(store.address.lat),
      endLng: Number(store.address.lng),
    });
  }, [storeId]);

  // add or delete favorite store
  const handleUpdateFavorStore = async (storeId: string, isFavor: boolean) => {
    try {
      if (!isFavor) {
        // add favor store
        await AddFavoriteStore(storeId);
      } else {
        // remove favor store
        await RemoveFavoriteStore(storeId);
      }
      setIsFavor((prev) => !prev);
    } catch (err) {
      setModalMsg("선호 가게 업데이트에 실패했습니다.");
      setShowModal(true);
    }
  };

  return (
    <>
      {product ? (
        <div className="flex flex-col justify-center">
          {/* store image */}
          <div className="bg-[#d9d9d9] h-[290px] relative">
            <img
              src={store.images.find((img) => img.is_main)?.image_url}
              alt="StoreImage"
              className="w-full h-full object-none"
            />
            <div className="absolute bottom-1 left-1 text-center gap-y-[4px] flex flex-col">
              <div className="bg-[#d9d9d9] rounded-[10px] py-[5px] px-[10px]">
                {store.operation_times.find(
                  (dow) => dow.day_of_week === todayDow
                )?.is_currently_open
                  ? "영업중"
                  : "영업 종료"}
              </div>
              <div className="bg-[#d9d9d9] rounded-[10px] py-[5px] px-[10px]">
                {product.products[0].current_stock}개
              </div>
            </div>
          </div>

          <div className="flex flex-col mx-[20px] my-[33px] gap-y-[30px] relative">
            {/* store name */}
            <div className="font-bold text-[15px]">
              {product.store_name}
              {/* favor */}
              <div
                className={`rounded-full absolute top-1 right-1 z-10 w-[41px] h-[41px] p-[5px] ${
                  isFavor ? "bg-red-300" : "bg-[#d9d9d9]"
                } flex justify-center items-center`}
                onClick={() =>
                  handleUpdateFavorStore(product.store_id, isFavor)
                }
              >
                <img
                  src="/icon/heart.svg"
                  alt="FavoriteStore"
                  className="w-5 h-5"
                />
              </div>
              {/* store logo and map */}
              <div className="flex flex-row gap-x-3 mt-[8px]">
                <img
                  src="/icon/direction.svg"
                  alt="directionIcon"
                  onClick={handleClickDirection}
                  width={22}
                />
                <img
                  src="/icon/instagram.svg"
                  alt="instagramIcon"
                  onClick={() => window.open(store.sns.instagram)}
                  width={22}
                />
              </div>
            </div>

            {/* store desc */}
            <div
              className="text-[12px] font-[#6c6c6c]"
              onClick={() => setDescOpen(true)}
            >
              매장 설명 보기 &gt;
            </div>

            {/* store addr */}
            <div className="gap-y-[13px] flex flex-col">
              <div className="font-bold text-[15px]">가게 주소</div>
              <div className="bg-[#BFBFBF] text-[11px] w-fit rounded-[10px] px-[17px] py-[5.5px]">
                {store.address.address} {store.address.detail_address},{" "}
                {store.address.postal_code}
              </div>
            </div>

            {/* store op time */}
            <div className="gap-y-[13px] flex flex-col">
              <div className="font-bold text-[15px]">영업 시간</div>
              <div className="text-[11px]">
                {store.operation_times
                  .sort((a, b) => a.day_of_week - b.day_of_week)
                  .map((dow, idx) => {
                    const todayDow = idxToDow[idx];
                    return (
                      <div>
                        {todayDow} {dow.open_time.slice(0, 5)} ~{" "}
                        {dow.close_time.slice(0, 5)}
                      </div>
                    );
                  })}
              </div>
            </div>

            {/* product name */}
            <div className="gap-y-[13px] flex flex-col">
              <div className="font-bold text-[15px]">
                {product.products[0].product_name}
              </div>
              {/* product desc */}
              <div className="bg-[#BFBFBF] text-[11px] w-fit rounded-[10px] px-[17px] py-[5.5px]">
                {product.products[0].description}
              </div>
            </div>

            {/* nutrition goal */}
            <div className="gap-y-[13px] flex flex-col">
              <div className="font-bold text-[15px]">영양 목표</div>
              <div className="text-[11px] flex flex-row gap-x-[5px]">
                {product.products[0].nutrition_types.map((n) => {
                  const nutritionLabel = NutritionList.find(
                    (item) => item.key === n
                  );
                  if (!nutritionLabel) return null;
                  return (
                    <div
                      key={n}
                      className="bg-[#BFBFBF] w-fit rounded-[10px] px-[17px] py-[5.5px]"
                    >
                      {nutritionLabel.title}
                    </div>
                  );
                })}
              </div>
            </div>

            {/* price */}
            <div className="gap-y-[13px] flex flex-col">
              <div className="font-bold text-[15px]">가격</div>
              {/* original price */}
              <div className="text-[11px]">
                <div className="line-through">
                  {product.products[0].price}원
                </div>
                <div className="text-[16px] font-bold">
                  {(product.products[0].price * product.products[0].sale) / 100}
                  원
                </div>
              </div>
            </div>

            {/* pickup time */}
            <div className="gap-y-[13px] flex flex-col">
              <div className="font-bold text-[15px]">픽업 시간</div>
              {/* pu time */}
              <div className="flex flex-row gap-x-[15px] items-center justify-center">
                <div className="bg-[#BFBFBF] text-[16px] font-bold w-fit rounded-[10px] px-[17px] py-[5.5px]">
                  {store.operation_times
                    .find((dow) => dow.day_of_week === todayDow)
                    ?.pickup_start_time.slice(0, 5)}
                </div>
                ~
                <div className="bg-[#BFBFBF] text-[16px] font-bold w-fit rounded-[10px] px-[17px] py-[5.5px]">
                  {store.operation_times
                    .find((dow) => dow.day_of_week === todayDow)
                    ?.pickup_end_time.slice(0, 5)}
                </div>
              </div>
              {/* pu time desc */}
              <div className="text-[20px] text-center">
                픽업 시간까지 1시간29분
              </div>
            </div>

            {/* notice */}
            <div className="gap-y-[13px] flex flex-col">
              <div className="font-bold text-[15px]">
                주문 후, 꼭 지켜주셔야 해요
              </div>
              {/* desc */}
              <div className="text-[11px]">
                <ol className="list-decimal bg-[#d9d9d9] py-[18px] px-[15px] rounded-[5px] space-y-1">
                  <li className="ml-2">
                    오직 픽업 시간에만 가게에서 픽업할 수 있어요.
                  </li>
                  <li className="ml-2">
                    사장님께 따로 메뉴 요청을 할 수 없어요.
                  </li>
                  <li className="ml-2">
                    픽업 확정 전, 가게 사정에 의해 취소될 수 있어요. 취소사유는
                    구매 내역에서 확인할 수 있어요.
                  </li>
                  <li className="ml-2">
                    주문 취소는 가게의 픽업 확정 이후에는 불가능해요.
                  </li>
                </ol>
              </div>
            </div>

            {storeId && customer && (
              <Payment
                storeId={storeId}
                product={product.products[0]}
                customer={customer}
              />
            )}
          </div>
        </div>
      ) : (
        <div>로딩중...</div>
      )}
      {/* show modal */}
      {showModal && (
        <CommonModal
          desc={modalMsg}
          confirmLabel="확인"
          onConfirmClick={() => setShowModal(false)}
          category="black"
        />
      )}

      {/* show desc modal */}
      {descOpen && (
        <CommonModal
          desc={store.store_introduction}
          confirmLabel="확인"
          onConfirmClick={() => setDescOpen(false)}
          category="black"
        />
      )}
    </>
  );
};

export default StoreDetail;
