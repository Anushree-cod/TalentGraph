import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import Card from '../components/ui/Card';

const skillData = [
  { skill: 'Python', score: 92 },
  { skill: 'React', score: 78 },
  { skill: 'SQL', score: 85 },
  { skill: 'AWS', score: 70 },
];

function ResultsDashboard() {
  return (
    <div className="page-container py-12">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900">Analysis Results</h1>
        <p className="mt-2 text-slate-600">
          Placeholder dashboard for parsed resume insights and skill scores.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card title="Candidate Summary">
          <dl className="space-y-3 text-sm">
            <div className="flex justify-between">
              <dt className="text-slate-500">Name</dt>
              <dd className="font-medium text-slate-900">Jane Doe</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-slate-500">Role</dt>
              <dd className="font-medium text-slate-900">Software Engineer</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-slate-500">Experience</dt>
              <dd className="font-medium text-slate-900">5 years</dd>
            </div>
          </dl>
        </Card>

        <Card title="Skill Scores" description="Placeholder chart — Recharts integration">
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={skillData} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="skill" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="score" fill="#6366f1" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>
    </div>
  );
}

export default ResultsDashboard;
