import { motion } from 'framer-motion';
import { TrendingUp } from 'lucide-react';

const barHeights = [38, 58, 48, 72, 82, 62, 92];

function PipelineChart() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-40px' }}
      transition={{ duration: 0.5, delay: 0.15 }}
      className="rounded-2xl border border-slate-200 bg-slate-50 p-5 dark:border-white/[0.06] dark:bg-[#121214] sm:p-6"
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-[12px] font-medium tg-muted">
          <svg className="h-3.5 w-3.5" viewBox="0 0 16 16" fill="none" aria-hidden>
            <rect x="1" y="8" width="3" height="7" rx="1" fill="currentColor" opacity="0.5" />
            <rect x="6" y="5" width="3" height="10" rx="1" fill="currentColor" opacity="0.7" />
            <rect x="11" y="2" width="3" height="13" rx="1" fill="currentColor" />
          </svg>
          Weekly Pipeline
        </div>
        <div className="flex items-center gap-1 text-[12px] font-medium text-emerald-600 dark:text-emerald-400">
          <TrendingUp className="h-3.5 w-3.5" />
          +18%
        </div>
      </div>

      <div className="mt-6 flex h-36 items-end justify-between gap-2 sm:h-44 sm:gap-3">
        {barHeights.map((height, index) => (
          <motion.div
            key={index}
            initial={{ height: 0 }}
            whileInView={{ height: `${height}%` }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.2 + index * 0.06, ease: [0.22, 1, 0.36, 1] }}
            className="flex-1 rounded-lg bg-gradient-to-br from-violet-500 via-violet-400 to-cyan-400"
          />
        ))}
      </div>
    </motion.div>
  );
}

export default PipelineChart;
