import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Lock, Mail } from 'lucide-react';
import PageShell from '../components/layout/PageShell';
import { signIn } from '../services/auth';
import { getDashboardPath, ROLES } from '../utils/roles';

function isPathAllowedForRole(path, role) {
  if (!path) {
    return false;
  }
  if (role === ROLES.RECRUITER) {
    return path.startsWith('/recruiter');
  }
  if (role === ROLES.APPLICANT) {
    return ['/jobs', '/applications', '/profile'].some((prefix) => path.startsWith(prefix));
  }
  return false;
}

function AuthField({ label, icon: Icon, type = 'text', value, onChange, placeholder, autoComplete }) {
  return (
    <div>
      <label className="tg-label">{label}</label>
      <div className="relative mt-2">
        <Icon className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400 dark:text-zinc-500" />
        <input
          type={type}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          autoComplete={autoComplete}
          required
          className="tg-input !pl-10"
        />
      </div>
    </div>
  );
}

function SignInPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const session = await signIn({ email, password });
      const from = location.state?.from;
      const destination = isPathAllowedForRole(from, session.role)
        ? from
        : getDashboardPath(session.role);
      navigate(destination);
    } catch (err) {
      setError(err.message || 'Sign in failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <PageShell>
      <main className="relative mx-auto flex min-h-[calc(100vh-4rem)] max-w-md items-center px-4 py-28 sm:px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="w-full"
        >
          <div className="mb-8 text-center">
            <p className="tg-label-wide">Welcome back</p>
            <h1 className="mt-3 text-3xl font-bold tg-heading">Sign in to TalentGraph</h1>
            <p className="mt-3 text-sm tg-body">
              Access your recruiter dashboard and candidate pipeline.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="tg-surface space-y-4 p-6 sm:p-8">
            <AuthField
              label="Email"
              icon={Mail}
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@company.com"
              autoComplete="email"
            />
            <AuthField
              label="Password"
              icon={Lock}
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Your password"
              autoComplete="current-password"
            />

            {error && (
              <p className="rounded-lg border border-rose-500/20 bg-rose-500/10 px-3 py-2 text-sm text-rose-600 dark:text-rose-400">
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={loading}
              className="tg-primary-btn w-full disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading ? 'Signing in…' : 'Sign in'}
            </button>
          </form>

          <p className="mt-6 text-center text-sm tg-body">
            Don&apos;t have an account?{' '}
            <Link to="/signup" className="font-medium text-violet-600 hover:text-violet-500 dark:text-violet-400">
              Create one
            </Link>
          </p>
        </motion.div>
      </main>
    </PageShell>
  );
}

export default SignInPage;
