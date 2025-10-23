import {
  Wrapper,
  Main,
  Footer,
  Header,
  SellerFooter,
} from "@components/layouts";
import SellerHeader from "./SellerHeader";
import { useRef } from "react";
import { useLocation, Outlet, Navigate, matchPath } from "react-router-dom";

const Layout = () => {
  const swiperRef = useRef<any>(null);
  const location = useLocation();
  const path = location.pathname.toLowerCase();
  const isCustomer = path.startsWith("/c");

  const role = localStorage.getItem("loginRole");

  const isAuth = path.startsWith("/auth");
  const isWithdraw = path.startsWith("/withdraw");
  const isDocs = path.startsWith("/docs");
  const isHome = path === "/c" || path === "/s";

  const resolveRedirect = () => {
    if (isAuth || isWithdraw || isDocs || isHome) return null;

    if (role === "seller" && path.startsWith("/c")) return "/auth/role-check";
    if (role === "customer" && path.startsWith("/s")) return "/auth/role-check";
  };

  const dest = resolveRedirect();

  if (dest && dest !== path) {
    return <Navigate to={dest} replace />;
  }

  const notFooter =
    path === "/c" ||
    path === "/c/signup" ||
    path === "/c/location" ||
    path === "/c/favorite" ||
    path === "/c/noti" ||
    path.startsWith("/c/change") ||
    path.startsWith("/c/order/all") ||
    path.startsWith("/s/change") ||
    path === "/s" ||
    path.startsWith("/s/signup") ||
    path.startsWith("/s/billing/") ||
    path.startsWith("/docs") ||
    path.startsWith("/withdraw") ||
    path.startsWith("/auth");

  const notHeader =
    path === "/c" ||
    matchPath("/c/stores/:storeId", path) ||
    path === "/s" ||
    path.startsWith("/s/signup") ||
    path === "/s/order" ||
    path.startsWith("/docs") ||
    path.startsWith("/withdraw") ||
    path.startsWith("/auth");

  return (
    <div className="app-layout">
      <aside className="app-intro">
        <img src="/cheapbop.svg" alt="Logo" className="app-logo" />
        <h1 className="app-title">저렴한끼</h1>
        <div className="app-desc">
          건강한 식사, <br />
          저렴하게 해결하세요
        </div>
      </aside>

      <div className="app-frame">
        <Wrapper>
          {!notHeader &&
            (isCustomer ? <Header swiperRef={swiperRef} /> : <SellerHeader />)}
          <Main className="app-scroll">
            <Outlet context={{ swiperRef }} />
          </Main>
          {!notFooter && (isCustomer ? <Footer /> : <SellerFooter />)}
        </Wrapper>

        <div id="toast-root" className="absolute inset-0 pointer-events-none" />
      </div>
    </div>
  );
};

export default Layout;
