// import Wrapper from "./Wrapper";
import {
  Wrapper,
  Main,
  Footer,
  Header,
  SellerFooter,
} from "@components/layouts";
import { pathToLayoutKey, pathToSellerLayoutKey } from "@utils";
import SellerHeader from "./SellerHeader";
import { useRef } from "react";
import { useLocation, Outlet, Navigate } from "react-router";

const Layout = () => {
  const swiperRef = useRef<any>(null);
  const location = useLocation();
  const path = location.pathname.toLowerCase();
  const isCustomer = path.startsWith("/c");
  const isAuth = path.startsWith("/auth");

  const token = localStorage.getItem("accessToken");
  const role = localStorage.getItem("loginRole");

  const resolveRedirect = (): string | null => {
    if (isAuth) return null;

    if (!token) {
      return path.startsWith("/s") ? "/s" : "/c";
    }

    if (token && role) {
      if (path === "/c") return "/c/stores";
      if (path === "/s") return "/s/dashboard";

      if (role === "seller" && path.startsWith("/c")) return "/auth/role-check";
      if (role === "customer" && path.startsWith("/s"))
        return "/auth/role-check";
    }

    return null;
  };

  const dest = resolveRedirect();

  if (dest && dest !== path) {
    return <Navigate to={dest} replace />;
  }

  const notFooter =
    path === "/c" ||
    path === "/c/signup" ||
    path.startsWith("/s/change") ||
    path === "/s" ||
    path.startsWith("/s/signup") ||
    path.startsWith("/s/billing/") ||
    path.startsWith("/docs") ||
    path.startsWith("/withdraw") ||
    path.startsWith("/auth");

  const notHeader =
    path === "/c" ||
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
            (isCustomer ? (
              <Header layout={pathToLayoutKey(path)} swiperRef={swiperRef} />
            ) : (
              <SellerHeader layout={pathToSellerLayoutKey(path)} />
            ))}
          <Main className="app-scroll">
            <Outlet context={{ swiperRef }} />
          </Main>
          {!notFooter && (isCustomer ? <Footer /> : <SellerFooter />)}
        </Wrapper>
      </div>
    </div>
  );
};

export default Layout;
