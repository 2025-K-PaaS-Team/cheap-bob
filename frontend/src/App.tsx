import { Navigate, Route, Routes } from "react-router";
import { Layout } from "@components/layouts";
import {
  My,
  StoreDetail,
  StoreList,
  LoginCallback,
  CustomerLab,
  QrLab,
  Order,
  OrderManage,
  Signup,
  CustomerHome,
  SellerHome,
  Location,
  Favorite,
  Noti,
  Dashboard,
  SellerSignup,
  LoginFail,
  RoleCheck,
  Withdraw,
  WithdrawCancel,
  StoreSearch,
  OrderAll,
  StoreDesc,
  Privacy,
  TermsOfService,
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
import { BillingChange, BillingHistory, BillingInfo } from "@pages/Seller";
import StorePayment from "@pages/Customer/StorePayment";
import {
  ChangeCustomerAllergy,
  ChangeCustomerInfo,
  ChangeCustomerMenu,
  ChangeCustomerNutrition,
  ChangeCustomerTopping,
} from "@pages/Customer";

const App = () => {
  return (
    <Routes>
      {/* login callback */}
      <Route path="/auth/success" element={<LoginCallback />} />
      {/* login 409 failed */}
      <Route path="/auth/fail" element={<LoginFail />} />
      {/* role path */}
      <Route path="/auth/role-check" element={<RoleCheck />} />
      {/* withdraw */}
      <Route path="/withdraw" element={<Withdraw />} />
      {/* roleback withdraw */}
      <Route path="/withdraw/cancel" element={<WithdrawCancel />} />
      {/* tos */}
      <Route path="/docs/tos" element={<TermsOfService />} />
      {/* privacy policy */}
      <Route path="/docs/privacy" element={<Privacy />} />

      {/* customer side */}
      <Route path="/c" element={<Layout />}>
        {/* home */}
        <Route index element={<CustomerHome />} />
        {/* signup */}
        <Route path="signup" element={<Signup />} />
        {/* store */}
        <Route path="stores" element={<StoreList />} />
        <Route path="stores/:storeId" element={<StoreDetail />} />
        <Route path="stores/:storeId/desc" element={<StoreDesc />} />
        <Route path="stores/:storeId/payment" element={<StorePayment />} />
        {/* store search */}
        <Route path="stores/search" element={<StoreSearch />} />
        {/* location */}
        <Route path="location" element={<Location />} />
        {/* favorite */}
        <Route path="favorite" element={<Favorite />} />
        {/* noti */}
        <Route path="noti" element={<Noti />} />
        {/* order */}
        <Route path="order" element={<Order />} />
        <Route path="order/all" element={<OrderAll />} />
        {/* mypage */}
        <Route path="my" element={<My />} />
        {/* change customer info */}
        <Route path="change/info" element={<ChangeCustomerInfo />} />
        <Route path="change/menu" element={<ChangeCustomerMenu />} />
        <Route path="change/topping" element={<ChangeCustomerTopping />} />
        <Route path="change/allergy" element={<ChangeCustomerAllergy />} />
        <Route path="change/nutrition" element={<ChangeCustomerNutrition />} />
        {/* lab */}
        <Route path="lab" element={<CustomerLab />} />
        <Route path="qr" element={<QrLab />} />
        {/* customer fallback */}
        <Route path="*" element={<Navigate to="/c" replace />} />
      </Route>

      {/* seller side */}
      <Route path="/s" element={<Layout />}>
        {/* home */}
        <Route index element={<SellerHome />} />
        {/* signup */}
        <Route path="signup" element={<SellerSignup />} />
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
        <Route path="change/package/num" element={<ChangePackageNum />} />

        {/* billing management */}
        <Route path="billing" element={<BillingInfo />} />
        <Route path="billing/history" element={<BillingHistory />} />
        <Route path="billing/change" element={<BillingChange />} />

        {/* seller fallback */}
        <Route path="*" element={<Navigate to="/s" replace />} />
      </Route>

      {/* global fallback */}
      <Route path="*" element={<Navigate to="/c" replace />} />
    </Routes>
  );
};

export default App;
