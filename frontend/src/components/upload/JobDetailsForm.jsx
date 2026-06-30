import { motion } from 'framer-motion';
import { Briefcase, Building2 } from 'lucide-react';

function FormField({ label, icon: Icon, value, onChange, placeholder }) {
  return (
    <div>
      <label className="tg-label">{label}</label>
      <div className="relative mt-2">
        <Icon className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400 dark:text-zinc-500" />
        <input
          type="text"
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          className="tg-input !pl-10"
        />
      </div>
    </div>
  );
}

function JobDetailsForm({ jobTitle, company, onJobTitleChange, onCompanyChange }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, delay: 0.15 }}
      className="tg-surface flex h-full flex-col gap-5 p-5 sm:p-6"
    >
      <FormField
        label="Job Title"
        icon={Briefcase}
        value={jobTitle}
        onChange={onJobTitleChange}
        placeholder="Senior Frontend Engineer"
      />
      <FormField
        label="Company"
        icon={Building2}
        value={company}
        onChange={onCompanyChange}
        placeholder="TalentGraph Labs"
      />
    </motion.div>
  );
}

export default JobDetailsForm;
