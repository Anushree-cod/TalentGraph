import { motion } from 'framer-motion';
import { Crosshair, Sparkles, Activity, ArrowUp } from 'lucide-react';
import MetricCard from './MetricCard';
import PipelineChart from './PipelineChart';

const avatarColors = ['bg-violet-500', 'bg-sky-400', 'bg-orange-400', 'bg-cyan-400'];
const skillTags = ['React', 'TS', 'GQL', 'K8s'];

function DashboardPreview() {
  return (
    <section className="relative mx-auto mt-16 w-full max-w-5xl px-4 sm:mt-20 sm:px-6 lg:mt-24">
      <motion.div
        initial={{ opacity: 0, y: 40 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: '-60px' }}
        transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
        className="relative"
      >
        <div
          aria-hidden
          className="pointer-events-none absolute -inset-x-8 bottom-0 top-1/4 bg-[radial-gradient(ellipse_at_center,rgba(124,58,237,0.08)_0%,rgba(99,102,241,0.04)_45%,transparent_70%)] dark:bg-[radial-gradient(ellipse_at_center,rgba(124,58,237,0.15)_0%,rgba(99,102,241,0.06)_45%,transparent_70%)]"
        />

        <div className="relative overflow-hidden rounded-t-2xl border border-slate-200 bg-slate-100 shadow-lg dark:border-white/10 dark:bg-[#0a0a0b] dark:shadow-dashboard-window">
          <div className="flex items-center justify-between border-b border-slate-200 bg-white px-4 py-3 dark:border-white/[0.06] dark:bg-[#111111] sm:px-5">
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-1.5">
                <span className="h-2.5 w-2.5 rounded-full bg-[#ff5f57]" />
                <span className="h-2.5 w-2.5 rounded-full bg-[#febc2e]" />
                <span className="h-2.5 w-2.5 rounded-full bg-[#28c840]" />
              </div>
              <div className="hidden rounded-md border border-slate-200 bg-slate-50 px-3 py-1 dark:border-white/[0.06] dark:bg-black/40 sm:block">
                <span className="font-mono text-[11px] tg-muted">
                  talentgraph.app/dashboard
                </span>
              </div>
            </div>
            <span className="text-[10px] font-medium uppercase tracking-[0.2em] tg-muted">
              Recruiter View
            </span>
          </div>

          <div className="space-y-3 bg-white p-4 dark:bg-transparent sm:space-y-4 sm:p-6">
            <div className="grid gap-3 sm:grid-cols-3 sm:gap-4">
              <MetricCard icon={Crosshair} label="Avg ATS Score">
                <div className="mt-3 flex items-baseline gap-2">
                  <span className="bg-gradient-to-r from-violet-600 to-indigo-500 bg-clip-text text-4xl font-bold text-transparent dark:from-violet-300 dark:to-indigo-300 sm:text-5xl">
                    87
                  </span>
                  <span className="flex items-center gap-0.5 text-[12px] font-medium text-emerald-600 dark:text-emerald-400">
                    <ArrowUp className="h-3 w-3" />
                    4.2%
                  </span>
                </div>
                <div className="tg-progress-track mt-4 h-1.5">
                  <motion.div
                    initial={{ width: 0 }}
                    whileInView={{ width: '87%' }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.8, delay: 0.3, ease: 'easeOut' }}
                    className="h-full rounded-full bg-gradient-to-r from-violet-500 to-cyan-400"
                  />
                </div>
              </MetricCard>

              <MetricCard icon={Sparkles} label="Top Matches">
                <div className="mt-3 flex items-baseline gap-1">
                  <span className="text-4xl font-bold tg-heading sm:text-5xl">12</span>
                  <span className="text-lg tg-muted">/ 24</span>
                </div>
                <div className="mt-4 flex items-center">
                  <div className="flex -space-x-2">
                    {avatarColors.map((color, i) => (
                      <div
                        key={color}
                        className={`h-7 w-7 rounded-full border-2 border-slate-50 dark:border-[#121214] ${color}`}
                        style={{ zIndex: avatarColors.length - i }}
                      />
                    ))}
                  </div>
                  <span className="ml-2 rounded-full bg-slate-900 px-2 py-0.5 text-[11px] font-medium text-white dark:bg-black">
                    +20
                  </span>
                </div>
              </MetricCard>

              <MetricCard icon={Activity} label="Skill Match">
                <p className="mt-3 text-4xl font-bold tg-heading sm:text-5xl">94%</p>
                <div className="mt-4 flex flex-wrap gap-1.5">
                  {skillTags.map((tag) => (
                    <span
                      key={tag}
                      className="rounded-md border border-slate-200 bg-white px-2 py-1 text-[11px] font-medium text-slate-600 dark:border-white/[0.08] dark:bg-white/[0.04] dark:text-zinc-300"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </MetricCard>
            </div>

            <PipelineChart />
          </div>
        </div>
      </motion.div>

      <motion.p
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="mt-10 text-center text-[11px] font-medium uppercase tracking-[0.25em] tg-muted"
      >
        Trusted by recruiters at
      </motion.p>
    </section>
  );
}

export default DashboardPreview;
