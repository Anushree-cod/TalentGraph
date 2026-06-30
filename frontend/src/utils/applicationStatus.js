const STATUS_LABELS = {
  applied: 'Under Review',
  analyzed: 'Under Review',
  shortlisted: 'Shortlisted',
  rejected: 'Rejected',
  interview: 'Interview Scheduled',
  interviewing: 'Interview Scheduled',
  selected: 'Selected',
};

export function getFriendlyStatus(status) {
  if (!status) {
    return 'Under Review';
  }
  return STATUS_LABELS[String(status).toLowerCase()] || status;
}
