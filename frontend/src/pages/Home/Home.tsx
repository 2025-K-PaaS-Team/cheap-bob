import { LoginButton } from "@components/home";

const Home = () => {
  return (
    <div className="flex justify-center">
      {/* title */}
      <h1 className="flex">저렴한끼</h1>
      {/* login */}
      <div className="fixed bottom-30 w-full flex flex-col max-w-[400px]">
        <LoginButton
          provider="kakao"
          label="카카오톡으로 로그인하기"
          color="bg-yellow-500"
        />
        <LoginButton
          provider="naver"
          label="네이버로 로그인하기"
          color="bg-green-500"
        />
        <LoginButton
          provider="google"
          label="구글로 로그인하기"
          color="bg-blue-300"
        />
      </div>
    </div>
  );
};

export default Home;
