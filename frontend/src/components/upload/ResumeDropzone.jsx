import { useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { CheckCircle2, FileText, Upload, X } from 'lucide-react';

const MAX_SIZE_MB = 5;
const ACCEPTED_TYPES = ['application/pdf'];
const ACCEPTED_EXT = /\.pdf$/i;

function validateFile(file) {
  if (!file) return 'No file selected.';
  const validType = ACCEPTED_TYPES.includes(file.type) || ACCEPTED_EXT.test(file.name);
  if (!validType) return 'Please upload a PDF file.';
  if (file.size > MAX_SIZE_MB * 1024 * 1024) return `File must be under ${MAX_SIZE_MB} MB.`;
  return null;
}

function ResumeDropzone({ file, onFileSelect }) {
  const inputRef = useRef(null);
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState('');

  const handleFile = (selected) => {
    const validationError = validateFile(selected);
    if (validationError) {
      setError(validationError);
      return;
    }
    setError('');
    onFileSelect?.(selected);
  };

  const openPicker = () => inputRef.current?.click();

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    handleFile(e.dataTransfer.files?.[0]);
  };

  const handleChange = (e) => {
    handleFile(e.target.files?.[0]);
    e.target.value = '';
  };

  const clearFile = (e) => {
    e.stopPropagation();
    setError('');
    onFileSelect?.(null);
    if (inputRef.current) inputRef.current.value = '';
  };

  return (
    <div>
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.45, delay: 0.1 }}
        role="button"
        tabIndex={0}
        onClick={openPicker}
        onKeyDown={(e) => e.key === 'Enter' && openPicker()}
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        className={`tg-dropzone ${dragOver ? 'tg-dropzone-active' : ''}`}
      >
        {file ? (
          <>
            <div className="tg-icon-box">
              <CheckCircle2 className="h-5 w-5 text-emerald-500" />
            </div>
            <div className="mt-4 flex max-w-full items-center gap-2 px-2">
              <FileText className="h-4 w-4 shrink-0 text-violet-500" />
              <p className="truncate text-[15px] font-medium tg-heading">{file.name}</p>
              <button
                type="button"
                onClick={clearFile}
                className="ml-1 rounded-md p-1 tg-muted hover:text-rose-500"
                aria-label="Remove file"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <p className="mt-2 text-[13px] tg-muted">
              {(file.size / 1024 / 1024).toFixed(2)} MB · Click to replace
            </p>
          </>
        ) : (
          <>
            <div className="tg-icon-box">
              <Upload className="h-5 w-5 text-violet-500" />
            </div>
            <p className="mt-5 text-center text-[15px] tg-subtle">
              Drop your resume here, or{' '}
              <span className="font-medium text-violet-600 dark:text-violet-400">browse</span>
            </p>
            <p className="mt-2 text-center text-[13px] tg-muted">
              PDF only, up to {MAX_SIZE_MB} MB · Parsed locally
            </p>
          </>
        )}

        <input
          ref={inputRef}
          type="file"
          accept=".pdf,application/pdf"
          className="sr-only"
          onChange={handleChange}
        />
      </motion.div>

      {error && (
        <p className="mt-2 text-[13px] text-rose-600 dark:text-rose-400">{error}</p>
      )}

      <div className="tg-surface-muted mt-3 px-4 py-3">
        <p className="text-[13px] leading-relaxed tg-muted">
          <span className="font-semibold tg-subtle">Tip</span>
          {' · '}
          For best results, upload an ATS-friendly PDF without images, tables, or columns.
        </p>
      </div>
    </div>
  );
}

export default ResumeDropzone;
