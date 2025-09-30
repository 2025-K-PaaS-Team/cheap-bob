// import Wrapper from "./Wrapper";
import {
  Wrapper,
  Main,
  Footer,
  Header,
  SellerFooter,
} from "@components/layouts";
import { pathToLayoutKey } from "@utils";
import { Outlet, useLocation } from "react-router";
import SellerHeader from "./SellerHeader";

const Layout = () => {
  const location = useLocation();
  const path = location.pathname;
  const isCustomer = path.startsWith("/c");
  const notFooter = path === "/c" || path === "/c/signup";
  const notHeader = path === "/c";

  return (
    <>
      <Wrapper>
        {!notHeader &&
          (isCustomer ? (
            <Header layout={pathToLayoutKey(path)} />
          ) : (
            <SellerHeader layout={pathToLayoutKey(path)} />
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
