import { LoginButton, SwiperBase } from "@components/common/home";
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
    <div className="flex justify-center w-full">
      {/* swiper */}
      <Swiper
        pagination={{ clickable: true }}
        modules={[Pagination]}
        className="mySwiper items-center flex h-[460px] mt-[119px]"
      >
        {homeSwiperMap.map((slide, idx) => (
          <SwiperSlide key={idx}>
            <SwiperBase title={slide.title} img={slide.img} />
          </SwiperSlide>
        ))}
      </Swiper>

      {/* login button */}
      <div className="fixed bottom-[38px] flex flex-col gap-y-[10px]">
        <LoginButton provider="kakao" label="카카오로 계속하기" />
        <LoginButton provider="naver" label="네이버로 계속하기" />
        <LoginButton provider="google" label="구글로 계속하기" />
      </div>
    </div>
  );
};

export default Home;
