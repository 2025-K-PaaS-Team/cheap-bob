import { Navigate, Route, Routes } from "react-router";
import Home from "@pages/Home";
import { Layout } from "@components/layouts";
import { LoginSuccess } from "@pages/Login";
import { StoreList } from "@pages/StoreList";
import { StoreDetail } from "@pages/StoreDetail";
import { Map } from "@pages/Lab";

const App = () => {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Home />} />
        {/* login */}
        <Route path="/auth/success" element={<LoginSuccess />} />
        {/* store */}
        <Route path="/store-list" element={<StoreList />} />
        <Route path="/store-detail" element={<StoreDetail />} />
        {/* lab */}
        <Route path="/lab/map" element={<Map />} />
        {/* fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
};

export default App;
