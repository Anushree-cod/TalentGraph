import { motion } from 'framer-motion';
import { ShieldCheck, Zap, Sparkles } from 'lucide-react';
import LandingButton from './LandingButton';

const highlights = [
  {
    icon: ShieldCheck,
    title: 'SOC 2 ready',
    description: 'Resumes processed in-region.',
    iconColor: 'text-sky-600 dark:text-sky-400',
    iconBg: 'bg-sky-500/10',
  },
  {
    icon: Zap,
    title: 'Under 8s / resume',
    description: 'Parsing + scoring + ranking.',
    iconColor: 'text-violet-600 dark:text-violet-400',
    iconBg: 'bg-violet-500/10',
  },
  {
    icon: Sparkles,
    title: 'Actionable AI suggestions',
    description: 'Line-level rewrites that ATS systems love.',
    iconColor: 'text-cyan-600 dark:text-cyan-400',
    iconBg: 'bg-cyan-500/10',
    wide: true,
  },
];

function CTASection() {
  return (
    <section className="mx-auto max-w-6xl px-4 pb-8 sm:px-6">
      <motion.div
        initial={{ opacity: 0, y: 32 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: '-60px' }}
        transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
        className="tg-cta-shell"
      >
        <div
          aria-hidden
          className="pointer-events-none absolute -right-20 -top-20 h-64 w-64 rounded-full bg-[radial-gradient(circle,rgba(124,58,237,0.12)_0%,transparent_70%)] dark:bg-[radial-gradient(circle,rgba(124,58,237,0.2)_0%,transparent_70%)]"
        />

        <div className="relative grid gap-10 lg:grid-cols-2 lg:gap-12">
          <div>
            <h2 className="text-3xl font-bold leading-tight tracking-tight tg-heading sm:text-4xl lg:text-[2.5rem] lg:leading-[1.15]">
              Stop reading resumes.
              <br />
              <span className="bg-gradient-to-r from-violet-600 to-cyan-500 bg-clip-text text-transparent dark:from-violet-400 dark:to-cyan-400">
                Start ranking them.
              </span>
            </h2>
            <p className="mt-5 max-w-md text-base leading-relaxed tg-body">
              Upload a JD and a stack of resumes. TalentGraph ranks every candidate by
              fit and shows you exactly why.
            </p>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <LandingButton to="/upload" showArrow>
                Analyze Resume
              </LandingButton>
              <LandingButton to="/recruiter" variant="secondary">
                View Dashboard
              </LandingButton>
            </div>
          </div>

          <div className="grid gap-3 sm:grid-cols-2">
            {highlights.map(({ icon: Icon, title, description, iconColor, iconBg, wide }, index) => (
              <motion.div
                key={title}
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: 0.1 + index * 0.08 }}
                whileHover={{ scale: 1.01 }}
                className={`tg-surface-inset p-5 ${wide ? 'sm:col-span-2' : ''}`}
              >
                <div className={`mb-4 inline-flex h-9 w-9 items-center justify-center rounded-lg ${iconBg}`}>
                  <Icon className={`h-4 w-4 ${iconColor}`} />
                </div>
                <h3 className="text-[15px] font-semibold tg-heading">{title}</h3>
                <p className="mt-1.5 text-sm tg-muted">{description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </motion.div>
    </section>
  );
}

export default CTASection;
