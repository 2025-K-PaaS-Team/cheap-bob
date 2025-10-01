// import Wrapper from "./Wrapper";
import {
  Wrapper,
  Main,
  Footer,
  Header,
  SellerFooter,
} from "@components/layouts";
import { pathToLayoutKey, pathToSellerLayoutKey } from "@utils";
import { Outlet, useLocation } from "react-router";
import SellerHeader from "./SellerHeader";

const Layout = () => {
  const location = useLocation();
  const path = location.pathname.toLowerCase();
  const isCustomer = path.startsWith("/c");
  const notFooter =
    path === "/c" ||
    path === "/c/signup" ||
    path.startsWith("/s/change") ||
    path === "/s" ||
    path.startsWith("/s/signup");
  const notHeader = path === "/c" || path.startsWith("/s/signup");

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
