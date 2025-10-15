import { HomeSwiper, LoginButton } from "@components/common/home";
import { homeSwiperMap } from "@constant";
import "swiper/css";
import "swiper/css/navigation";
import "swiper/css/pagination";
import { Pagination } from "swiper/modules";
import { Swiper, SwiperSlide } from "swiper/react";

const Home = () => {
  localStorage.clear();

  return (
    <div className="flex flex-col justify-around w-full min-h-screen py-[30px]">
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
      <div className="space-y-2 p-4">
        <div className="font-bold bg-[#d9d9d9] rounded-lg">
          hello (bold 700)
        </div>
        <div className="font-normal bg-main-500">bye (normal 400)</div>
        <div className="font-extrabold">extrabold 800</div>
        <div className="font-black">black 900</div>
      </div>

      <div className="flex flex-col gap-y-[10px] items-center">
        <LoginButton
          provider="kakao"
          label="카카오로 계속하기"
          isCustomer={false}
        />
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
    </div>
  );
};

export default Home;
