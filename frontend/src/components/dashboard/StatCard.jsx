import { motion } from 'framer-motion';
import { TrendingDown, TrendingUp } from 'lucide-react';

function StatCard({ label, value, change, trend, icon: Icon, iconBg, iconColor, index }) {
  const isUp = trend === 'up';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, delay: index * 0.08 }}
      whileHover={{ y: -2 }}
      className="tg-surface p-5"
    >
      <div className="flex items-start justify-between">
        <p className="tg-label">{label}</p>
        <div className={`flex h-8 w-8 items-center justify-center rounded-lg ${iconBg}`}>
          <Icon className={`h-4 w-4 ${iconColor}`} />
        </div>
      </div>
      <p className="mt-4 text-3xl font-bold tg-heading">{value}</p>
      <div
        className={`mt-2 flex items-center gap-1 text-[12px] font-medium ${
          isUp ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'
        }`}
      >
        {isUp ? (
          <TrendingUp className="h-3.5 w-3.5" />
        ) : (
          <TrendingDown className="h-3.5 w-3.5" />
        )}
        {change}
      </div>
    </motion.div>
  );
}

export default StatCard;
