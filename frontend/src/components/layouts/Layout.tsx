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
  const isCustomer = path.includes("c");

  return (
    <>
      <Wrapper>
        <Header />
        <Main>
          <Outlet />
        </Main>
        {isCustomer ? <Footer /> : <SellerFooter />}
      </Wrapper>
    </>
  );
};

export default Layout;
