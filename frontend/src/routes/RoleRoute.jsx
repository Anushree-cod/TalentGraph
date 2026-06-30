import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { getSession } from '../services/auth';
import { getDashboardPath } from '../utils/roles';

export function RoleRoute({ allowedRoles }) {
  const location = useLocation();
  const session = getSession();

  if (!session?.token) {
    return <Navigate to="/signin" state={{ from: location.pathname }} replace />;
  }

  if (!allowedRoles.includes(session.role)) {
    return <Navigate to={getDashboardPath(session.role)} replace />;
  }

  return <Outlet />;
}

export function GuestRoute() {
  const session = getSession();

  if (session?.token) {
    return <Navigate to={getDashboardPath(session.role)} replace />;
  }

  return <Outlet />;
}

export function AuthRedirect() {
  const session = getSession();

  if (session?.token) {
    return <Navigate to={getDashboardPath(session.role)} replace />;
  }

  return <Outlet />;
}
