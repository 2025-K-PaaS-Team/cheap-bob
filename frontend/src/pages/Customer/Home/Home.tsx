import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { LoginButton, HomeSwiper } from "@components/common/home";
import { Pagination } from "swiper/modules";
import { Swiper, SwiperSlide } from "swiper/react";
import "swiper/css";
import "swiper/css/navigation";
import "swiper/css/pagination";
import { homeSwiperMap } from "@constant";
import { GetCustomerEmail } from "@services";

const Home = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const init = async () => {
      try {
        await GetCustomerEmail();
        navigate("/c/stores");
      } catch (err) {
        console.warn("Failed to get email:", err);
      }
    };

    init();
  }, []);

  return (
    <div className="flex flex-col flex-1 justify-around w-full py-[50px]">
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

      <div className="flex flex-col justify-end gap-y-[20px]">
        {/* login button */}
        <div className="flex flex-col gap-y-[10px] items-center">
          <LoginButton provider="naver" label="네이버로 계속하기" />
          <LoginButton provider="google" label="구글로 계속하기" />
        </div>

        <div className="flex flex-col gap-y-[10px] text-center">
          <div
            className="btnFont text-main-deep"
            onClick={() => {
              localStorage.removeItem("loginRole");
              navigate("/s");
            }}
          >
            가게를 운영하고 계신가요?
          </div>
          <div className="flex flex-row justify-center gap-x-[20px] text-[#9D9D9D] tagFont">
            <div onClick={() => navigate("/docs/tos")}>이용약관</div>
            <div onClick={() => navigate("/docs/privacy")}>
              개인정보처리방침
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
