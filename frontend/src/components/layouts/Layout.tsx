// import Wrapper from "./Wrapper";
import {
  Wrapper,
  Main,
  Footer,
  Header,
  SellerFooter,
} from "@components/layouts";
import { pathToLayoutKey, pathToSellerLayoutKey } from "@utils";
import { Outlet, useLocation, useNavigate } from "react-router";
import SellerHeader from "./SellerHeader";
import { useEffect } from "react";

const Layout = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const path = location.pathname.toLowerCase();
  const isCustomer = path.startsWith("/c");
  const notFooter =
    path === "/c" ||
    path === "/c/signup" ||
    path.startsWith("/s/change") ||
    path === "/s" ||
    path.startsWith("/s/signup") ||
    path.startsWith("/s/billing/");
  const notHeader =
    path === "/c" ||
    path === "/s" ||
    path.startsWith("/s/signup") ||
    path === "/s/order";

  useEffect(() => {
    const token = localStorage.getItem("accessToken");
    const role = localStorage.getItem("loginRole");

    if (role === "seller" && path.startsWith("/c")) {
      navigate("/auth/role-check", { replace: true });
      return;
    }

    if (role === "customer" && path.startsWith("/s")) {
      navigate("/auth/role-check", { replace: true });
      return;
    }

    if (!token) {
      if (role === "customer") {
        navigate("/c", { replace: true });
        return;
      }

      if (role === "seller") {
        navigate("/s", { replace: true });
        return;
      }

      if (!role) {
        navigate("/c", { replace: true });
        return;
      }
    }
  }, [location.pathname, navigate]);

  return (
    <>
      <Wrapper>
        {!notHeader &&
          (isCustomer ? (
            <Header layout={pathToLayoutKey(path)} />
          ) : (
            <SellerHeader layout={pathToSellerLayoutKey(path)} />
          ))}
        <Main>
          <Outlet />
        </Main>
        {!notFooter && (isCustomer ? <Footer /> : <SellerFooter />)}
      </Wrapper>
    </>
  );
};

export default Layout;
