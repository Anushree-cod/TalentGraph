import { motion } from 'framer-motion';
import { Cell, Pie, PieChart, ResponsiveContainer } from 'recharts';

const defaultPipelineData = [
  { name: 'Shortlisted', value: 0, color: '#22c55e' },
  { name: 'Interviewing', value: 0, color: '#22d3ee' },
  { name: 'Rejected', value: 0, color: '#f43f5e' },
  { name: 'Applied', value: 0, color: '#8b5cf6' },
];

function PipelineDonutChart({ data }) {
  const chartData = data ?? defaultPipelineData;
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.25 }}
      className="tg-surface p-5 sm:p-6"
    >
      <p className="tg-label">Pipeline stages</p>

      <div className="mt-4 flex h-56 items-center justify-center sm:h-64">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              innerRadius="58%"
              outerRadius="82%"
              paddingAngle={3}
              dataKey="value"
              stroke="none"
            >
              {chartData.map((entry) => (
                <Cell key={entry.name} fill={entry.color} />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  );
}

export default PipelineDonutChart;
