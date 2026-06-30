import { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

const EXPERIENCE_OPTIONS = ['0-2 years', '2-5 years', '5+ years'];

function PostJobPage() {
  const navigate = useNavigate();
  const [title, setTitle] = useState('');
  const [skillsRequired, setSkillsRequired] = useState('');
  const [experienceRequired, setExperienceRequired] = useState('');
  const [location, setLocation] = useState('');
  const [description, setDescription] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await api.createJob({
        title,
        description,
        skills_required: skillsRequired,
        experience_required: experienceRequired,
        location,
        requirements: skillsRequired,
      });
      navigate('/recruiter/candidates');
    } catch (err) {
      setError(err.message || 'Failed to post job.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container py-12">
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="mx-auto max-w-2xl">
        <p className="tg-label-wide">Recruiter</p>
        <h1 className="mt-2 text-3xl font-bold tg-heading">Post a job</h1>
        <p className="mt-2 text-sm tg-body">Create a new opening for applicants to discover.</p>

        <form onSubmit={handleSubmit} className="tg-surface mt-8 space-y-4 p-6 sm:p-8">
          <div>
            <label className="tg-label">Job title</label>
            <input className="tg-input mt-2" value={title} onChange={(e) => setTitle(e.target.value)} required />
          </div>
          <div>
            <label className="tg-label">Skills required</label>
            <input
              className="tg-input mt-2"
              value={skillsRequired}
              onChange={(e) => setSkillsRequired(e.target.value)}
              placeholder="e.g. React, Python, SQL"
              required
            />
            <p className="mt-1 text-xs tg-muted">Separate skills with commas</p>
          </div>
          <div>
            <label className="tg-label">Experience required</label>
            <select
              className="tg-input mt-2"
              value={experienceRequired}
              onChange={(e) => setExperienceRequired(e.target.value)}
              required
            >
              <option value="">Select experience level</option>
              {EXPERIENCE_OPTIONS.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="tg-label">Location</label>
            <input
              className="tg-input mt-2"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="e.g. Remote, New York, NY"
              required
            />
          </div>
          <div>
            <label className="tg-label">Job description</label>
            <textarea
              className="tg-input mt-2 min-h-28"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              required
            />
          </div>
          {error && (
            <p className="rounded-lg border border-rose-500/20 bg-rose-500/10 px-3 py-2 text-sm text-rose-600 dark:text-rose-400">
              {error}
            </p>
          )}
          <button type="submit" disabled={loading} className="tg-primary-btn w-full disabled:opacity-60">
            {loading ? 'Posting…' : 'Post job'}
          </button>
        </form>
      </motion.div>
    </div>
  );
}

export default PostJobPage;
