import { CommonBtn, HomeSwiper } from "@components/common";
import { routeHomeSwiperMap } from "@constant";
import { useNavigate } from "react-router-dom";
import { Swiper, SwiperSlide } from "swiper/react";
import "swiper/css";
import "swiper/css/navigation";
import "swiper/css/pagination";
import { Autoplay, Pagination } from "swiper/modules";

const RouteHome = () => {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col flex-1 items-center justify-center text-center mx-auto w-full gap-y-[28px]">
      {/* swiper */}
      <Swiper
        loop={true}
        pagination={{ clickable: true }}
        modules={[Pagination, Autoplay]}
        className="mySwiper items-center flex w-full my-[20px]"
        autoplay={{ delay: 3000, disableOnInteraction: false }}
        speed={600}
      >
        {routeHomeSwiperMap.map((slide, idx) => (
          <SwiperSlide key={idx}>
            <HomeSwiper title={slide.title} img={slide.img} />
          </SwiperSlide>
        ))}
      </Swiper>

      <div className="w-full flex flex-col gap-y-[10px] px-[20px]">
        <CommonBtn
          label="고객 페이지로 이동하기"
          onClick={() => navigate("/c")}
          notBottom
        />

        <CommonBtn
          label="점주 페이지로 이동하기"
          onClick={() => navigate("/s")}
          notBottom
        />
      </div>
    </div>
  );
};

export default RouteHome;
