import { Navigate, Route, Routes, useLocation } from "react-router";

import { useAuth } from "./auth/AuthContext";
import { Shell } from "./components/Shell";
import { DashboardPage } from "./pages/DashboardPage";
import { ForecastingPage } from "./pages/ForecastingPage";
import { IotPage } from "./pages/IotPage";
import { LoginPage } from "./pages/LoginPage";
import { LogisticsPage } from "./pages/LogisticsPage";
import { PatternsPage } from "./pages/PatternsPage";
import { ProductsPage } from "./pages/ProductsPage";
import { TrackingPage } from "./pages/TrackingPage";

function RequireSession() {
  const { user } = useAuth();
  const location = useLocation();
  if (!user) return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  return <Shell />;
}

export function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<RequireSession />}>
        <Route index element={<DashboardPage />} />
        <Route path="productos" element={<ProductsPage />} />
        <Route path="seguimiento" element={<TrackingPage />} />
        <Route path="logistica" element={<LogisticsPage />} />
        <Route path="pronosticos" element={<ForecastingPage />} />
        <Route path="iot" element={<IotPage />} />
        <Route path="patrones" element={<PatternsPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
