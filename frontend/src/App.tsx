import { Navigate, Route, Routes } from "react-router";
import Home from "@pages/Home";
import { Layout } from "@components/layouts";
import { Google, Kakao, Naver, LoginSuccess } from "@pages/Login";
import { StoreList } from "@pages/StoreList";
import { StoreDetail } from "@pages/StoreDetail";

const App = () => {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Home />} />
        {/* login */}
        <Route path="/auth/success" element={<LoginSuccess />} />
        <Route path="/login-kakao" element={<Kakao />} />
        <Route path="/login-naver" element={<Naver />} />
        <Route path="/login-google" element={<Google />} />
        {/* store */}
        <Route path="/store-list" element={<StoreList />} />
        <Route path="/store-detail" element={<StoreDetail />} />
        {/* fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
};

export default App;
