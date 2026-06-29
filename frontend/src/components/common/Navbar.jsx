import { Link, NavLink } from 'react-router-dom';
import { Menu, Network } from 'lucide-react';
import Button from '../ui/Button';
import ThemeToggle from './ThemeToggle';

const navLinks = [
  { to: '/', label: 'Home', end: true },
  { to: '/upload', label: 'Upload' },
  { to: '/results', label: 'Results' },
  { to: '/recruiter', label: 'Recruiter' },
];

function Navbar({ onMenuToggle }) {
  return (
    <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/90 backdrop-blur dark:border-white/[0.06] dark:bg-black/60">
      <div className="page-container flex h-16 items-center justify-between">
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={onMenuToggle}
            className="rounded-lg p-2 text-slate-600 hover:bg-slate-100 lg:hidden"
            aria-label="Toggle sidebar"
          >
            <Menu className="h-5 w-5" />
          </button>

          <Link to="/" className="flex items-center gap-2 font-semibold text-slate-900 dark:text-white">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-600 text-white">
              <Network className="h-4 w-4" />
            </span>
            <span>TalentGraph</span>
          </Link>
        </div>

        <nav className="hidden items-center gap-1 md:flex">
          {navLinks.map(({ to, label, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                `rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-brand-50 text-brand-700 dark:bg-violet-500/10 dark:text-violet-300'
                    : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:text-zinc-400 dark:hover:bg-white/5 dark:hover:text-white'
                }`
              }
            >
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="flex items-center gap-2">
          <ThemeToggle />
          <Button as={Link} to="/upload" size="sm" className="hidden sm:inline-flex">
          Analyze Resume
          </Button>
        </div>
      </div>
    </header>
  );
}

export default Navbar;
