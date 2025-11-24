import type { ProductBaseType, StoreSearchBaseType } from "@interface";
import "swiper/css";
import { Swiper, SwiperSlide } from "swiper/react";

interface StoreImgType {
  store: StoreSearchBaseType;
  setActiveSlide: (idx: number) => void;
  activeSlide: number;
  isStoreOpenWindow: boolean;
  mainProd: ProductBaseType;
}

export const StoreImg = ({
  store,
  setActiveSlide,
  activeSlide,
  isStoreOpenWindow,
  mainProd,
}: StoreImgType) => {
  return (
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
        {/* img idx */}
        <div className="absolute top-3 right-3 z-10 bg-[#0A0A0A]/50 btnFont text-white rounded-lg py-[4px] px-[10px] pointer-events-auto">
          {activeSlide} / {store.images.length}
        </div>

        <div className="absolute bottom-14 left-3 z-10 bg-custom-white rounded-lg py-[4px] px-[10px] pointer-events-auto">
          {isStoreOpenWindow ? "영업중" : "영업 종료"}
        </div>

        <div className="absolute bottom-3 left-3 z-10 bg-[#E7E7E7] rounded py-[5.5px] px-[10px] pointer-events-auto">
          {mainProd.current_stock === 0 ? (
            <>
              패키지 <span className="text-sub-orange font-bold">품절</span>
            </>
          ) : (
            <>
              패키지{" "}
              <span className="text-main-deep font-bold">
                {mainProd.current_stock}개 남음
              </span>
            </>
          )}
        </div>
      </div>
    </div>
  );
};
