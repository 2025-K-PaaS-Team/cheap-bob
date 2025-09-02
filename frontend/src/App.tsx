import { Navigate, Route, Routes } from "react-router";
import { Layout } from "@components/layouts";
import {
  My,
  StoreDetail,
  StoreList,
  LoginCallback,
  CustomerLab,
  Map,
  SellerLab,
  PortOneLab,
} from "@pages";
import { CustomerHome, SellerHome } from "@pages/Home";

const App = () => {
  return (
    <Routes>
      {/* login callback */}
      <Route path="/auth/success" element={<LoginCallback />} />

      {/* customer side */}
      <Route path="/c" element={<Layout />}>
        {/* home */}
        <Route index element={<CustomerHome />} />
        {/* store */}
        <Route path="store-list" element={<StoreList />} />
        <Route path="store-detail" element={<StoreDetail />} />
        {/* mypage */}
        <Route path="my" element={<My />} />
        {/* lab */}
        <Route path="lab" element={<CustomerLab />} />
        <Route path="lab-portone" element={<PortOneLab />} />
        <Route path="lab-map" element={<Map />} />
      </Route>

      {/* seller side */}
      <Route path="/s" element={<Layout />}>
        {/* home */}
        <Route index element={<SellerHome />} />
        <Route path="lab" element={<SellerLab />} />
      </Route>

      {/* 루트 접근시 고객 홈으로 */}
      <Route path="/" element={<Navigate to="/c" replace />} />
      {/* fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

export default App;
