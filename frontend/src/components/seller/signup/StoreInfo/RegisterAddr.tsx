import { PostalCode } from "@components/seller/dashboard";

const RegisterAddr = () => {
  return (
    <div className="mx-[20px] mt-[69px] flex flex-col gap-y-[11px]">
      <div className="text-[16px]">3/4</div>
      <div className="text-[24px]">
        <span className="font-bold">매장 위치</span>를 알려주세요.
      </div>
      {/* postal code */}
      <PostalCode />
    </div>
  );
};

export default RegisterAddr;
