import { useState } from 'react';
import { motion } from 'framer-motion';
import PageShell from '../components/layout/PageShell';
import ResumeDropzone from '../components/upload/ResumeDropzone';
import JobDetailsForm from '../components/upload/JobDetailsForm';
import JobDescriptionField, { DEFAULT_JD } from '../components/upload/JobDescriptionField';
import UploadActionBar from '../components/upload/UploadActionBar';

function UploadResumePage() {
  const [resumeFile, setResumeFile] = useState(null);
  const [jobTitle, setJobTitle] = useState('Senior Frontend Engineer');
  const [company, setCompany] = useState('TalentGraph Labs');
  const [jobDescription, setJobDescription] = useState(DEFAULT_JD);

  return (
    <PageShell>
      <main className="relative mx-auto max-w-5xl px-4 pb-16 pt-28 sm:px-6 sm:pt-32 lg:pb-20">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-10"
        >
          <p className="tg-label-wide">Step 1 of 3</p>
          <h1 className="mt-3 text-3xl font-bold tracking-tight tg-heading sm:text-4xl lg:text-[2.5rem] lg:leading-tight">
            Upload a resume, paste a job description.
          </h1>
          <p className="mt-4 max-w-2xl text-base leading-relaxed tg-body">
            We&apos;ll score the resume against the JD on ATS, skill match, and recruiter
            signals. You can adjust everything before running the analysis.
          </p>
        </motion.div>

        <div className="grid gap-4 lg:grid-cols-2 lg:gap-5">
          <ResumeDropzone file={resumeFile} onFileSelect={setResumeFile} />
          <JobDetailsForm
            jobTitle={jobTitle}
            company={company}
            onJobTitleChange={(e) => setJobTitle(e.target.value)}
            onCompanyChange={(e) => setCompany(e.target.value)}
          />
        </div>

        <div className="mt-4 space-y-4 sm:mt-5">
          <JobDescriptionField
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
          />
          <UploadActionBar hasResume={Boolean(resumeFile)} />
        </div>
      </main>
    </PageShell>
  );
}

export default UploadResumePage;
