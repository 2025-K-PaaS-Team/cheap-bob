import { useNavigate } from "react-router";

const Home = () => {
  const navigate = useNavigate();

  const handleClick = (link: string) => navigate(link);

  return (
    <div className="flex justify-center">
      {/* title */}
      <h1 className="flex">저렴한끼</h1>
      {/* login */}
      <div className="fixed bottom-30 w-full flex flex-col max-w-[400px]">
        <h3
          className="bg-yellow-500 p-3 rounded-xl"
          onClick={() => handleClick("/kakao")}
        >
          카카오톡으로 로그인하기
        </h3>
        <h3
          className="bg-green-500 p-3 rounded-xl"
          onClick={() => handleClick("/naver")}
        >
          네이버로 로그인하기
        </h3>
        <h3
          className="bg-blue-300 p-3 rounded-xl"
          onClick={() => handleClick("google")}
        >
          구글로 로그인하기
        </h3>
      </div>
    </div>
  );
};

export default Home;
