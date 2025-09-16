import { SignupSwiper } from "@components/customer/signup";
import { AllergyList, MenuList, NutritionList, ToppingList } from "@constant";
import { SignupLab } from "@pages/Common";
import { CreateCustomerDetail } from "@services";
import { useRef, useState } from "react";
import { Pagination } from "swiper/modules";
import { Swiper, SwiperSlide } from "swiper/react";

const Signup = () => {
  const swiperRef = useRef<any>(null);
  const [nickname, setNickname] = useState<string>("");
  const [phone, setPhone] = useState<string>("");

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    try {
      const res = await CreateCustomerDetail({
        nickname,
        phone_number: phone,
      });

      console.log("회원정보 등록 성공", res);
    } catch (err: unknown) {
      console.error("회원정보 등록 실패", err);
    }
  };

  return (
    <div className="h-full">
      <Swiper
        pagination={{ type: "progressbar" }}
        navigation={false}
        modules={[Pagination]}
        className="mySwiper h-full"
        // allowTouchMove={false}
        onSwiper={(swiper) => (swiperRef.current = swiper)}
      >
        <SwiperSlide>
          <SignupSwiper
            title={`서비스 이용 약관에 \n동의해주세요.`}
            type="agree"
            onNext={() => swiperRef.current.slideNext()}
          />
        </SwiperSlide>
        <SwiperSlide>
          <SignupSwiper
            title={`어떻게 불러드릴까요?`}
            type="enter"
            placeholder="7자 이내로 닉네임을 입력하세요"
            onNext={() => swiperRef.current.slideNext()}
          />
        </SwiperSlide>
        <SwiperSlide>
          <SignupSwiper
            title={`전화번호를 입력해주세요`}
            type="enter"
            placeholder="번호를 입력하세요"
            onNext={() => swiperRef.current.slideNext()}
          />
        </SwiperSlide>
        <SwiperSlide>
          <SignupSwiper
            title={`영양 목표를\n선택해주세요`}
            data={NutritionList}
            type="select"
            selectType="nutrition"
            subTitle="내 목표 맞춤형 식사를 추천해드려요."
            onNext={() => swiperRef.current.slideNext()}
          />
        </SwiperSlide>
        <SwiperSlide>
          <SignupSwiper
            title={`선호하는 메뉴를\n선택해주세요`}
            data={MenuList}
            type="select"
            selectType="menu"
            onNext={() => swiperRef.current.slideNext()}
          />
        </SwiperSlide>
        <SwiperSlide>
          <SignupSwiper
            title={`선호하는 토핑을\n선택해주세요`}
            data={ToppingList}
            type="select"
            selectType="topping"
            onNext={() => swiperRef.current.slideNext()}
          />
        </SwiperSlide>
        <SwiperSlide>
          <SignupSwiper
            title={`못 먹는 음식을\n선택해주세요`}
            data={AllergyList}
            type="select"
            selectType="allergy"
            onNext={() => swiperRef.current.slideNext()}
          />
        </SwiperSlide>
      </Swiper>

      {/* <form onSubmit={handleSubmit} className="p-3 gap-y-3 flex flex-col w-50">
        <input
          placeholder="어떻게 불러드릴까요"
          value={nickname}
          onChange={(e) => setNickname(e.target.value)}
          className="border-2 border-blue-500"
        />
        <input
          placeholder="번호"
          type="tel"
          value={phone}
          onChange={(e) => setPhone(e.target.value)}
          className="border-2 border-blue-500"
        />
        <button type="submit" className="bg-blue-300">
          제출하기
        </button>
      </form>

      <SignupLab /> */}
    </div>
  );
};

export default Signup;
