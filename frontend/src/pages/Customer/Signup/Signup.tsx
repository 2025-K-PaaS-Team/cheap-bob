import { SignupLab } from "@pages/Common";
import { CreateCustomerDetail } from "@services";
import { useState } from "react";

const Signup = () => {
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
    <div>
      <form onSubmit={handleSubmit} className="p-3 gap-y-3 flex flex-col w-50">
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

      <SignupLab />
    </div>
  );
};

export default Signup;
