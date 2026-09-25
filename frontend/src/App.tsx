import { Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout";
import HomePage from "./pages/Home";
import ExploreMap from "./pages/ExploreMap";
import PlaceDetailPage from "./pages/PlaceDetail";
import MakersPage from "./pages/Makers";
import MakerDetailPage from "./pages/MakerDetail";
import { ExperiencesPage, ExperienceDetailPage } from "./pages/Experiences";
import { FestivalsPage, FestivalDetailPage } from "./pages/Festivals";
import StaysPage from "./pages/Stays";
import AssistantPage from "./pages/Assistant";
import { ReportPage, MyReportsPage } from "./pages/Report";
import LoginPage from "./pages/Login";
import RegisterPage from "./pages/Register";
import AuthorityApp from "./authority/AuthorityApp";
import BusinessApp from "./business/BusinessApp";
import { useAuth } from "./state/auth";
import type { Role } from "./lib/types";

function Guard({ roles, children }: { roles: Role[]; children: React.ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="min-h-screen" />;
  if (!user || !roles.includes(user.role)) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/places/:id" element={<PlaceDetailPage />} />
        <Route path="/artisans" element={<MakersPage />} />
        <Route path="/artisans/:id" element={<MakerDetailPage />} />
        <Route path="/experiences" element={<ExperiencesPage />} />
        <Route path="/experiences/:id" element={<ExperienceDetailPage />} />
        <Route path="/festivals" element={<FestivalsPage />} />
        <Route path="/festivals/:id" element={<FestivalDetailPage />} />
        <Route path="/stays" element={<StaysPage />} />
        <Route path="/guide" element={<AssistantPage />} />
        <Route path="/report" element={<ReportPage />} />
        <Route path="/my-reports" element={<MyReportsPage />} />
      </Route>

      <Route path="/map" element={<ExploreMap />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      <Route
        path="/authority/*"
        element={
          <Guard roles={["authority_officer", "authority_admin"]}>
            <AuthorityApp />
          </Guard>
        }
      />
      <Route
        path="/business/*"
        element={
          <Guard roles={["artisan", "business", "authority_admin", "authority_officer"]}>
            <BusinessApp />
          </Guard>
        }
      />

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}