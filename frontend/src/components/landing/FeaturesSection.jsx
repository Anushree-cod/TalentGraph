import { motion } from 'framer-motion';
import {
  Scan,
  Key,
  Stethoscope,
  ListOrdered,
  Sparkles,
} from 'lucide-react';

const features = [
  {
    icon: Scan,
    title: 'ATS Analysis',
    description: 'Score every resume against ATS rules — format, parseability, density.',
    glow: 'shadow-[0_0_20px_rgba(56,189,248,0.12)] dark:shadow-[0_0_20px_rgba(56,189,248,0.15)]',
    iconBg: 'bg-sky-500/10 text-sky-600 dark:text-sky-400',
  },
  {
    icon: Key,
    title: 'Keyword Matching',
    description:
      'Side-by-side JD ↔ resume keyword overlap with confidence weighting.',
    glow: 'shadow-[0_0_20px_rgba(168,85,247,0.12)] dark:shadow-[0_0_20px_rgba(168,85,247,0.15)]',
    iconBg: 'bg-violet-500/10 text-violet-600 dark:text-violet-400',
  },
  {
    icon: Stethoscope,
    title: 'Skill Gap Detection',
    description: 'Spot critical missing skills before they cost you a great candidate.',
    glow: 'shadow-[0_0_20px_rgba(45,212,191,0.12)] dark:shadow-[0_0_20px_rgba(45,212,191,0.15)]',
    iconBg: 'bg-teal-500/10 text-teal-600 dark:text-teal-400',
  },
  {
    icon: ListOrdered,
    title: 'Candidate Ranking',
    description:
      'Auto-rank applicants by JD fit, ATS, experience and recruiter signals.',
    glow: 'shadow-[0_0_20px_rgba(251,191,36,0.12)] dark:shadow-[0_0_20px_rgba(251,191,36,0.15)]',
    iconBg: 'bg-amber-500/10 text-amber-600 dark:text-amber-400',
  },
  {
    icon: Sparkles,
    title: 'AI Suggestions',
    description: 'Actionable, line-level improvements that lift ATS scores 20%+.',
    glow: 'shadow-[0_0_20px_rgba(52,211,153,0.12)] dark:shadow-[0_0_20px_rgba(52,211,153,0.15)]',
    iconBg: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400',
  },
];

function FeatureCard({ icon: Icon, title, description, glow, iconBg, index }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-40px' }}
      transition={{ duration: 0.5, delay: index * 0.08 }}
      whileHover={{ scale: 1.01 }}
      className={`tg-feature-card ${glow}`}
    >
      <div className={`mb-5 inline-flex h-10 w-10 items-center justify-center rounded-xl ${iconBg}`}>
        <Icon className="h-5 w-5" strokeWidth={1.75} />
      </div>
      <h3 className="text-lg font-semibold tg-heading">{title}</h3>
      <p className="mt-2 text-sm leading-relaxed tg-body">{description}</p>
    </motion.div>
  );
}

function FeaturesSection() {
  return (
    <section className="mx-auto max-w-6xl px-4 py-24 sm:px-6 sm:py-32">
      <div className="grid gap-8 lg:grid-cols-2 lg:gap-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <p className="tg-label-wide">The recruiter stack</p>
          <h2 className="mt-4 text-3xl font-bold leading-tight tracking-tight tg-heading sm:text-4xl lg:text-[2.75rem] lg:leading-[1.15]">
            Everything you need to find the{' '}
            <span className="text-violet-600 dark:text-violet-400">signal</span> in a stack of
            resumes.
          </h2>
        </motion.div>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="text-base leading-relaxed tg-body lg:pt-8 lg:text-lg"
        >
          From parsing PDFs to ranking candidates, TalentGraph compresses a recruiter&apos;s
          week into a single, fast workflow.
        </motion.p>
      </div>

      <div className="mt-12 grid gap-4 sm:grid-cols-2 lg:mt-16">
        {features.slice(0, 2).map((feature, index) => (
          <FeatureCard key={feature.title} {...feature} index={index} />
        ))}
      </div>

      <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {features.slice(2).map((feature, index) => (
          <FeatureCard key={feature.title} {...feature} index={index + 2} />
        ))}
      </div>
    </section>
  );
}

export default FeaturesSection;
