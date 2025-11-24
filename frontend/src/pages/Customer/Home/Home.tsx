import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { HomeSwiper } from "@components/common/home";
import { Pagination } from "swiper/modules";
import { Swiper, SwiperSlide } from "swiper/react";
import "swiper/css";
import "swiper/css/navigation";
import "swiper/css/pagination";
import { homeSwiperMap } from "@constant";
import { GetUserRole } from "@services/common/auth";
import type { UserRoleType } from "@interface";
import { LoginInfo } from "@components/customer/home";

const Home = () => {
  const navigate = useNavigate();
  const [, setUserInfo] = useState<UserRoleType | null>(null);

  useEffect(() => {
    const init = async () => {
      const res = await GetUserRole();
      setUserInfo(res);
      if (
        res.email &&
        res.user_type == "customer" &&
        res.status === "complete" &&
        res.is_active
      )
        navigate("/c/stores");
    };

    init();
  }, [navigate]);

  return (
    <div className="flex flex-col flex-1 justify-center w-full py-[50px] gap-y-[15px]">
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

      <LoginInfo />
    </div>
  );
};

export default Home;
