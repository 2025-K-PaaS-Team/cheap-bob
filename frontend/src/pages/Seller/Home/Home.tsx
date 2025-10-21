import { HomeSwiper, LoginButton } from "@components/common/home";
import { homeSwiperMap } from "@constant";
import { useNavigate } from "react-router-dom";
import "swiper/css";
import "swiper/css/navigation";
import "swiper/css/pagination";
import { Pagination } from "swiper/modules";
import { Swiper, SwiperSlide } from "swiper/react";

const Home = () => {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col flex-1 justify-start w-full py-[50px]">
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

      <div className="flex flex-1 flex-col justify-end gap-y-[20px]">
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
        <div className="flex flex-col gap-y-[10px]">
          {/* change to customer account */}
          <div
            className="btnFont text-center text-sub-orange"
            onClick={() => navigate("/c")}
          >
            구매자 계정으로 전환
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
