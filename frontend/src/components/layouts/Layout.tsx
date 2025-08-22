// import Wrapper from "./Wrapper";
import { Wrapper, Main } from "@components/layouts";
import { Outlet } from "react-router";

const Layout = () => {
  return (
    <Wrapper>
      <Main>
        <Outlet />
      </Main>
      {/* <Footer /> */}
    </Wrapper>
  );
};

export default Layout;
