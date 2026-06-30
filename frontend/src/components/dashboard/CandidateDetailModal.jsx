import { motion, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';
import { getFriendlyStatus } from '../../utils/applicationStatus';

function CandidateDetailModal({ candidate, isOpen, onClose, onShortlist, onReject, updating }) {
  if (!isOpen || !candidate) {
    return null;
  }

  const skills = candidate.skills || candidate.matched_skills || [];
  const education = candidate.education || [];

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.button
            type="button"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[80] bg-black/50 backdrop-blur-sm"
            onClick={onClose}
            aria-label="Close candidate details"
          />
          <motion.div
            initial={{ opacity: 0, x: '-50%', y: 'calc(-50% + 24px)' }}
            animate={{ opacity: 1, x: '-50%', y: '-50%' }}
            exit={{ opacity: 0, x: '-50%', y: 'calc(-50% + 24px)' }}
            transition={{ duration: 0.25 }}
            className="tg-surface fixed left-1/2 top-1/2 z-[90] max-h-[90vh] w-[min(960px,calc(100vw-2rem))] overflow-y-auto p-6 sm:w-[min(960px,92vw)] sm:p-8"
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="tg-label">Candidate detail</p>
                <h2 className="mt-1 text-2xl font-bold tg-heading">
                  {candidate.applicant_name || `Candidate #${candidate.applicant_id}`}
                </h2>
                <p className="mt-1 text-sm tg-muted">
                  {candidate.job_title ? `${candidate.job_title} · ` : ''}
                  Rank #{candidate.rank ?? '—'}
                </p>
              </div>
              <button type="button" onClick={onClose} className="rounded-lg p-2 tg-nav-link" aria-label="Close">
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="mt-6 grid gap-4 sm:grid-cols-3">
              <div className="tg-surface rounded-xl border border-slate-200 p-4 dark:border-white/10">
                <p className="tg-label">ATS Score</p>
                <p className="mt-2 text-2xl font-bold text-emerald-600 dark:text-emerald-400">
                  {candidate.ats_score ?? candidate.match_score ?? 0}%
                </p>
              </div>
              <div className="tg-surface rounded-xl border border-slate-200 p-4 dark:border-white/10">
                <p className="tg-label">Match Score</p>
                <p className="mt-2 text-2xl font-bold tg-heading">{candidate.match_score ?? 0}%</p>
              </div>
              <div className="tg-surface rounded-xl border border-slate-200 p-4 dark:border-white/10">
                <p className="tg-label">Status</p>
                <p className="mt-2 text-sm font-semibold tg-heading">{getFriendlyStatus(candidate.status)}</p>
              </div>
            </div>

            <div className="mt-6 space-y-4 text-sm">
              <div>
                <p className="tg-label">Experience</p>
                <p className="mt-1 tg-body">
                  {candidate.years_experience != null ? `${candidate.years_experience} years` : '—'}
                  {candidate.location ? ` · ${candidate.location}` : ''}
                </p>
              </div>

              <div>
                <p className="tg-label">Extracted Skills</p>
                <p className="mt-1 tg-body">{skills.length ? skills.join(', ') : '—'}</p>
              </div>

              <div>
                <p className="tg-label">Resume Summary</p>
                <p className="mt-1 whitespace-pre-wrap tg-body">{candidate.resume_summary || '—'}</p>
              </div>

              <div>
                <p className="tg-label">Education</p>
                {education.length ? (
                  <ul className="mt-1 list-disc space-y-1 pl-5 tg-body">
                    {education.map((item, index) => (
                      <li key={index}>
                        {[item.degree, item.field, item.institution].filter(Boolean).join(' · ') || '—'}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="mt-1 tg-body">—</p>
                )}
              </div>

              <div>
                <p className="tg-label">Resume Preview</p>
                <pre className="mt-1 max-h-48 overflow-auto whitespace-pre-wrap rounded-lg bg-slate-50 p-3 text-xs tg-body dark:bg-white/5">
                  {candidate.resume_preview || candidate.resume_summary || '—'}
                </pre>
              </div>
            </div>

            <div className="mt-6 flex flex-wrap gap-3">
              <button
                type="button"
                disabled={updating}
                onClick={() => onShortlist(candidate)}
                className="tg-primary-btn disabled:opacity-60"
              >
                Shortlist
              </button>
              <button
                type="button"
                disabled={updating}
                onClick={() => onReject(candidate)}
                className="tg-filter-btn disabled:opacity-60"
              >
                Reject
              </button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

export default CandidateDetailModal;
