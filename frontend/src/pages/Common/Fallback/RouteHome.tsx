import { CommonBtn, HomeSwiper } from "@components/common";
import { homeSwiperMap } from "@constant";
import { Navigate, useNavigate } from "react-router-dom";
import { Swiper, SwiperSlide } from "swiper/react";
import "swiper/css";
import "swiper/css/navigation";
import "swiper/css/pagination";
import { Pagination } from "swiper/modules";

const RouteHome = () => {
  const navigate = useNavigate();
  const loginRole = localStorage.getItem("loginRole");

  if (loginRole === "seller") return <Navigate to="/s" replace />;
  if (loginRole === "customer") return <Navigate to="/c" replace />;

  return (
    <div className="flex flex-col flex-1 items-center justify-center text-center my-[20px] mx-auto w-[calc(100%-40px)] gap-y-[28px]">
      <img src="/typo.svg" alt="errorIcon" className="w-30 mb-5" />
      {/* swiper */}
      <Swiper
        loop={true}
        pagination={{ clickable: true }}
        modules={[Pagination]}
        className="mySwiper items-center flex w-full"
      >
        {homeSwiperMap.map((slide, idx) => (
          <SwiperSlide key={idx}>
            <HomeSwiper title={slide.title} img={slide.img} />
          </SwiperSlide>
        ))}
      </Swiper>

      <div className="w-full flex flex-col gap-y-[10px]">
        <CommonBtn
          label="고객 페이지로 이동하기"
          onClick={() => navigate("/c/stores")}
          category="white"
          notBottom
        />

        <CommonBtn
          label="점주 페이지로 이동하기"
          onClick={() => navigate("/s/dashboard")}
          notBottom
        />
      </div>
    </div>
  );
};

export default RouteHome;
