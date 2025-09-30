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
import {
  ChangeOperationInfo,
  ChangeOperationTime,
  ChangePackageDesc,
  ChangePackageInfo,
  ChangePackageName,
  ChangePackageNum,
  ChangePackageNutrition,
  ChangePackagePrice,
  ChangePickupTime,
  ChangeStoreAddr,
  ChangeStoreDesc,
  ChangeStoreImg,
  ChangeStoreInfo,
  ChangeStoreName,
  ChangeStoreNum,
} from "@pages/Seller/Dashboard";

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
        {/* dashboard = store management */}
        <Route path="dashboard" element={<Dashboard />}></Route>
        {/* order management */}
        <Route path="order" element={<OrderManage />} />
        {/* change store info */}
        <Route path="change/store" element={<ChangeStoreInfo />} />
        <Route path="change/store/name" element={<ChangeStoreName />} />
        <Route path="change/store/desc" element={<ChangeStoreDesc />} />
        <Route path="change/store/num" element={<ChangeStoreNum />} />
        <Route path="change/store/addr" element={<ChangeStoreAddr />} />
        <Route path="change/store/img" element={<ChangeStoreImg />} />
        {/* change operation info */}
        <Route path="change/operation" element={<ChangeOperationInfo />} />
        <Route
          path="change/operation/op-time"
          element={<ChangeOperationTime />}
        />
        <Route path="change/operation/pu-time" element={<ChangePickupTime />} />
        {/* change package info */}
        <Route path="change/package" element={<ChangePackageInfo />} />
        <Route path="change/package/name" element={<ChangePackageName />} />
        <Route path="change/package/desc" element={<ChangePackageDesc />} />
        <Route
          path="change/package/nutrition"
          element={<ChangePackageNutrition />}
        />
        <Route path="change/package/price" element={<ChangePackagePrice />} />
        <Route path="change/package/quantity" element={<ChangePackageNum />} />

        {/* store page -- need to delete after refactoring */}
        <Route path="store" element={<Store />} />
        {/* lab */}
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
