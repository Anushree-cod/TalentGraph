import { motion } from 'framer-motion';
import { ArrowUpDown, ChevronDown, Search } from 'lucide-react';
import { getFriendlyStatus } from '../../utils/applicationStatus';

const statusStyles = {
  SHORTLISTED:
    'border-emerald-500/30 bg-emerald-500/10 text-emerald-700 dark:text-emerald-400',
  INTERVIEWING: 'border-cyan-500/30 bg-cyan-500/10 text-cyan-700 dark:text-cyan-400',
  APPLIED: 'border-violet-500/30 bg-violet-500/10 text-violet-700 dark:text-violet-400',
  applied: 'border-violet-500/30 bg-violet-500/10 text-violet-700 dark:text-violet-400',
  analyzed: 'border-cyan-500/30 bg-cyan-500/10 text-cyan-700 dark:text-cyan-400',
  shortlisted: 'border-emerald-500/30 bg-emerald-500/10 text-emerald-700 dark:text-emerald-400',
  rejected: 'border-rose-500/30 bg-rose-500/10 text-rose-700 dark:text-rose-400',
  interviewing: 'border-cyan-500/30 bg-cyan-500/10 text-cyan-700 dark:text-cyan-400',
  interview: 'border-cyan-500/30 bg-cyan-500/10 text-cyan-700 dark:text-cyan-400',
  selected: 'border-violet-500/30 bg-violet-500/10 text-violet-700 dark:text-violet-400',
};

function getInitials(name) {
  if (!name) {
    return 'NA';
  }
  return name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join('');
}

function CandidateRankingTable({ candidates = [], onSelectCandidate }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.35 }}
      className="tg-surface p-5 sm:p-6"
    >
      <p className="tg-label">Candidate ranking</p>
      <h2 className="mt-1 text-lg font-semibold tg-heading">
        Sorted by ATS · click a row for the profile
      </h2>

      <div className="mt-5 flex flex-col gap-3 sm:flex-row">
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400 dark:text-zinc-500" />
          <input
            type="text"
            placeholder="Search by name, role, or skill..."
            className="tg-input"
          />
        </div>
        {['All domains', 'All statuses'].map((label) => (
          <button key={label} type="button" className="tg-filter-btn">
            {label}
            <ChevronDown className="h-4 w-4 text-slate-400 dark:text-zinc-500" />
          </button>
        ))}
      </div>

      <div className="mt-5 overflow-x-auto">
        <table className="w-full min-w-[720px] text-left">
          <thead>
            <tr className="tg-table-head">
              {['Candidate', 'Domain', 'Exp', 'ATS', 'Match', 'Status', 'Location'].map(
                (col) => (
                  <th key={col} className="pb-3 pr-4 font-semibold last:pr-0">
                    <span className="inline-flex items-center gap-1">
                      {col}
                      {col !== 'Status' && col !== 'Location' && (
                        <ArrowUpDown className="h-3 w-3 opacity-50" />
                      )}
                    </span>
                  </th>
                ),
              )}
            </tr>
          </thead>
          <tbody>
            {candidates.map((candidate, index) => {
              const skills = candidate.skills || candidate.matched_skills || [];
              const domain = skills.slice(0, 2).join(', ') || '—';
              const name = candidate.applicant_name || `Candidate #${candidate.applicant_id}`;

              return (
                <motion.tr
                  key={candidate.application_id || candidate.applicant_id || index}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.4 + index * 0.06 }}
                  className="tg-table-row cursor-pointer"
                  title={candidate.resume_summary || ''}
                  onClick={() => onSelectCandidate?.(candidate)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      onSelectCandidate?.(candidate);
                    }
                  }}
                  tabIndex={0}
                >
                  <td className="py-4 pr-4">
                    <div className="flex items-center gap-3">
                      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-violet-500 text-[11px] font-semibold text-white">
                        {getInitials(name)}
                      </div>
                      <div>
                        <p className="text-[14px] font-semibold tg-heading">
                          {name}
                          {candidate.rank ? ` · #${candidate.rank}` : ''}
                        </p>
                        <p className="text-[12px] tg-muted">
                          {candidate.recommendation || 'Pending review'}
                        </p>
                      </div>
                    </div>
                  </td>
                  <td className="py-4 pr-4 text-[13px] text-slate-700 dark:text-zinc-300">
                    {domain}
                  </td>
                  <td className="py-4 pr-4 text-[13px] text-slate-700 dark:text-zinc-300">
                    {candidate.years_experience != null ? `${candidate.years_experience} yrs` : '—'}
                  </td>
                  <td className="py-4 pr-4 text-[14px] font-semibold text-emerald-600 dark:text-emerald-400">
                    {candidate.ats_score ?? candidate.match_score ?? 0}%
                  </td>
                  <td className="py-4 pr-4">
                    <div className="flex items-center gap-2">
                      <div className="tg-progress-track h-1.5 w-16">
                        <div
                          className="h-full rounded-full bg-gradient-to-r from-violet-500 to-cyan-400"
                          style={{ width: `${candidate.match_score ?? 0}%` }}
                        />
                      </div>
                      <span className="text-[13px] font-medium text-slate-700 dark:text-zinc-300">
                        {candidate.match_score ?? 0}%
                      </span>
                    </div>
                  </td>
                  <td className="py-4 pr-4">
                    <span
                      className={`inline-block rounded-full border px-2.5 py-0.5 text-[10px] font-semibold tracking-wide ${statusStyles[candidate.status] || statusStyles[candidate.status?.toUpperCase()] || statusStyles.APPLIED}`}
                    >
                      {getFriendlyStatus(candidate.status)}
                    </span>
                  </td>
                  <td className="py-4 text-[13px] tg-muted">{candidate.location || '—'}</td>
                </motion.tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </motion.div>
  );
}

export default CandidateRankingTable;
