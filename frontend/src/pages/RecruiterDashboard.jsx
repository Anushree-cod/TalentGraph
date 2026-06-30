import { useState, useEffect, useCallback } from 'react';
import { Users, CheckCircle2, Sparkles, TrendingUp } from 'lucide-react';
import DashboardHeader from '../components/dashboard/DashboardHeader';
import StatCard from '../components/dashboard/StatCard';
import DomainBarChart from '../components/dashboard/DomainBarChart';
import PipelineDonutChart from '../components/dashboard/PipelineDonutChart';
import ApplicationsChart from '../components/dashboard/ApplicationsChart';
import CandidateRankingTable from '../components/dashboard/CandidateRankingTable';
import CandidateDetailModal from '../components/dashboard/CandidateDetailModal';
import api from '../services/api';

const statMeta = [
  {
    key: 'candidates',
    label: 'Candidates',
    icon: Users,
    iconBg: 'bg-violet-500/10',
    iconColor: 'text-violet-500 dark:text-violet-400',
  },
  {
    key: 'shortlisted',
    label: 'Shortlisted',
    icon: CheckCircle2,
    iconBg: 'bg-emerald-500/10',
    iconColor: 'text-emerald-600 dark:text-emerald-400',
  },
  {
    key: 'interviewing',
    label: 'Interviewing',
    icon: Sparkles,
    iconBg: 'bg-cyan-500/10',
    iconColor: 'text-cyan-600 dark:text-cyan-400',
  },
  {
    key: 'avg_ats',
    label: 'Avg ATS',
    icon: TrendingUp,
    iconBg: 'bg-violet-500/10',
    iconColor: 'text-violet-500 dark:text-violet-400',
  },
];

function RecruiterDashboard() {
  const [candidates, setCandidates] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedCandidate, setSelectedCandidate] = useState(null);
  const [detailOpen, setDetailOpen] = useState(false);
  const [detailLoading, setDetailLoading] = useState(false);
  const [updating, setUpdating] = useState(false);

  const loadDashboard = useCallback(() => {
    setLoading(true);
    api.getRecruiterMetrics()
      .then((data) => {
        setMetrics(data);
        setCandidates(data.top_candidates || []);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Failed to fetch recruiter metrics:', err);
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    loadDashboard();
  }, [loadDashboard]);

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
        loadDashboard();
      })
      .catch((err) => {
        console.error('Failed to update application status:', err);
      })
      .finally(() => {
        setUpdating(false);
      });
  };

  const stats = statMeta.map((meta) => {
    const statsData = metrics?.stats || {};
    const value = String(statsData[meta.key] ?? 0);
    let change = '';
    let trend = 'up';

    if (meta.key === 'candidates') {
      change = `${metrics?.total_jobs ?? 0} jobs posted`;
    } else if (meta.key === 'shortlisted') {
      change = `${metrics?.total_applications ?? 0} applications`;
    } else if (meta.key === 'interviewing') {
      change = 'in pipeline';
    } else if (meta.key === 'avg_ats') {
      change = 'avg match score';
    }

    return { ...meta, value, change, trend };
  });

  return (
    <div className="page-container py-12">
      <DashboardHeader />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat, index) => (
          <StatCard key={stat.label} {...stat} index={index} />
        ))}
      </div>

      <div className="mt-4 grid gap-4 lg:mt-5 lg:grid-cols-3">
        <DomainBarChart data={metrics?.domain_data} />
        <PipelineDonutChart data={metrics?.pipeline} />
      </div>

      <div className="mt-4 space-y-4 lg:mt-5">
        <ApplicationsChart data={metrics?.applications_per_job} />
        {loading ? (
          <div className="tg-surface flex items-center justify-center p-5 sm:p-6">
            Loading AI Matches...
          </div>
        ) : (
          <CandidateRankingTable
            candidates={candidates}
            onSelectCandidate={handleSelectCandidate}
          />
        )}
      </div>

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

export default RecruiterDashboard;
