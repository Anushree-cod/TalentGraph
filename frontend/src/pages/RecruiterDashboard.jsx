import { Users, CheckCircle2, Sparkles, TrendingUp } from 'lucide-react';
import PageShell from '../components/layout/PageShell';
import DashboardHeader from '../components/dashboard/DashboardHeader';
import StatCard from '../components/dashboard/StatCard';
import DomainBarChart from '../components/dashboard/DomainBarChart';
import PipelineDonutChart from '../components/dashboard/PipelineDonutChart';
import ApplicationsChart from '../components/dashboard/ApplicationsChart';
import CandidateRankingTable from '../components/dashboard/CandidateRankingTable';

const stats = [
  {
    label: 'Candidates',
    value: '24',
    change: '12% this week',
    trend: 'up',
    icon: Users,
    iconBg: 'bg-violet-500/10',
    iconColor: 'text-violet-500 dark:text-violet-400',
  },
  {
    label: 'Shortlisted',
    value: '8',
    change: '8% this week',
    trend: 'up',
    icon: CheckCircle2,
    iconBg: 'bg-emerald-500/10',
    iconColor: 'text-emerald-600 dark:text-emerald-400',
  },
  {
    label: 'Interviewing',
    value: '6',
    change: '3% this week',
    trend: 'down',
    icon: Sparkles,
    iconBg: 'bg-cyan-500/10',
    iconColor: 'text-cyan-600 dark:text-cyan-400',
  },
  {
    label: 'Avg ATS',
    value: '86',
    change: '4% this week',
    trend: 'up',
    icon: TrendingUp,
    iconBg: 'bg-violet-500/10',
    iconColor: 'text-violet-500 dark:text-violet-400',
  },
];

function RecruiterDashboard() {
  return (
    <PageShell>
      <main className="relative mx-auto max-w-6xl px-4 pb-16 pt-28 sm:px-6 sm:pt-32 lg:pb-20">
        <DashboardHeader />

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {stats.map((stat, index) => (
            <StatCard key={stat.label} {...stat} index={index} />
          ))}
        </div>

        <div className="mt-4 grid gap-4 lg:mt-5 lg:grid-cols-3">
          <DomainBarChart />
          <PipelineDonutChart />
        </div>

        <div className="mt-4 space-y-4 lg:mt-5">
          <ApplicationsChart />
          <CandidateRankingTable />
        </div>
      </main>
    </PageShell>
  );
}

export default RecruiterDashboard;
