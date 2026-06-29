import { motion } from 'framer-motion';
import HeroBadge from './HeroBadge';
import LandingButton from './LandingButton';

const fadeUp = (delay = 0) => ({
  initial: { opacity: 0, y: 24 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.55, delay, ease: [0.22, 1, 0.36, 1] },
});

function HeroSection() {
  return (
    <section className="relative flex flex-col items-center px-4 pt-28 text-center sm:px-6 sm:pt-32 lg:pt-36">
      <HeroBadge>Built for modern talent teams</HeroBadge>

      <motion.h1
        {...fadeUp(0.15)}
        className="mt-8 max-w-4xl text-[2.5rem] font-bold leading-[1.1] tracking-tight tg-heading sm:text-5xl md:text-6xl lg:text-[4.25rem]"
      >
        Hire the right talent,
        <br />
        <span className="bg-gradient-to-r from-violet-500 via-violet-400 to-indigo-500 bg-clip-text text-transparent dark:from-violet-400 dark:via-violet-300 dark:to-indigo-400">
          10x faster.
        </span>
      </motion.h1>

      <motion.p
        {...fadeUp(0.25)}
        className="mt-6 max-w-2xl text-base leading-relaxed tg-body sm:text-lg sm:leading-8"
      >
        TalentGraph is the AI resume layer for serious recruiters. Score, match,
        and rank candidates against any job description — in seconds.
      </motion.p>

      <motion.div
        {...fadeUp(0.35)}
        className="mt-10 flex w-full max-w-md flex-col items-center justify-center gap-3 sm:max-w-none sm:flex-row"
      >
        <LandingButton to="/upload" showArrow>
          Analyze Resume
        </LandingButton>
        <LandingButton to="/recruiter" variant="secondary">
          Explore Dashboard
        </LandingButton>
      </motion.div>

      <motion.p {...fadeUp(0.45)} className="mt-6 text-[13px] tg-muted">
        No credit card · 14-day trial · GDPR-ready
      </motion.p>
    </section>
  );
}

export default HeroSection;
