import { motion } from 'framer-motion';
import { ArrowRight } from 'lucide-react';

function UploadActionBar({ hasResume, onAnalyze, isSubmitting = false }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, delay: 0.25 }}
      className="flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center"
    >
      <p className="text-[13px] tg-muted">
        {hasResume
          ? 'Resume ready — click Run analysis to continue.'
          : 'Upload a resume first, then run the analysis.'}
      </p>
      {hasResume ? (
        <motion.div whileHover={{ y: -1 }} whileTap={{ scale: 0.98 }}>
          <button
            type="button"
            onClick={onAnalyze}
            disabled={isSubmitting}
            className="tg-cta-btn disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isSubmitting ? 'Starting analysis…' : 'Run analysis'}
            <ArrowRight className="h-4 w-4" />
          </button>
        </motion.div>
      ) : (
        <span className="tg-cta-btn cursor-not-allowed opacity-40" aria-disabled="true">
          Run analysis
          <ArrowRight className="h-4 w-4" />
        </span>
      )}
    </motion.div>
  );
}

export default UploadActionBar;
