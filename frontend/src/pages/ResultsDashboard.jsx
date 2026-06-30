import { useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
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
import { useAnalysis } from '../context/AnalysisContext';

function ResultsDashboard() {
  const navigate = useNavigate();
  const { analysisResult } = useAnalysis();

  useEffect(() => {
    if (!analysisResult) {
      navigate('/upload', { replace: true });
    }
  }, [analysisResult, navigate]);

  const candidate = analysisResult?.candidate || {};
  const matching = analysisResult?.matching || {};
  const ranking = analysisResult?.ranking || {};
  const job = analysisResult?.job || {};

  const skillData = useMemo(() => {
    const skills = analysisResult?.skills || candidate.skills || [];
    const matched = new Set((matching.matched_skills || []).map((skill) => skill.toLowerCase()));

    return skills.slice(0, 8).map((skill) => ({
      skill,
      score: matched.has(String(skill).toLowerCase())
        ? matching.match_score || 0
        : Math.max(20, (matching.match_score || 40) - 15),
    }));
  }, [analysisResult, candidate.skills, matching]);

  if (!analysisResult) {
    return null;
  }

  const displayName = candidate.headline || candidate.current_title || candidate.candidate_id || 'Candidate';
  const displayRole = job.title || candidate.current_title || '—';
  const displayExperience =
    candidate.years_experience != null ? `${candidate.years_experience} years` : '—';
  const matchSummary = matching.recommendation
    ? `${matching.recommendation} — ${matching.match_score ?? 0}% match`
    : analysisResult.message;

  return (
    <div className="page-container py-12">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900">Analysis Results</h1>
        <p className="mt-2 text-slate-600">{matchSummary}</p>
        {ranking.rank != null && (
          <p className="mt-1 text-sm text-slate-500">Rank: #{ranking.rank}</p>
        )}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card title="Candidate Summary">
          <dl className="space-y-3 text-sm">
            <div className="flex justify-between">
              <dt className="text-slate-500">Name</dt>
              <dd className="font-medium text-slate-900">{displayName}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-slate-500">Role</dt>
              <dd className="font-medium text-slate-900">{displayRole}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-slate-500">Experience</dt>
              <dd className="font-medium text-slate-900">{displayExperience}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-slate-500">Location</dt>
              <dd className="font-medium text-slate-900">{candidate.location || '—'}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-slate-500">Company</dt>
              <dd className="font-medium text-slate-900">{job.company || '—'}</dd>
            </div>
          </dl>
        </Card>

        <Card title="Skill Scores" description="Parsed skills scored against the job description">
          <div className="h-64">
            {skillData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={skillData} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="skill" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Bar dataKey="score" fill="#6366f1" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <p className="flex h-full items-center justify-center text-sm text-slate-500">
                No skills detected in the uploaded resume.
              </p>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}

export default ResultsDashboard;
