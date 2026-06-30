import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { getSession, signOut } from '../services/auth';

function ApplicantProfilePage() {
  const navigate = useNavigate();
  const session = getSession();

  const handleLogout = () => {
    signOut();
    navigate('/signin');
  };

  return (
    <div className="page-container py-12">
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="mx-auto max-w-lg">
        <p className="tg-label-wide">Applicant</p>
        <h1 className="mt-2 text-3xl font-bold tg-heading">My profile</h1>

        <div className="tg-surface mt-8 space-y-4 p-6 sm:p-8">
          <div className="flex justify-between text-sm">
            <span className="tg-muted">Email</span>
            <span className="font-medium tg-heading">{session?.email || '—'}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="tg-muted">Role</span>
            <span className="font-medium tg-heading">Applicant</span>
          </div>
          <button type="button" onClick={handleLogout} className="tg-primary-btn mt-4 w-full">
            Logout
          </button>
        </div>
      </motion.div>
    </div>
  );
}

export default ApplicantProfilePage;
