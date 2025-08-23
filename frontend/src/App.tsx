import { Route, Routes } from "react-router";
import Home from "@pages/Home";
import { Layout } from "@components/layouts";
import { Google, Kakao, Naver } from "@pages/Login";
import { StoreList } from "@pages/StoreList";
import { StoreDetail } from "@pages/StoreDetail";

const App = () => {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Home />} />
        {/* login */}
        <Route path="/login-kakao" element={<Kakao />} />
        <Route path="/login-naver" element={<Naver />} />
        <Route path="/login-google" element={<Google />} />
        {/* store */}
        <Route path="/store-list" element={<StoreList />} />
        <Route path="/store-detail" element={<StoreDetail />} />
      </Route>
    </Routes>
  );
};

export default App;
