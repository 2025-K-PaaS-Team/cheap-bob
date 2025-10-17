export { default as My } from "./Customer/My";
export { default as StoreDetail } from "./Customer/StoreDetail";
export { default as StoreList } from "./Customer/StoreList";
export { default as LoginCallback } from "./Common/LoginCallback";
export { default as LoginFail } from "./Common/LoginCallback/LoginFail";
export { default as RoleCheck } from "./Common/LoginCallback/RoleCheck";
export { default as Order } from "./Customer/Order";
export { default as Signup } from "./Customer/Signup";
export { default as CustomerHome } from "./Customer/Home";
export { default as Location } from "./Customer/Location";
export { default as Noti } from "./Customer/Noti";
export { default as Favorite } from "./Customer/Favorite";

// seller
export { default as OrderManage } from "./Seller/Order";
export { default as SellerHome } from "./Seller/Home";
export { default as Dashboard } from "./Seller/Dashboard";
export { default as SellerSignup } from "./Seller//Signup";
export * from "./Seller/Billing";

// lab
export { default as CustomerLab } from "./Common/Lab/CustomerLab";
export { default as PortOneLab } from "../components/Payment/Payment";
export { default as QrLab } from "./Common/Lab/QrLab";
export { default as Withdraw } from "./Common/Withdraw";
export { default as WithdrawCancel } from "./Common/Withdraw/WithdrawCancel";
