import { HomeSwiper, LoginButton } from "@components/common/home";
import { homeSwiperMap } from "@constant";
import { useNavigate } from "react-router";
import "swiper/css";
import "swiper/css/navigation";
import "swiper/css/pagination";
import { Pagination } from "swiper/modules";
import { Swiper, SwiperSlide } from "swiper/react";

const Home = () => {
  const navigate = useNavigate();
  localStorage.clear();

  return (
    <div className="flex flex-col flex-1 justify-around w-full pt-[30px]">
      {/* swiper */}
      <Swiper
        pagination={{ clickable: true }}
        modules={[Pagination]}
        className="mySwiper items-center flex h-fit w-full"
      >
        {homeSwiperMap.map((slide, idx) => (
          <SwiperSlide key={idx}>
            <HomeSwiper title={slide.title} img={slide.img} />
          </SwiperSlide>
        ))}
      </Swiper>

      {/* login button */}
      <div className="flex flex-col gap-y-[10px] items-center">
        {/* <LoginButton
          provider="kakao"
          label="카카오로 계속하기"
          isCustomer={false}
        /> */}
        <LoginButton
          provider="naver"
          label="네이버로 계속하기"
          isCustomer={false}
        />
        <LoginButton
          provider="google"
          label="구글로 계속하기"
          isCustomer={false}
        />
      </div>

      {/* change to customer account */}
      <div
        className="btnFont text-center text-main-deep py-5"
        onClick={() => navigate("/c")}
      >
        구매자 계정으로 전환
      </div>
    </div>
  );
};

export default Home;
