import { Routes, Route } from 'react-router-dom';
import MainLayout from '../layouts/MainLayout';
import LandingPage from '../pages/LandingPage';
import UploadResumePage from '../pages/UploadResumePage';
import LoadingPage from '../pages/LoadingPage';
import ResultsDashboard from '../pages/ResultsDashboard';
import RecruiterDashboard from '../pages/RecruiterDashboard';
import SignUpPage from '../pages/SignUpPage';
import SignInPage from '../pages/SignInPage';
import NotFound from '../pages/NotFound';

function AppRoutes() {
  return (
    <Routes>
      <Route index element={<LandingPage />} />
      <Route path="upload" element={<UploadResumePage />} />
      <Route path="loading" element={<LoadingPage />} />
      <Route path="recruiter" element={<RecruiterDashboard />} />
      <Route path="signup" element={<SignUpPage />} />
      <Route path="signin" element={<SignInPage />} />
      <Route element={<MainLayout />}>
          <Route path="results" element={<ResultsDashboard />} />
          <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  );
}

export default AppRoutes;
