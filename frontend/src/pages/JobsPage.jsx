import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import api from '../services/api';

function JobsPage() {
  const navigate = useNavigate();
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    api.getJobs()
      .then((data) => {
        setJobs(data || []);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || 'Failed to load jobs.');
        setLoading(false);
      });
  }, []);

  return (
    <div className="page-container py-12">
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
        <p className="tg-label-wide">Applicant</p>
        <h1 className="mt-2 text-3xl font-bold tg-heading">Available jobs</h1>
        <p className="mt-2 text-sm tg-body">Browse openings and apply with your resume and details.</p>

        {error && (
          <p className="mt-4 rounded-lg border border-rose-500/20 bg-rose-500/10 px-3 py-2 text-sm text-rose-600 dark:text-rose-400">
            {error}
          </p>
        )}

        <div className="mt-8 space-y-4">
          {loading && <div className="tg-surface p-6 text-center text-sm tg-muted">Loading jobs…</div>}
          {!loading && jobs.length === 0 && (
            <div className="tg-surface p-6 text-center text-sm tg-muted">No jobs available right now.</div>
          )}
          {jobs.map((job) => (
            <div key={job.id} className="tg-surface p-5 sm:p-6">
              <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <h2 className="text-lg font-semibold tg-heading">{job.title}</h2>
                  <p className="mt-2 text-sm tg-body line-clamp-2">{job.description}</p>
                  <p className="mt-3 text-xs tg-muted">
                    {job.location ? `${job.location}` : 'Location not specified'}
                    {job.experience_required ? ` · ${job.experience_required}` : ''}
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => navigate(`/jobs/${job.id}`)}
                  className="tg-primary-btn shrink-0"
                >
                  View Details
                </button>
              </div>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  );
}

export default JobsPage;
