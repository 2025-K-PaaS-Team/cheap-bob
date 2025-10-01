import { HomeSwiper, LoginButton } from "@components/common/home";
import { homeSwiperMap } from "@constant";
import { useEffect } from "react";
import { useNavigate } from "react-router";
import "swiper/css";
import "swiper/css/navigation";
import "swiper/css/pagination";
import { Pagination } from "swiper/modules";
import { Swiper, SwiperSlide } from "swiper/react";

const Home = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("accessToken");

    if (token) {
      navigate("/s/dashboard");
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
            <HomeSwiper title={slide.title} img={slide.img} />
          </SwiperSlide>
        ))}
      </Swiper>

      {/* login button */}
      <div className="fixed bottom-[38px] flex flex-col gap-y-[10px]">
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
