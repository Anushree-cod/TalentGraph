import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Building2, Lock, Mail, User } from 'lucide-react';
import PageShell from '../components/layout/PageShell';
import { signUp } from '../services/auth';
import { getDashboardPath } from '../utils/roles';

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

function SignUpPage() {
  const navigate = useNavigate();
  const [accountType, setAccountType] = useState('applicant');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [company, setCompany] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (password.length < 6) {
      setError('Password must be at least 6 characters.');
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    setLoading(true);

    try {
      const session = await signUp({
        email,
        password,
        isRecruiter: accountType === 'recruiter',
      });
      navigate(getDashboardPath(session.role));
    } catch (err) {
      setError(err.message || 'Sign up failed. Please try again.');
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
            <p className="tg-label-wide">Get started</p>
            <h1 className="mt-3 text-3xl font-bold tg-heading">Create your account</h1>
            <p className="mt-3 text-sm tg-body">
              Join TalentGraph to analyze resumes and rank candidates faster.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="tg-surface space-y-4 p-6 sm:p-8">
            <div>
              <label className="tg-label">Account type</label>
              <div className="mt-2 grid grid-cols-2 gap-2">
                {[
                  { value: 'applicant', label: 'Applicant' },
                  { value: 'recruiter', label: 'Recruiter' },
                ].map((option) => (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => setAccountType(option.value)}
                    className={`rounded-lg border px-3 py-2 text-sm font-medium transition-colors ${
                      accountType === option.value
                        ? 'border-violet-500 bg-violet-500/10 text-violet-700 dark:text-violet-300'
                        : 'border-slate-200 text-slate-600 dark:border-white/10 dark:text-zinc-400'
                    }`}
                  >
                    {option.label}
                  </button>
                ))}
              </div>
            </div>
            <AuthField
              label="Full name"
              icon={User}
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Jane Doe"
              autoComplete="name"
            />
            <AuthField
              label="Work email"
              icon={Mail}
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@company.com"
              autoComplete="email"
            />
            <AuthField
              label="Company"
              icon={Building2}
              value={company}
              onChange={(e) => setCompany(e.target.value)}
              placeholder="TalentGraph Labs"
              autoComplete="organization"
            />
            <AuthField
              label="Password"
              icon={Lock}
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Min. 6 characters"
              autoComplete="new-password"
            />
            <AuthField
              label="Confirm password"
              icon={Lock}
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Repeat password"
              autoComplete="new-password"
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
              {loading ? 'Creating account…' : 'Create account'}
            </button>
          </form>

          <p className="mt-6 text-center text-sm tg-body">
            Already have an account?{' '}
            <Link to="/signin" className="font-medium text-violet-600 hover:text-violet-500 dark:text-violet-400">
              Sign in
            </Link>
          </p>
        </motion.div>
      </main>
    </PageShell>
  );
}

export default SignUpPage;
