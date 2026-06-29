import { motion } from 'framer-motion';

function HeroBadge({ children }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.1, ease: 'easeOut' }}
      className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-slate-100 px-4 py-1.5 dark:border-white/10 dark:bg-white/[0.04]"
    >
      <span className="h-1.5 w-1.5 rounded-full bg-violet-500 dark:bg-violet-400" />
      <span className="text-[13px] font-medium tg-body">{children}</span>
    </motion.div>
  );
}

export default HeroBadge;
