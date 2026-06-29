import { motion } from 'framer-motion';
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  XAxis,
  YAxis,
} from 'recharts';

const applicationsData = [
  { day: 'Mon', count: 12 },
  { day: 'Tue', count: 16 },
  { day: 'Wed', count: 14 },
  { day: 'Thu', count: 20 },
  { day: 'Fri', count: 28 },
  { day: 'Sat', count: 18 },
  { day: 'Sun', count: 8 },
];

function ApplicationsChart() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.3 }}
      className="tg-surface p-5 sm:p-6"
    >
      <p className="tg-label">Applications · Last 7 days</p>

      <div className="mt-6 h-52 sm:h-56">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={applicationsData} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#8b5cf6" stopOpacity={0.35} />
                <stop offset="100%" stopColor="#8b5cf6" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid
              strokeDasharray="3 3"
              className="stroke-slate-200 dark:stroke-white/10"
              vertical={false}
            />
            <XAxis
              dataKey="day"
              tick={{ fill: '#94a3b8', fontSize: 12 }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              ticks={[0, 7, 14, 21, 28]}
              tick={{ fill: '#94a3b8', fontSize: 12 }}
              axisLine={false}
              tickLine={false}
            />
            <Area
              type="monotone"
              dataKey="count"
              stroke="#a78bfa"
              strokeWidth={2}
              fill="url(#areaGradient)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  );
}

export default ApplicationsChart;
