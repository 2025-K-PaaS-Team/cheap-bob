import CommonAgree from "@components/customer/signup/Agree";

const Agree = () => {
  return (
    <div className="mx-[20px]">
      <div className="font-bold text-2xl pt-[42px]">
        서비스 이용 약관에 <br />
        동의해주세요
      </div>
      <CommonAgree />
    </div>
  );
};

export default Agree;
