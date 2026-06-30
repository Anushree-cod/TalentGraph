import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Loader2 } from 'lucide-react';
import PageShell from '../components/layout/PageShell';
import { useAnalysis } from '../context/AnalysisContext';
import { getSession } from '../services/auth';
import api from '../services/api';

function LoadingPage() {
  const navigate = useNavigate();
  const { pendingAnalysis, setAnalysisResult, clearPendingAnalysis } = useAnalysis();
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;

    async function runAnalysis() {
      if (!pendingAnalysis?.resumeFile) {
        navigate('/upload', { replace: true });
        return;
      }

      if (!getSession()?.token) {
        navigate('/signin', { state: { from: '/loading' }, replace: true });
        return;
      }

      const formData = new FormData();
      formData.append('resume', pendingAnalysis.resumeFile);
      formData.append('job_description', pendingAnalysis.jobDescription || '');
      formData.append('job_title', pendingAnalysis.jobTitle || '');
      formData.append('company', pendingAnalysis.company || '');

      try {
        const result = await api.uploadResume(formData);
        if (cancelled) {
          return;
        }

        setAnalysisResult(result);
        clearPendingAnalysis();
        navigate('/results', { replace: true });
      } catch (err) {
        if (cancelled) {
          return;
        }
        setError(err.message || 'Analysis failed. Please try again.');
      }
    }

    runAnalysis();

    return () => {
      cancelled = true;
    };
  }, [pendingAnalysis, setAnalysisResult, clearPendingAnalysis, navigate]);

  return (
    <PageShell>
      <main className="relative flex min-h-[calc(100vh-4rem)] items-center justify-center px-4 pt-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="tg-surface w-full max-w-md p-8 text-center"
        >
          {error ? (
            <>
              <h1 className="text-2xl font-bold tg-heading">Analysis failed</h1>
              <p className="mt-2 text-sm leading-relaxed text-rose-600 dark:text-rose-400">{error}</p>
              <button
                type="button"
                onClick={() => navigate('/upload')}
                className="tg-primary-btn mt-6"
              >
                Back to upload
              </button>
            </>
          ) : (
            <>
              <Loader2 className="mx-auto h-10 w-10 animate-spin text-violet-500 dark:text-violet-400" />
              <h1 className="mt-6 text-2xl font-bold tg-heading">Analyzing resume</h1>
              <p className="mt-2 text-sm leading-relaxed tg-body">
                Scoring against your job description on ATS rules, skill match, and
                recruiter signals.
              </p>
              <div className="tg-progress-track mt-6 h-1.5">
                <motion.div
                  initial={{ width: '0%' }}
                  animate={{ width: '100%' }}
                  transition={{ duration: 2.5, ease: 'easeInOut' }}
                  className="h-full rounded-full bg-gradient-to-r from-violet-500 to-cyan-400"
                />
              </div>
              <p className="mt-4 text-[12px] tg-muted">Waiting for backend response…</p>
            </>
          )}
        </motion.div>
      </main>
    </PageShell>
  );
}

export default LoadingPage;
