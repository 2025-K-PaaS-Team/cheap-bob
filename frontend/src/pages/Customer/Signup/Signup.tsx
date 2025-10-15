import { CommonModal } from "@components/common";
import { SignupSwiper } from "@components/customer/signup";
import { AllergyList, MenuList, NutritionList, ToppingList } from "@constant";
import { CreateCustomerRegister } from "@services";
import { formatErrMsg } from "@utils";
import { useRef, useState } from "react";
import { Pagination } from "swiper/modules";
import { Swiper, SwiperSlide } from "swiper/react";

const Signup = () => {
  const swiperRef = useRef<any>(null);
  const [nickname, setNickname] = useState<string>("");
  const [phone, setPhone] = useState<string>("");
  const [nutrition, setNutrition] = useState<string[]>([]);
  const [menu, setMenu] = useState<string[]>([]);
  const [topping, setTopping] = useState<string[]>([]);
  const [allergy, setAllergy] = useState<string[]>([]);
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState<string>("");

  const handleNext = async () => {
    const swiper = swiperRef.current;

    if (!swiper) return;

    if (swiper.isEnd) {
      try {
        await CreateCustomerRegister({
          nickname,
          phone_number: phone,
          nutrition_types: nutrition,
          preferred_menus: menu,
          allergies: allergy,
          topping_types: topping,
        });
      } catch (err: unknown) {
        setModalMsg(formatErrMsg(err));
        setShowModal(true);
      }
    } else {
      swiper.slideNext();
    }
  };

  return (
    <div className="h-full">
      <Swiper
        pagination={{ type: "progressbar" }}
        navigation={false}
        modules={[Pagination]}
        className="mySwiper h-full"
        allowTouchMove={false}
        onSwiper={(swiper) => (swiperRef.current = swiper)}
      >
        <SwiperSlide>
          <SignupSwiper
            title={`서비스 이용 약관에 \n동의해주세요.`}
            type="agree"
            onNext={handleNext}
          />
        </SwiperSlide>
        <SwiperSlide>
          <SignupSwiper
            title={`어떻게 불러드릴까요?`}
            type="enter"
            placeholder="7자 이내로 닉네임을 입력하세요"
            validate={(val) =>
              val.length > 7 || val.length < 1
                ? "7자 이내로 닉네임을 입력해주세요"
                : ""
            }
            onNext={handleNext}
            value={nickname}
            setValue={setNickname}
          />
        </SwiperSlide>
        <SwiperSlide>
          <SignupSwiper
            title={`전화번호를 입력해주세요`}
            type="enter"
            placeholder="번호를 입력하세요"
            validate={(val) =>
              !/^\d{10,11}$/.test(val) ? "01011112222형식으로 입력해주세요" : ""
            }
            onNext={handleNext}
            value={phone}
            setValue={setPhone}
          />
        </SwiperSlide>
        <SwiperSlide>
          <SignupSwiper
            title={`영양 목표를\n선택해주세요`}
            data={NutritionList}
            type="select"
            selectType="nutrition"
            subTitle="내 목표 맞춤형 식사를 추천해드려요."
            onNext={handleNext}
            selected={nutrition}
            setSelected={setNutrition}
            validate={(selected) =>
              selected.length === 0
                ? "최소 1개 이상 선택해주세요"
                : selected.length > 3
                ? "최대 3개까지만 선택할 수 있습니다"
                : null
            }
          />
        </SwiperSlide>
        <SwiperSlide>
          <SignupSwiper
            title={`선호하는 메뉴를\n선택해주세요`}
            data={MenuList}
            type="select"
            selectType="menu"
            onNext={handleNext}
            selected={menu}
            setSelected={setMenu}
          />
        </SwiperSlide>
        <SwiperSlide>
          <SignupSwiper
            title={`선호하는 토핑을\n선택해주세요`}
            data={ToppingList}
            type="select"
            selectType="topping"
            onNext={handleNext}
            selected={topping}
            setSelected={setTopping}
          />
        </SwiperSlide>
        <SwiperSlide>
          <SignupSwiper
            title={`못 먹는 음식을\n선택해주세요`}
            data={AllergyList}
            type="select"
            selectType="allergy"
            onNext={handleNext}
            selected={allergy}
            setSelected={setAllergy}
          />
        </SwiperSlide>
      </Swiper>

      {showModal && (
        <CommonModal
          desc={modalMsg}
          confirmLabel="확인"
          onConfirmClick={() => setShowModal(false)}
          category="green"
        />
      )}
    </div>
  );
};

export default Signup;
