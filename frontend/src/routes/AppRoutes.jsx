import { Routes, Route } from 'react-router-dom';
import MainLayout from '../layouts/MainLayout';
import LandingPage from '../pages/LandingPage';
import UploadResumePage from '../pages/UploadResumePage';
import LoadingPage from '../pages/LoadingPage';
import ResultsDashboard from '../pages/ResultsDashboard';
import RecruiterDashboard from '../pages/RecruiterDashboard';
import PostJobPage from '../pages/PostJobPage';
import ViewCandidatesPage from '../pages/ViewCandidatesPage';
import RecruiterProfilePage from '../pages/RecruiterProfilePage';
import JobsPage from '../pages/JobsPage';
import JobDetailsPage from '../pages/JobDetailsPage';
import ApplyJobPage from '../pages/ApplyJobPage';
import MyApplicationsPage from '../pages/MyApplicationsPage';
import ApplicantProfilePage from '../pages/ApplicantProfilePage';
import SignUpPage from '../pages/SignUpPage';
import SignInPage from '../pages/SignInPage';
import NotFound from '../pages/NotFound';
import { RoleRoute, GuestRoute, AuthRedirect } from './RoleRoute';
import { ROLES } from '../utils/roles';

function AppRoutes() {
  return (
    <Routes>
      <Route element={<AuthRedirect />}>
        <Route index element={<LandingPage />} />
      </Route>

      <Route path="signup" element={<SignUpPage />} />
      <Route path="signin" element={<SignInPage />} />

      <Route element={<GuestRoute />}>
        <Route path="upload" element={<UploadResumePage />} />
        <Route path="loading" element={<LoadingPage />} />
        <Route path="results" element={<ResultsDashboard />} />
      </Route>

      <Route element={<RoleRoute allowedRoles={[ROLES.RECRUITER]} />}>
        <Route element={<MainLayout />}>
          <Route path="recruiter" element={<RecruiterDashboard />} />
          <Route path="recruiter/post-job" element={<PostJobPage />} />
          <Route path="recruiter/candidates" element={<ViewCandidatesPage />} />
          <Route path="recruiter/profile" element={<RecruiterProfilePage />} />
        </Route>
      </Route>

      <Route element={<RoleRoute allowedRoles={[ROLES.APPLICANT]} />}>
        <Route element={<MainLayout />}>
          <Route path="jobs" element={<JobsPage />} />
          <Route path="jobs/:jobId" element={<JobDetailsPage />} />
          <Route path="jobs/:jobId/apply" element={<ApplyJobPage />} />
          <Route path="applications" element={<MyApplicationsPage />} />
          <Route path="profile" element={<ApplicantProfilePage />} />
        </Route>
      </Route>

      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}

export default AppRoutes;
