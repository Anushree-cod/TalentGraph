import { motion } from 'framer-motion';
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  XAxis,
  YAxis,
} from 'recharts';

const domainData = [
  { domain: 'FE', score: 92 },
  { domain: 'BE', score: 78 },
  { domain: 'ML', score: 85 },
  { domain: 'DevOps', score: 71 },
  { domain: 'Design', score: 88 },
];

function DomainBarChart() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
      className="tg-surface p-5 sm:p-6 lg:col-span-2"
    >
      <p className="tg-label">Average ATS · By domain</p>
      <p className="mt-1 text-[13px] tg-muted">Where your strongest candidates come from.</p>

      <div className="mt-6 h-56 sm:h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={domainData} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#a78bfa" />
                <stop offset="100%" stopColor="#3b82f6" />
              </linearGradient>
            </defs>
            <CartesianGrid
              strokeDasharray="3 3"
              className="stroke-slate-200 dark:stroke-white/10"
              vertical={false}
            />
            <XAxis
              dataKey="domain"
              tick={{ fill: '#94a3b8', fontSize: 12 }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              ticks={[25, 50, 75, 100]}
              tick={{ fill: '#94a3b8', fontSize: 12 }}
              axisLine={false}
              tickLine={false}
            />
            <Bar dataKey="score" fill="url(#barGradient)" radius={[6, 6, 0, 0]} barSize={40} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  );
}

export default DomainBarChart;
