import { Link } from 'react-router-dom';

function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className="mt-auto border-t border-slate-200 bg-white">
      <div className="page-container flex flex-col items-center justify-between gap-4 py-6 sm:flex-row">
        <p className="text-sm text-slate-500">
          &copy; {year} TalentGraph. AI-Powered Resume Analyzer.
        </p>

        <div className="flex items-center gap-4 text-sm text-slate-500">
          <Link to="/" className="hover:text-slate-900">
            Home
          </Link>
          <Link to="/upload" className="hover:text-slate-900">
            Upload
          </Link>
          <Link to="/recruiter" className="hover:text-slate-900">
            Recruiter
          </Link>
        </div>
      </div>
    </footer>
  );
}

export default Footer;
