import { Link } from 'react-router-dom';
import { Sparkles } from 'lucide-react';

function LandingFooter() {
  return (
    <footer className="tg-footer">
      <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-4 py-8 sm:flex-row sm:px-6">
        <Link to="/" className="flex items-center gap-2.5">
          <Sparkles className="h-4 w-4 text-violet-500 dark:text-violet-400" />
          <span className="text-[15px] font-semibold tg-heading">TalentGraph</span>
        </Link>
        <p className="text-center text-[13px] tg-muted sm:text-right">
          &copy; 2026 TalentGraph Labs &middot; Crafted for recruiters who care.
        </p>
      </div>
    </footer>
  );
}

export default LandingFooter;
