import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import CandidateRankingTable from '../components/dashboard/CandidateRankingTable';
import CandidateDetailModal from '../components/dashboard/CandidateDetailModal';
import api from '../services/api';

function ViewCandidatesPage() {
  const [jobs, setJobs] = useState([]);
  const [selectedJobId, setSelectedJobId] = useState(null);
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedCandidate, setSelectedCandidate] = useState(null);
  const [detailOpen, setDetailOpen] = useState(false);
  const [detailLoading, setDetailLoading] = useState(false);
  const [updating, setUpdating] = useState(false);

  useEffect(() => {
    api.getRecruiterJobs()
      .then((jobList) => {
        setJobs(jobList || []);
        if (jobList?.length) {
          setSelectedJobId(jobList[0].id);
        } else {
          setLoading(false);
        }
      })
      .catch((err) => {
        setError(err.message || 'Failed to load jobs.');
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    if (!selectedJobId) {
      return;
    }

    setLoading(true);
    api.getRecruiterDashboard(selectedJobId)
      .then((data) => {
        setCandidates(data || []);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || 'Failed to load candidates.');
        setLoading(false);
      });
  }, [selectedJobId]);

  const refreshCandidates = () => {
    if (!selectedJobId) {
      return;
    }
    api.getRecruiterDashboard(selectedJobId)
      .then((data) => setCandidates(data || []))
      .catch((err) => console.error('Failed to refresh candidates:', err));
  };

  const handleSelectCandidate = (candidate) => {
    if (!candidate.application_id) {
      setSelectedCandidate(candidate);
      setDetailOpen(true);
      return;
    }

    setDetailLoading(true);
    setDetailOpen(true);
    api.getApplicationDetail(candidate.application_id)
      .then((detail) => {
        setSelectedCandidate(detail);
        setDetailLoading(false);
      })
      .catch((err) => {
        console.error('Failed to load candidate detail:', err);
        setSelectedCandidate(candidate);
        setDetailLoading(false);
      });
  };

  const updateCandidateStatus = (candidate, status) => {
    if (!candidate?.application_id) {
      return;
    }

    setUpdating(true);
    api.updateApplicationStatus(candidate.application_id, status)
      .then((updated) => {
        setSelectedCandidate((prev) => (prev ? { ...prev, ...updated, status } : prev));
        setCandidates((prev) =>
          prev.map((item) =>
            item.application_id === candidate.application_id
              ? { ...item, ...updated, status }
              : item,
          ),
        );
        refreshCandidates();
      })
      .catch((err) => {
        console.error('Failed to update application status:', err);
      })
      .finally(() => {
        setUpdating(false);
      });
  };

  return (
    <div className="page-container py-12">
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
        <p className="tg-label-wide">Recruiter</p>
        <h1 className="mt-2 text-3xl font-bold tg-heading">View candidates</h1>
        <p className="mt-2 text-sm tg-body">Ranked applicants for your open roles.</p>

        {jobs.length > 0 && (
          <div className="mt-6 max-w-md">
            <label className="tg-label">Select job</label>
            <select
              className="tg-input mt-2"
              value={selectedJobId ?? ''}
              onChange={(e) => setSelectedJobId(Number(e.target.value))}
            >
              {jobs.map((job) => (
                <option key={job.id} value={job.id}>
                  {job.title}
                </option>
              ))}
            </select>
          </div>
        )}

        <div className="mt-6">
          {error && (
            <p className="rounded-lg border border-rose-500/20 bg-rose-500/10 px-3 py-2 text-sm text-rose-600 dark:text-rose-400">
              {error}
            </p>
          )}
          {!error && loading && (
            <div className="tg-surface p-6 text-center text-sm tg-muted">Loading ranked candidates…</div>
          )}
          {!error && !loading && jobs.length === 0 && (
            <div className="tg-surface p-6 text-center text-sm tg-muted">Post a job to start receiving applications.</div>
          )}
          {!error && !loading && jobs.length > 0 && (
            <CandidateRankingTable
              candidates={candidates}
              onSelectCandidate={handleSelectCandidate}
            />
          )}
        </div>
      </motion.div>

      <CandidateDetailModal
        candidate={detailLoading ? null : selectedCandidate}
        isOpen={detailOpen}
        onClose={() => {
          setDetailOpen(false);
          setSelectedCandidate(null);
        }}
        onShortlist={(candidate) => updateCandidateStatus(candidate, 'shortlisted')}
        onReject={(candidate) => updateCandidateStatus(candidate, 'rejected')}
        updating={updating || detailLoading}
      />
      {detailOpen && detailLoading && (
        <div className="fixed inset-0 z-[90] flex items-center justify-center bg-black/30">
          <div className="tg-surface px-6 py-4 text-sm tg-muted">Loading candidate details…</div>
        </div>
      )}
    </div>
  );
}

export default ViewCandidatesPage;
