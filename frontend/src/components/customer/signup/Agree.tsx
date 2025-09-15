const Agree = () => {
  return (
    <div className="absolute bottom-[145px]">
      <div className="flex flex-col gap-y-[28px]">
        {/* 서비스 동의 */}
        <div className="flex flex-row gap-x-[10px]">
          <input type="checkbox" />
          <div className="font-base">(필수) 서비스 이용약관 동의</div>
          <div className="underline text-[#6C6C6C] fixed right-[20px]">
            보기
          </div>
        </div>
        {/* 개인정보 동의 */}
        <div className="flex flex-row gap-x-[10px]">
          <input type="checkbox" />
          <div className="font-base">(필수) 개인정보 수집 이용 동의</div>
          <div className="underline text-[#6C6C6C] fixed right-[20px]">
            보기
          </div>
        </div>
        {/* 모두 동의 */}
        <div className="flex flex-row gap-x-[10px] mt-[53px]">
          <input type="checkbox" />
          <div className="font-bold">모두 동의합니다.</div>
        </div>
      </div>
    </div>
  );
};

export default Agree;
