import { CommonBtn, CommonModal } from "@components/common";
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
import { formatErrMsg, getRoundedPrice } from "@utils";
import dayjs from "dayjs";
import { useEffect, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router";
import "swiper/css";
import { Swiper, SwiperSlide } from "swiper/react";

const StoreDetail = () => {
  const navigate = useNavigate();
  const [activeSlide, setActiveSlide] = useState(1);
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
  const now = dayjs();
  const todayDow = (now.day() + 6) % 7;
  const todayOp = store.operation_times.find(
    (dow) => dow.day_of_week === todayDow
  );
  const pickupTime = todayOp?.pickup_start_time
    ? dayjs(now)
        .set("hour", Number(todayOp.pickup_start_time.slice(0, 2)))
        .set("minute", Number(todayOp.pickup_start_time.slice(3, 5)))
        .set("second", Number(todayOp.pickup_start_time.slice(6, 8)))
    : null;

  const diffTime = pickupTime ? pickupTime.diff(now, "minute") : null;

  const [openCheckNoti, setOpenCheckNoti] = useState<boolean>(false);

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
        <div className="relative flex flex-col justify-center mb-[50px]">
          {/* store image */}
          <div className="bg-custom-white h-[230px] w-full relative">
            <Swiper
              loop={true}
              onSlideChange={(swiper) => setActiveSlide(swiper.realIndex + 1)}
              className="mySwiper h-[230px]"
            >
              {store.images.map((img) => (
                <SwiperSlide key={img.image_id}>
                  <img
                    src={img.image_url}
                    alt="StoreImage"
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute inset-0 bg-black/30" />
                </SwiperSlide>
              ))}
            </Swiper>

            {/* overlay */}
            <div className="absolute top-0 left-0 w-full h-full hintFont pointer-events-none">
              {/* img idx  */}
              <div className="absolute top-3 right-3 z-10 bg-[#0A0A0A]/50 btnFont text-white rounded-lg py-[4px] px-[10px] pointer-events-auto">
                {activeSlide} / {store.images.length}
              </div>
              {/* 영업중 / 종료 */}
              <div className="absolute bottom-14 left-3 z-10 bg-custom-white rounded-lg py-[4px] px-[10px] pointer-events-auto">
                {todayOp?.is_currently_open ? "영업중" : "영업 종료"}
              </div>

              {/* 남은 수량 */}
              <div className="absolute bottom-3 left-3 z-10 bg-[#E7E7E7] rounded py-[5.5px] px-[10px] pointer-events-auto">
                {store.products[0].current_stock === 0 ? (
                  <>
                    패키지{" "}
                    <span className="text-sub-orange font-bold">품절</span>
                  </>
                ) : (
                  <>
                    패키지{" "}
                    <span className="text-main-deep font-bold">
                      {store.products[0].current_stock}개 남음
                    </span>
                  </>
                )}
              </div>
            </div>
          </div>

          <div className="relative flex flex-col mx-[20px] my-[33px] gap-y-[30px] relative">
            {/* store representation intro */}
            <div>
              {/* store name */}
              <h1> {product.store_name}</h1>

              {/* favor */}
              <div
                className="rounded-full absolute top-1 right-1 z-10 w-[41px] h-[41px] flex justify-center items-center"
                onClick={() =>
                  handleUpdateFavorStore(product.store_id, isFavor)
                }
              >
                {isFavor ? (
                  <img
                    src="/icon/heartFull.svg"
                    alt="FavoriteStore"
                    className="w-5 h-5"
                  />
                ) : (
                  <img
                    src="/icon/heart.svg"
                    alt="FavoriteStore"
                    className="w-5 h-5"
                  />
                )}
              </div>
              {/* store logo and map */}
              <div className="flex flex-row gap-x-3 mt-[8px]">
                <img
                  src="/icon/direction.svg"
                  alt="directionIcon"
                  onClick={handleClickDirection}
                  width={22}
                />
                {store.sns.instagram && (
                  <img
                    src="/icon/instagram.svg"
                    alt="instagramIcon"
                    onClick={() => window.open(store.sns.instagram)}
                    width={22}
                  />
                )}
                {store.sns.homepage && (
                  <img
                    src="/icon/homeFull.svg"
                    alt="homeIcon"
                    onClick={() => window.open(store.sns.homepage)}
                    width={22}
                  />
                )}

                {store.sns.x && (
                  <img
                    src="/icon/twitter.svg"
                    alt="twitterIcon"
                    onClick={() => window.open(store.sns.x)}
                    width={22}
                  />
                )}
              </div>
            </div>

            {/* store desc */}
            <div
              className="text-[12px] font-[#6c6c6c]"
              onClick={() =>
                navigate("desc", { state: store.store_introduction })
              }
            >
              매장 설명 보기 &gt;
            </div>

            {/* store addr */}
            <div className="gap-y-[13px] flex flex-col">
              <h3>가게 주소</h3>
              <div className="bodyFont">
                {store.address.address} {store.address.detail_address},{" "}
                {store.address.postal_code}
              </div>
            </div>

            {/* store op time */}
            <div className="gap-y-[13px] flex flex-col">
              <h3>영업 시간</h3>
              <div className="tagFont">
                {store.operation_times
                  .filter((dow) => dow.is_open_enabled == true)
                  .sort((a, b) => a.day_of_week - b.day_of_week)
                  .map((dow, idx) => {
                    const todayDow = idxToDow[idx];
                    return (
                      <div key={idx}>
                        {todayDow} {dow.open_time.slice(0, 5)} ~{" "}
                        {dow.close_time.slice(0, 5)}
                      </div>
                    );
                  })}
              </div>
            </div>

            {/* product name */}
            <div className="gap-y-[13px] flex flex-col">
              <h3>{product.products[0].product_name}</h3>
              {/* product desc */}
              <div className="p-[8px] bodyFont border-[#E7E7E7] border rounded text-custom-black">
                {product.products[0].description}
              </div>
            </div>

            {/* nutrition goal */}
            <div className="gap-y-[20px] flex flex-col">
              <h3>영양 목표</h3>
              <div className="tagFont">
                우리 가게의 패키지에서 제공하는 성분들이에요
              </div>
              <div className="tagFont flex flex-row gap-x-[6px]">
                {product.products[0].nutrition_types.map((n) => {
                  const nutritionLabel = NutritionList.find(
                    (item) => item.key === n
                  );
                  if (!nutritionLabel) return null;
                  return (
                    <div
                      key={n}
                      className="bg-main-pale border border-main-deep text-main-deep font-bold w-fit rounded px-[16px] py-[7px]"
                    >
                      {nutritionLabel.title}
                    </div>
                  );
                })}
              </div>
            </div>

            {/* price */}
            <div className="gap-y-[20px] flex flex-col">
              <h3>가격</h3>
              {/* original price */}
              <div className="tagFont">
                <div className="line-through text-[#6C6C6C]">
                  {product.products[0].price.toLocaleString()}원
                </div>
                <div className="flex flex-row items-center gap-x-[10px]">
                  <div className="text-[#6C6C6C]">
                    {product.products[0].sale}%
                  </div>
                  <h1 className="text-[16px] font-bold text-sub-orange">
                    {getRoundedPrice(
                      store.products[0].price,
                      store.products[0].sale
                    ).toLocaleString()}
                    원
                  </h1>
                </div>
              </div>
            </div>

            {/* pickup time */}
            <div className="gap-y-[13px] flex flex-col">
              <h3>픽업 시간</h3>
              {/* pu time */}
              <div className="flex flex-row gap-x-[15px] items-center justify-center text-center font-bold">
                <div className="flex items-center text-main-deep justify-center w-[127px] h-[51px] bg-main-pale border border-male-deep rounded btnFont px-[17px] py-[5.5px]">
                  {todayOp?.pickup_start_time.slice(0, 5)}
                </div>
                ~
                <div className="flex items-center text-main-deep justify-center w-[127px] h-[51px] bg-main-pale border border-male-deep rounded btnFont px-[17px] py-[5.5px]">
                  {todayOp?.pickup_end_time.slice(0, 5)}
                </div>
              </div>
              {/* pu time desc */}
              <h3 className="text-center text-main-deep my-[16px]">
                {diffTime !== null && diffTime > 0 ? (
                  <div>
                    픽업 시간까지 {Math.floor(diffTime / 60)}시간{" "}
                    {diffTime % 60}분
                  </div>
                ) : (
                  <div>픽업 시간이 지났습니다</div>
                )}
              </h3>
            </div>

            {/* notice */}
            <div className="gap-y-[13px] flex flex-col">
              <h3>주문 후 약속</h3>
              {/* desc */}
              <div className="hintFont">
                <ol className="list-decimal bg-custom-white py-[18px] px-[15px] rounded">
                  <li className="ml-4">
                    오직 픽업 시간에만 가게에서 픽업할 수 있어요.
                  </li>
                  <li className="ml-4">
                    사장님께 따로 메뉴 요청을 할 수 없어요.
                  </li>
                  <li className="ml-4">
                    픽업 확정 전, 가게 사정에 의해 취소될 수 있어요.
                  </li>
                  <li className="ml-4">
                    취소사유는 구매 내역에서 확인할 수 있어요.
                  </li>
                  <li className="ml-4">
                    주문 취소는 가게의 픽업 확정 이후에는 불가능해요.
                  </li>
                </ol>
              </div>
            </div>

            {storeId && customer && (
              <div className="">
                {!todayOp?.is_currently_open ? (
                  <CommonBtn category="grey" label="영업시간이 아니예요" />
                ) : product.products[0].current_stock > 0 ? (
                  <CommonBtn
                    category="green"
                    onClick={() => setOpenCheckNoti(true)}
                    label={`${getRoundedPrice(
                      store.products[0].price,
                      store.products[0].sale
                    ).toLocaleString()}원 구매하기 (${
                      product.products[0].current_stock
                    }개 남음)`}
                  />
                ) : (
                  <CommonBtn category="grey" label="품절됐어요" />
                )}
              </div>
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
          category="green"
        />
      )}

      {/* show check modal */}
      {openCheckNoti && (
        <CommonModal
          desc=""
          confirmLabel="확인"
          onConfirmClick={() =>
            navigate("payment", { state: { store, customer } })
          }
          category="green"
          onCancelClick={() => setOpenCheckNoti(false)}
          cancelLabel="이전"
        >
          <div className="flex flex-col text-start p-[10px]">
            <h3 className="mb-[10px]">구매 전 필수체크</h3>
            <div className="bodyFont font-bold">1. 메뉴 요구는 금지</div>
            <div className="hintFont">가게에 따로 메뉴 요청을 할 수 없어요</div>
            <div className="bodyFont font-bold">2. 픽업 시간 엄수</div>
            <div className="hintFont">
              픽업 시간이 지나면 주문이 취소되어 음식이 폐기돼요
            </div>
            <div className="bodyFont font-bold">
              3. 픽업 확정 알림은 꼭 확인!
            </div>
            <div className="hintFont">
              저렴한끼 서비스 또는 이메일로 주문 알림을 확인하세요
            </div>
          </div>
        </CommonModal>
      )}
    </>
  );
};

export default StoreDetail;
