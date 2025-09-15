// import Wrapper from "./Wrapper";
import {
  Wrapper,
  Main,
  Footer,
  Header,
  SellerFooter,
} from "@components/layouts";
import { Outlet, useLocation } from "react-router";

const Layout = () => {
  const location = useLocation();
  const path = location.pathname;
  const isCustomer = path.startsWith("c");
  const notFooter = path === "/c";
  const notHeader = path === "/c";

  return (
    <>
      <Wrapper>
        {!notHeader && <Header />}
        <Main>
          <Outlet />
        </Main>
        {!notFooter && (isCustomer ? <Footer /> : <SellerFooter />)}
      </Wrapper>
    </>
  );
};

export default Layout;
