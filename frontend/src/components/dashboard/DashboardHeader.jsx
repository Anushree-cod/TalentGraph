import { motion } from 'framer-motion';

function DashboardHeader() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="mb-8"
    >
      <p className="tg-label-wide">Pipeline overview</p>
      <h1 className="mt-3 text-3xl font-bold tracking-tight tg-heading sm:text-4xl">
        Recruiter{' '}
        <span className="bg-gradient-to-r from-violet-600 to-cyan-500 bg-clip-text text-transparent dark:from-violet-400 dark:to-cyan-400">
          Dashboard
        </span>
      </h1>
      <p className="mt-3 text-base tg-body">
        Live view of your active funnel. Click any candidate for the full profile.
      </p>
    </motion.div>
  );
}

export default DashboardHeader;
