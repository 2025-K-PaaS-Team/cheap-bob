import { Navigate, Route, Routes } from "react-router";
import { Layout } from "@components/layouts";
import { Home, My, StoreDetail, StoreList, Login, Lab, Map } from "@pages";

const App = () => {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Home />} />
        {/* login */}
        <Route path="/auth/success" element={<Login />} />
        {/* store */}
        <Route path="/store-list" element={<StoreList />} />
        <Route path="/store-detail" element={<StoreDetail />} />
        {/* mypage */}
        <Route path="/my" element={<My />} />
        {/* lab */}
        <Route path="/lab" element={<Lab />}>
          <Route path="map" element={<Map />} />
        </Route>
        {/* fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
};

export default App;
