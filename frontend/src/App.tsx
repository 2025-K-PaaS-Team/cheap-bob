import { Navigate, Route, Routes } from "react-router";
import { Layout } from "@components/layouts";
import {
  My,
  StoreDetail,
  StoreList,
  LoginCallback,
  CustomerLab,
  SellerLab,
  QrLab,
  Order,
  Store,
  OrderManage,
  Signup,
  CustomerMapLab,
  CustomerHome,
  SellerHome,
  Location,
  Favorite,
  Noti,
  Dashboard,
} from "@pages";
import { SellerMapLab } from "@pages/Common";

const App = () => {
  return (
    <Routes>
      {/* login callback */}
      <Route path="/auth/success" element={<LoginCallback />} />

      {/* customer side */}
      <Route path="/c" element={<Layout />}>
        {/* home */}
        <Route index element={<CustomerHome />} />
        {/* signup */}
        <Route path="signup" element={<Signup />} />
        {/* store */}
        <Route path="stores" element={<StoreList />} />
        <Route path="stores/:storeId" element={<StoreDetail />} />
        {/* location */}
        <Route path="location" element={<Location />} />
        {/* favorite */}
        <Route path="favorite" element={<Favorite />} />
        {/* noti */}
        <Route path="noti" element={<Noti />} />
        {/* order */}
        <Route path="order" element={<Order />} />
        {/* mypage */}
        <Route path="my" element={<My />} />
        {/* lab */}
        <Route path="lab" element={<CustomerLab />} />
        <Route path="lab/map" element={<CustomerMapLab />} />
        <Route path="qr" element={<QrLab />} />
      </Route>

      {/* seller side */}
      <Route path="/s" element={<Layout />}>
        {/* home */}
        <Route index element={<SellerHome />} />
        {/* dashboard */}
        <Route path="dashboard" element={<Dashboard />} />
        {/* order */}
        <Route path="order" element={<OrderManage />} />
        {/* store */}
        <Route path="store" element={<Store />} />
        {/* lab */}
        <Route path="lab" element={<SellerLab />} />
        <Route path="lab/map" element={<SellerMapLab />} />
      </Route>

      {/* 루트 접근시 고객 홈으로 */}
      <Route path="/" element={<Navigate to="/c" replace />} />
      {/* fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

export default App;
