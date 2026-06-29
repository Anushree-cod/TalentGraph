import { motion } from 'framer-motion';

const fadeUp = {
  initial: { opacity: 0, y: 20 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, margin: '-40px' },
  transition: { duration: 0.5, ease: [0.22, 1, 0.36, 1] },
};

function MetricCard({ icon: Icon, label, children, className = '' }) {
  return (
    <motion.div
      {...fadeUp}
      className={`rounded-2xl border border-slate-200 bg-slate-50 p-5 dark:border-white/[0.06] dark:bg-[#121214] sm:p-6 ${className}`}
    >
      <div className="flex items-center gap-2 text-[12px] font-medium tg-muted">
        <Icon className="h-3.5 w-3.5" />
        {label}
      </div>
      {children}
    </motion.div>
  );
}

export default MetricCard;
