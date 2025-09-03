import { Navigate, Route, Routes } from "react-router";
import { Layout } from "@components/layouts";
import {
  My,
  StoreDetail,
  StoreList,
  LoginCallback,
  CustomerLab,
  SellerLab,
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
        <Route path="stores" element={<StoreList />} />
        <Route path="stores/:storeId" element={<StoreDetail />} />
        {/* mypage */}
        <Route path="my" element={<My />} />
        {/* lab */}
        <Route path="lab" element={<CustomerLab />} />
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
