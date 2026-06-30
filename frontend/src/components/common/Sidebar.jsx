import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  Briefcase,
  Users,
  User,
  FileText,
  LogOut,
  X,
} from 'lucide-react';
import { getSession, signOut } from '../../services/auth';
import { getNavLinksForRole } from '../../config/navigation';
import { ROLES } from '../../utils/roles';

const iconMap = {
  Dashboard: LayoutDashboard,
  'Post Job': Briefcase,
  'View Candidates': Users,
  Profile: User,
  'Available Jobs': Briefcase,
  'My Applications': FileText,
  'My Profile': User,
};

function Sidebar({ isOpen, onClose }) {
  const navigate = useNavigate();
  const session = getSession();
  const sidebarLinks = getNavLinksForRole(session?.role);

  const handleLogout = () => {
    signOut();
    onClose();
    navigate('/signin');
  };

  return (
    <>
      {isOpen && (
        <button
          type="button"
          className="fixed inset-0 z-40 bg-slate-900/40 lg:hidden"
          onClick={onClose}
          aria-label="Close sidebar overlay"
        />
      )}

      <aside
        className={`fixed inset-y-0 left-0 z-50 w-64 transform border-r border-slate-200 bg-white pt-16 transition-transform duration-200 dark:border-white/[0.06] dark:bg-[#0c0c0e] lg:static lg:z-0 lg:translate-x-0 lg:pt-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3 lg:hidden">
          <span className="text-sm font-semibold text-slate-700">
            {session?.role === ROLES.RECRUITER ? 'Recruiter' : 'Applicant'}
          </span>
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-1.5 text-slate-500 hover:bg-slate-100"
            aria-label="Close sidebar"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        <nav className="flex flex-col gap-1 p-4">
          {sidebarLinks.map(({ to, label, end }) => {
            const Icon = iconMap[label] || User;
            return (
              <NavLink
                key={to}
                to={to}
                end={end}
                onClick={onClose}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-brand-50 text-brand-700'
                      : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                  }`
                }
              >
                <Icon className="h-4 w-4 shrink-0" />
                {label}
              </NavLink>
            );
          })}

          <button
            type="button"
            onClick={handleLogout}
            className="mt-2 flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-100 hover:text-slate-900"
          >
            <LogOut className="h-4 w-4 shrink-0" />
            Logout
          </button>
        </nav>
      </aside>
    </>
  );
}

export default Sidebar;
