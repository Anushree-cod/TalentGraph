import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Loader2 } from 'lucide-react';
import api from '../services/api';
import { getSession } from '../services/auth';

function ApplyJobPage() {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const session = getSession();

  const [job, setJob] = useState(null);
  const [resumeFile, setResumeFile] = useState(null);
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState(session?.email || '');
  const [phone, setPhone] = useState('');
  const [location, setLocation] = useState('');
  const [yearsExperience, setYearsExperience] = useState('');
  const [expectedSalary, setExpectedSalary] = useState('');
  const [coverLetter, setCoverLetter] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingJob, setLoadingJob] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    api.getJob(jobId)
      .then((data) => {
        setJob(data);
        setLoadingJob(false);
      })
      .catch((err) => {
        setError(err.message || 'Failed to load job.');
        setLoadingJob(false);
      });
  }, [jobId]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!resumeFile) {
      setError('Resume upload is required.');
      return;
    }

    const formData = new FormData();
    formData.append('resume', resumeFile);
    formData.append('full_name', fullName);
    formData.append('email', email);
    formData.append('phone', phone);
    formData.append('location', location);
    formData.append('years_experience', yearsExperience);
    if (expectedSalary) {
      formData.append('expected_salary', expectedSalary);
    }
    if (coverLetter) {
      formData.append('cover_letter', coverLetter);
    }

    setLoading(true);
    try {
      const result = await api.submitApplication(jobId, formData);
      setSuccess(
        `${result.message} Match score: ${result.match_score ?? 0}% · ATS: ${result.ats_score ?? 0}%`,
      );
      setTimeout(() => navigate('/applications'), 1800);
    } catch (err) {
      setError(err.message || 'Failed to submit application.');
    } finally {
      setLoading(false);
    }
  };

  if (loadingJob) {
    return (
      <div className="page-container flex min-h-[50vh] items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-violet-500" />
      </div>
    );
  }

  return (
    <div className="page-container py-12">
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="mx-auto max-w-2xl">
        <Link to={`/jobs/${jobId}`} className="text-sm font-medium text-violet-600 dark:text-violet-400">
          ← Back to job details
        </Link>
        <p className="tg-label-wide mt-4">Apply</p>
        <h1 className="mt-2 text-3xl font-bold tg-heading">{job?.title}</h1>
        <p className="mt-2 text-sm tg-body">{job?.description}</p>

        <form onSubmit={handleSubmit} className="tg-surface mt-8 space-y-4 p-6 sm:p-8">
          <div>
            <label className="tg-label">Resume (PDF) *</label>
            <input
              type="file"
              accept=".pdf,application/pdf"
              onChange={(e) => setResumeFile(e.target.files?.[0] || null)}
              required
              className="tg-input mt-2 block w-full"
            />
          </div>

          <div>
            <label className="tg-label">Full Name *</label>
            <input className="tg-input mt-2" value={fullName} onChange={(e) => setFullName(e.target.value)} required />
          </div>

          <div>
            <label className="tg-label">Email *</label>
            <input type="email" className="tg-input mt-2" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </div>

          <div>
            <label className="tg-label">Phone Number *</label>
            <input className="tg-input mt-2" value={phone} onChange={(e) => setPhone(e.target.value)} required />
          </div>

          <div>
            <label className="tg-label">Current Location *</label>
            <input className="tg-input mt-2" value={location} onChange={(e) => setLocation(e.target.value)} required />
          </div>

          <div>
            <label className="tg-label">Years of Experience *</label>
            <input
              type="number"
              min="0"
              className="tg-input mt-2"
              value={yearsExperience}
              onChange={(e) => setYearsExperience(e.target.value)}
              required
            />
          </div>

          <div>
            <label className="tg-label">Expected Salary (optional)</label>
            <input className="tg-input mt-2" value={expectedSalary} onChange={(e) => setExpectedSalary(e.target.value)} />
          </div>

          <div>
            <label className="tg-label">Cover Letter (optional)</label>
            <textarea
              className="tg-input mt-2 min-h-28"
              value={coverLetter}
              onChange={(e) => setCoverLetter(e.target.value)}
            />
          </div>

          {error && (
            <p className="rounded-lg border border-rose-500/20 bg-rose-500/10 px-3 py-2 text-sm text-rose-600 dark:text-rose-400">
              {error}
            </p>
          )}
          {success && (
            <p className="rounded-lg border border-emerald-500/20 bg-emerald-500/10 px-3 py-2 text-sm text-emerald-700 dark:text-emerald-400">
              {success}
            </p>
          )}

          <button type="submit" disabled={loading} className="tg-primary-btn w-full disabled:opacity-60">
            {loading ? (
              <span className="inline-flex items-center justify-center gap-2">
                <Loader2 className="h-4 w-4 animate-spin" />
                Analyzing application…
              </span>
            ) : (
              'Submit application'
            )}
          </button>
        </form>
      </motion.div>
    </div>
  );
}

export default ApplyJobPage;
