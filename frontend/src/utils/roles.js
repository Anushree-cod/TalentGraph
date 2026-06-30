export const ROLES = {
  RECRUITER: 'recruiter',
  APPLICANT: 'applicant',
};

export function roleFromIsRecruiter(isRecruiter) {
  return isRecruiter ? ROLES.RECRUITER : ROLES.APPLICANT;
}

export function getDashboardPath(role) {
  return role === ROLES.RECRUITER ? '/recruiter' : '/jobs';
}

export function isRecruiter(role) {
  return role === ROLES.RECRUITER;
}

export function isApplicant(role) {
  return role === ROLES.APPLICANT;
}
