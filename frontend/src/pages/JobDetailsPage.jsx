import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Loader2 } from 'lucide-react';
import api from '../services/api';

function JobDetailsPage() {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    api.getJob(jobId)
      .then((data) => {
        setJob(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || 'Failed to load job.');
        setLoading(false);
      });
  }, [jobId]);

  if (loading) {
    return (
      <div className="page-container flex min-h-[50vh] items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-violet-500" />
      </div>
    );
  }

  if (error || !job) {
    return (
      <div className="page-container py-12">
        <p className="rounded-lg border border-rose-500/20 bg-rose-500/10 px-3 py-2 text-sm text-rose-600 dark:text-rose-400">
          {error || 'Job not found.'}
        </p>
        <Link to="/jobs" className="mt-4 inline-block text-sm font-medium text-violet-600 dark:text-violet-400">
          ← Back to jobs
        </Link>
      </div>
    );
  }

  const skills = (job.skills_required || job.requirements || '')
    .split(',')
    .map((skill) => skill.trim())
    .filter(Boolean);

  return (
    <div className="page-container py-12">
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="mx-auto max-w-2xl">
        <Link to="/jobs" className="text-sm font-medium text-violet-600 dark:text-violet-400">
          ← Back to jobs
        </Link>
        <p className="tg-label-wide mt-4">Job details</p>
        <h1 className="mt-2 text-3xl font-bold tg-heading">{job.title}</h1>

        <div className="tg-surface mt-8 space-y-5 p-6 sm:p-8">
          <div>
            <p className="tg-label">Company</p>
            <p className="mt-1 text-sm tg-body">{job.company || '—'}</p>
          </div>
          <div>
            <p className="tg-label">Location</p>
            <p className="mt-1 text-sm tg-body">{job.location || '—'}</p>
          </div>
          <div>
            <p className="tg-label">Experience required</p>
            <p className="mt-1 text-sm tg-body">{job.experience_required || '—'}</p>
          </div>
          <div>
            <p className="tg-label">Skills required</p>
            {skills.length ? (
              <p className="mt-1 text-sm tg-body">{skills.join(', ')}</p>
            ) : (
              <p className="mt-1 text-sm tg-body">—</p>
            )}
          </div>
          <div>
            <p className="tg-label">Job description</p>
            <p className="mt-1 whitespace-pre-wrap text-sm tg-body">{job.description}</p>
          </div>

          <button
            type="button"
            onClick={() => navigate(`/jobs/${job.id}/apply`)}
            className="tg-primary-btn w-full"
          >
            Apply
          </button>
        </div>
      </motion.div>
    </div>
  );
}

export default JobDetailsPage;
