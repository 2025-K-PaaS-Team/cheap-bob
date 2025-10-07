import { LoginButton, HomeSwiper } from "@components/common/home";
import { useEffect } from "react";
import { useNavigate } from "react-router";
import { Pagination } from "swiper/modules";
import { Swiper, SwiperSlide } from "swiper/react";
import "swiper/css";
import "swiper/css/navigation";
import "swiper/css/pagination";
import { homeSwiperMap } from "@constant";

const Home = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("accessToken");

    if (token) {
      navigate("stores");
    }
  }, []);

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
      <div className="flex flex-col gap-y-[10px] items-center">
        <LoginButton provider="kakao" label="카카오로 계속하기" />
        <LoginButton provider="naver" label="네이버로 계속하기" />
        <LoginButton provider="google" label="구글로 계속하기" />
      </div>
    </div>
  );
};

export default Home;
