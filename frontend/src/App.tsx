import { Route, Routes } from "react-router";
import Home from "@pages/Home";
import { Layout } from "@components/layouts";
import { Google, Kakao, Naver } from "@pages/Login";

const App = () => {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="/kakao" element={<Kakao />} />
        <Route path="/naver" element={<Naver />} />
        <Route path="/google" element={<Google />} />
      </Route>
    </Routes>
  );
};

export default App;
