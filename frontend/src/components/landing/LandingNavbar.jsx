import { useEffect, useState } from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Menu,
  Sparkles,
  X,
  Home,
  LogIn,
  UserPlus,
  LogOut,
} from 'lucide-react';
import ThemeToggle from '../common/ThemeToggle';
import { getSession, signOut } from '../../services/auth';
import { getNavLinksForRole } from '../../config/navigation';
import { getDashboardPath } from '../../utils/roles';

function LandingNavbar() {
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);
  const session = getSession();
  const navLinks = session?.token ? getNavLinksForRole(session.role) : [{ to: '/', label: 'Product', end: true }];

  useEffect(() => {
    document.body.style.overflow = mobileOpen ? 'hidden' : '';
    return () => {
      document.body.style.overflow = '';
    };
  }, [mobileOpen]);

  const handleLogout = () => {
    signOut();
    setMobileOpen(false);
    navigate('/signin');
  };

  return (
    <>
      <motion.header
        initial={{ opacity: 0, y: -12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: 'easeOut' }}
        className="tg-navbar"
      >
        <div className="mx-auto flex h-16 max-w-7xl items-center gap-3 px-4 sm:px-6 lg:px-8">
          {/* Left: hamburger + logo */}
          <div className="flex min-w-0 flex-1 items-center gap-2 md:flex-none">
            <button
              type="button"
              onClick={() => setMobileOpen(true)}
              className="rounded-lg p-2 tg-nav-link md:hidden"
              aria-label="Open menu"
            >
              <Menu className="h-5 w-5" />
            </button>

            <Link to="/" className="flex min-w-0 items-center gap-2.5">
              <span className="flex h-7 w-7 shrink-0 items-center justify-center">
                <Sparkles className="h-5 w-5 text-violet-500" strokeWidth={2} />
              </span>
              <span className="truncate text-[15px] font-semibold tracking-tight tg-heading">
                TalentGraph
              </span>
            </Link>
          </div>

          {/* Center: desktop nav */}
          <nav className="hidden flex-1 items-center justify-center gap-8 md:flex">
            {navLinks.map(({ to, label, end }) => (
              <NavLink
                key={to}
                to={to}
                end={end}
                className={({ isActive }) =>
                  `relative text-[13px] font-medium ${
                    isActive ? 'tg-nav-link-active' : 'tg-nav-link'
                  }`
                }
              >
                {({ isActive }) => (
                  <>
                    {label}
                    {isActive && (
                      <motion.span
                        layoutId="landing-nav-underline"
                        className="absolute -bottom-[21px] left-0 right-0 h-[2px] bg-violet-500"
                        transition={{ type: 'spring', stiffness: 380, damping: 30 }}
                      />
                    )}
                  </>
                )}
              </NavLink>
            ))}
          </nav>

          {/* Right: actions */}
          <div className="flex shrink-0 items-center gap-1 sm:gap-2">
            <ThemeToggle />
            {session?.token ? (
              <>
                <Link
                  to={getDashboardPath(session.role)}
                  className="hidden text-[13px] font-medium tg-nav-link sm:inline-block"
                >
                  Dashboard
                </Link>
                <button
                  type="button"
                  onClick={handleLogout}
                  className="hidden text-[13px] font-medium tg-nav-link sm:inline-block"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/signin"
                  className="hidden text-[13px] font-medium tg-nav-link sm:inline-block"
                >
                  Sign in
                </Link>
                <Link to="/signup" className="tg-navbar-cta">
                  Get started
                </Link>
              </>
            )}
          </div>
        </div>
      </motion.header>

      {/* Mobile left drawer */}
      <AnimatePresence>
        {mobileOpen && (
          <>
            <motion.button
              type="button"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 z-[60] bg-black/50 backdrop-blur-sm md:hidden"
              onClick={() => setMobileOpen(false)}
              aria-label="Close menu overlay"
            />

            <motion.aside
              initial={{ x: '-100%' }}
              animate={{ x: 0 }}
              exit={{ x: '-100%' }}
              transition={{ type: 'spring', stiffness: 380, damping: 36 }}
              className="tg-mobile-drawer fixed inset-y-0 left-0 z-[70] flex w-[min(300px,85vw)] flex-col shadow-2xl md:hidden"
            >
              <div className="flex items-center justify-between border-b border-inherit px-5 py-4">
                <Link
                  to="/"
                  onClick={() => setMobileOpen(false)}
                  className="flex items-center gap-2"
                >
                  <Sparkles className="h-5 w-5 text-violet-500" />
                  <span className="text-[15px] font-semibold tg-heading">TalentGraph</span>
                </Link>
                <button
                  type="button"
                  onClick={() => setMobileOpen(false)}
                  className="rounded-lg p-2 tg-nav-link"
                  aria-label="Close menu"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              <nav className="flex flex-1 flex-col gap-1 overflow-y-auto px-3 py-4">
                <p className="mb-2 px-3 text-[10px] font-semibold uppercase tracking-[0.2em] tg-muted">
                  Menu
                </p>
                {navLinks.map(({ to, label, end }) => (
                  <NavLink
                    key={to}
                    to={to}
                    end={end}
                    onClick={() => setMobileOpen(false)}
                    className={({ isActive }) =>
                      `flex items-center gap-3 rounded-xl px-3 py-3 text-[15px] font-medium transition-colors ${
                        isActive ? 'tg-nav-mobile-active' : 'tg-nav-mobile'
                      }`
                    }
                  >
                    <Home className="h-[18px] w-[18px] shrink-0 opacity-70" />
                    {label}
                  </NavLink>
                ))}

                <div className="my-3 border-t border-slate-200 dark:border-white/[0.06]" />

                {session?.token ? (
                  <button
                    type="button"
                    onClick={handleLogout}
                    className="flex w-full items-center gap-3 rounded-xl px-3 py-3 text-[15px] font-medium tg-nav-mobile"
                  >
                    <LogOut className="h-[18px] w-[18px] shrink-0 opacity-70" />
                    Logout
                  </button>
                ) : (
                  <>
                    <p className="mb-2 px-3 text-[10px] font-semibold uppercase tracking-[0.2em] tg-muted">
                      Account
                    </p>
                    <Link
                      to="/signin"
                      onClick={() => setMobileOpen(false)}
                      className="flex items-center gap-3 rounded-xl px-3 py-3 text-[15px] font-medium tg-nav-mobile"
                    >
                      <LogIn className="h-[18px] w-[18px] shrink-0 opacity-70" />
                      Sign in
                    </Link>
                    <Link
                      to="/signup"
                      onClick={() => setMobileOpen(false)}
                      className="flex items-center gap-3 rounded-xl px-3 py-3 text-[15px] font-medium tg-nav-mobile"
                    >
                      <UserPlus className="h-[18px] w-[18px] shrink-0 opacity-70" />
                      Sign up
                    </Link>
                  </>
                )}
              </nav>

              {!session?.token && (
                <div className="border-t border-inherit p-4">
                  <Link
                    to="/signup"
                    onClick={() => setMobileOpen(false)}
                    className="tg-primary-btn w-full"
                  >
                    Get started
                  </Link>
                </div>
              )}
            </motion.aside>
          </>
        )}
      </AnimatePresence>
    </>
  );
}

export default LandingNavbar;
