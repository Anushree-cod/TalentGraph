import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import api from '../services/api';
import { getFriendlyStatus } from '../utils/applicationStatus';

function MyApplicationsPage() {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    api.getApplicantDashboard()
      .then((data) => {
        setApplications(data?.applications || []);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || 'Failed to load applications.');
        setLoading(false);
      });
  }, []);

  return (
    <div className="page-container py-12">
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
        <p className="tg-label-wide">Applicant</p>
        <h1 className="mt-2 text-3xl font-bold tg-heading">My applications</h1>
        <p className="mt-2 text-sm tg-body">Track jobs you have applied to and their status.</p>

        <div className="mt-8 space-y-4">
          {loading && <div className="tg-surface p-6 text-center text-sm tg-muted">Loading applications…</div>}
          {error && (
            <p className="rounded-lg border border-rose-500/20 bg-rose-500/10 px-3 py-2 text-sm text-rose-600 dark:text-rose-400">
              {error}
            </p>
          )}
          {!loading && !error && applications.length === 0 && (
            <div className="tg-surface p-6 text-center text-sm tg-muted">You have not applied to any jobs yet.</div>
          )}
          {applications.map((app) => (
            <div key={app.job_id} className="tg-surface flex flex-col gap-2 p-5 sm:flex-row sm:items-center sm:justify-between sm:p-6">
              <div>
                <h2 className="text-lg font-semibold tg-heading">{app.job_title}</h2>
                <p className="mt-1 text-sm tg-muted">Status: {getFriendlyStatus(app.status)}</p>
              </div>
              <div className="text-sm font-medium text-violet-600 dark:text-violet-400">
                Match score: {app.match_score ?? 0}%
              </div>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  );
}

export default MyApplicationsPage;
