// import Wrapper from "./Wrapper";
import { Wrapper, Main, Footer, Header } from "@components/layouts";
import { Outlet } from "react-router";

const Layout = () => {
  return (
    <>
      <Wrapper>
        <Header />
        <Main>
          <Outlet />
        </Main>
        <Footer />
      </Wrapper>
    </>
  );
};

export default Layout;
