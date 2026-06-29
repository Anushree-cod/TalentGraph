import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Loader2 } from 'lucide-react';
import PageShell from '../components/layout/PageShell';

function LoadingPage() {
  const navigate = useNavigate();

  useEffect(() => {
    const timer = setTimeout(() => navigate('/recruiter'), 2800);
    return () => clearTimeout(timer);
  }, [navigate]);

  return (
    <PageShell>
      <main className="relative flex min-h-[calc(100vh-4rem)] items-center justify-center px-4 pt-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="tg-surface w-full max-w-md p-8 text-center"
        >
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
          <p className="mt-4 text-[12px] tg-muted">Redirecting to dashboard…</p>
        </motion.div>
      </main>
    </PageShell>
  );
}

export default LoadingPage;
