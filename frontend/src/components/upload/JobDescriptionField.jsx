import { motion } from 'framer-motion';

const DEFAULT_JD =
  "We're hiring a Senior Frontend Engineer to lead our design system. Must have 5+ years with React, TypeScript, Tailwind, and Storybook. Familiarity with micro-frontends, GraphQL, A/B testing, and performance optimization is a strong plus.";

function JobDescriptionField({ value, onChange }) {
  const charCount = value.length;

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, delay: 0.2 }}
      className="tg-surface p-5 sm:p-6"
    >
      <div className="flex items-center justify-between">
        <span className="tg-label">Job Description</span>
        <span className="text-[12px] tg-muted">{charCount} chars</span>
      </div>
      <textarea
        value={value}
        onChange={onChange}
        rows={5}
        placeholder={DEFAULT_JD}
        className="tg-textarea mt-4"
      />
    </motion.div>
  );
}

export { DEFAULT_JD };
export default JobDescriptionField;
