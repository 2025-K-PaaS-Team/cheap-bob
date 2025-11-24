import { CommonModal } from "@components/common";
import CommonLoading from "@components/common/CommonLoading";
import DetailHeader from "@components/customer/storeDetail";
import { NutritionList } from "@constant";
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
import { buildWindow, inWindow, parseToday } from "dayjs-time-window";
import { useEffect, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import { StoreImg } from "./StoreImg";
import { StoreIntro } from "./StoreIntro";
import { StoreAddr } from "./StoreAddr";
import { StoreOpTime } from "./StoreOpTime";
import { StoreNotice } from "./StoreNotice";
import { StoreStatus } from "./StoreStatus";

const StoreDetail = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { storeId } = useParams<{ storeId: string }>();

  const storeFromState =
    (location.state as { store?: StoreSearchBaseType } | null)?.store ?? null;

  const [isLoading, setIsLoading] = useState<boolean>(true);

  const [activeSlide, setActiveSlide] = useState(1);
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");

  const [store, setStore] = useState<StoreSearchBaseType | null>(
    storeFromState
  );
  const [product, setProduct] = useState<ProductType | null>(null);
  const [isFavor, setIsFavor] = useState<boolean>(
    storeFromState?.is_favorite ?? false
  );
  const [customer, setCustomer] = useState<CustomerDetailType | null>(null);

  const [startCoord, setStartCoord] = useState<CoordBaseType>({
    lat: "",
    lng: "",
  });
  const [endCoord, setEndCoord] = useState({ endLat: 0, endLng: 0 });

  const [openCheckNoti, setOpenCheckNoti] = useState<boolean>(false);

  const now = dayjs();
  const todayDow = (now.day() + 6) % 7;
  const todayOp =
    store?.operation_times.find((dow) => dow.day_of_week === todayDow) ?? null;

  const minutesUntil = (target: dayjs.Dayjs | null) =>
    target && target.valueOf() > now.valueOf()
      ? target.diff(now, "minute")
      : null;

  const { start: openStart, end: openEnd } = buildWindow(
    todayOp?.open_time,
    todayOp?.close_time
  );

  const pickupEnd = parseToday(now, todayOp?.pickup_end_time);

  const isStoreOpenWindow =
    !!todayOp?.is_open_enabled && inWindow(dayjs(), openStart, openEnd);

  const isPickupNotEnded = !!pickupEnd && now.valueOf() <= pickupEnd.valueOf();

  const minutesToPickupEnd = minutesUntil(pickupEnd);

  const directionUrl = `https://map.naver.com/index.nhn?slng=${startCoord.lng}&slat=${startCoord.lat}&stext=내위치&elng=${endCoord.endLng}&elat=${endCoord.endLat}&etext=도착가게&menu=route&pathType=1`;
  const handleClickDirection = () => {
    if (!startCoord?.lat || !startCoord?.lng) return;
    window.open(directionUrl, "_blank");
  };

  const handleGetCustomerDetail = async () => {
    const res = await GetCustomerDetail();
    setCustomer(res);
  };

  const handleGetProducts = async (id: string) => {
    const res = await getStoreProduct(id);
    setProduct(res);
  };

  useEffect(() => {
    const init = async () => {
      try {
        if (!storeFromState || !storeId) {
          navigate("/c/stores", { replace: true });
          return;
        }
        setStore(storeFromState);
        setIsFavor(!!storeFromState.is_favorite);

        await Promise.all([
          handleGetCustomerDetail(),
          storeId ? handleGetProducts(storeId) : Promise.resolve(),
        ]);

        // 현재 위치
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

        // 도착지 좌표
        setEndCoord({
          endLat: Number(storeFromState.address.lat),
          endLng: Number(storeFromState.address.lng),
        });
      } catch (err) {
        setModalMsg(formatErrMsg(err));
        setShowModal(true);
      } finally {
        setIsLoading(false);
      }
    };

    init();
  }, [storeId, storeFromState, navigate]);

  const handleUpdateFavorStore = async (
    targetStoreId: string,
    nowFavor: boolean
  ) => {
    try {
      if (!nowFavor) {
        await AddFavoriteStore(targetStoreId);
      } else {
        await RemoveFavoriteStore(targetStoreId);
      }
      setIsFavor((prev) => !prev);
    } catch {
      setModalMsg("선호 가게 업데이트에 실패했습니다.");
      setShowModal(true);
    }
  };

  if (isLoading || !product || !store) {
    return <CommonLoading type="data" isLoading={true} />;
  }

  const mainProd = product.products[0];

  return (
    <div className="flex flex-col">
      <DetailHeader name={product.store_name || ""} />

      <div className="relative flex flex-col justify-center mb-[50px]">
        {/* store image */}
        <StoreImg
          store={store}
          setActiveSlide={setActiveSlide}
          activeSlide={activeSlide}
          isStoreOpenWindow={isStoreOpenWindow}
          mainProd={mainProd}
        />

        <div className="relative flex flex-col mx-[20px] my-[33px] gap-y-[30px]">
          {/* store representation intro */}
          <StoreIntro
            store={store}
            product={product}
            handleUpdateFavorStore={handleUpdateFavorStore}
            handleClickDirection={handleClickDirection}
            isFavor={isFavor}
          />

          {/* store desc */}
          <div
            className="text-[12px] text-[#6c6c6c] cursor-pointer"
            onClick={() =>
              navigate("desc", {
                state: {
                  desc: store.store_introduction,
                  name: store.store_name,
                  phone: store.store_phone,
                },
              })
            }
          >
            매장 소개 보기 &gt;
          </div>

          {/* store addr */}
          <StoreAddr store={store} />

          {/* store op time */}
          <StoreOpTime store={store} />

          {/* product name + desc */}
          <div className="gap-y-[13px] flex flex-col">
            <h3>{mainProd.product_name}</h3>
            <div className="p-[8px] bodyFont border-[#E7E7E7] border rounded text-custom-black">
              {mainProd.description}
            </div>
          </div>

          {/* nutrition goal */}
          <div className="gap-y-[20px] flex flex-col">
            <h3>영양 목표</h3>
            <div className="tagFont">
              우리 가게의 패키지에서 제공하는 성분들이에요
            </div>
            <div className="tagFont flex flex-row gap-x-[6px] flex-wrap">
              {mainProd.nutrition_types.map((n) => {
                const label = NutritionList.find((item) => item.key === n);
                if (!label) return null;
                return (
                  <div
                    key={n}
                    className="bg-main-pale border border-main-deep text-main-deep font-bold w-fit rounded px-[16px] py-[7px]"
                  >
                    {label.title}
                  </div>
                );
              })}
            </div>
          </div>

          {/* price */}
          <div className="gap-y-[20px] flex flex-col">
            <h3>가격</h3>
            <div className="tagFont">
              <div className="line-through text-[#6C6C6C]">
                {mainProd.price.toLocaleString()}원
              </div>
              <div className="flex flex-row items-center gap-x-[10px]">
                <div className="text-[#6C6C6C]">{mainProd.sale}%</div>
                <h1 className="text-[16px] font-bold text-sub-orange">
                  {getRoundedPrice(
                    mainProd.price,
                    mainProd.sale
                  ).toLocaleString()}
                  원
                </h1>
              </div>
            </div>
          </div>

          {/* pickup time */}
          <div className="gap-y-[13px] flex flex-col">
            <h3>픽업 시간</h3>
            <div className="flex flex-row gap-x-[15px] items-center justify-center text-center font-bold">
              <div className="flex items-center text-main-deep justify-center w-[127px] h-[51px] bg-main-pale border border-main-deep rounded btnFont px-[17px] py-[5.5px]">
                {todayOp?.pickup_start_time?.slice(0, 5) ?? "--:--"}
              </div>
              ~
              <div className="flex items-center text-main-deep justify-center w-[127px] h-[51px] bg-main-pale border border-main-deep rounded btnFont px-[17px] py-[5.5px]">
                {todayOp?.pickup_end_time?.slice(0, 5) ?? "--:--"}
              </div>
            </div>

            <h3 className="text-center text-main-deep my-[16px]">
              {minutesToPickupEnd !== null ? (
                <div>
                  픽업 종료까지 {Math.floor(minutesToPickupEnd / 60)}시간{" "}
                  {minutesToPickupEnd % 60}분
                </div>
              ) : (
                <div>오늘 픽업 시간이 지났습니다</div>
              )}
            </h3>
          </div>

          {/* notice */}
          <StoreNotice />

          {storeId && customer && (
            // storeStatus
            <StoreStatus
              mainProd={mainProd}
              isStoreOpenWindow={isStoreOpenWindow}
              isPickupNotEnded={isPickupNotEnded}
              setOpenCheckNoti={setOpenCheckNoti}
            />
          )}
        </div>

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
              <div className="hintFont">
                가게에 따로 메뉴 요청을 할 수 없어요
              </div>
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
      </div>
    </div>
  );
};

export default StoreDetail;
