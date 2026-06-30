import { ROLES } from '../utils/roles';

export const recruiterNavLinks = [
  { to: '/recruiter', label: 'Dashboard', end: true },
  { to: '/recruiter/post-job', label: 'Post Job' },
  { to: '/recruiter/candidates', label: 'View Candidates' },
  { to: '/recruiter/profile', label: 'Profile' },
];

export const applicantNavLinks = [
  { to: '/jobs', label: 'Available Jobs', end: true },
  { to: '/applications', label: 'My Applications' },
  { to: '/profile', label: 'My Profile' },
];

export const guestNavLinks = [
  { to: '/', label: 'Home', end: true },
];

export function getNavLinksForRole(role) {
  if (role === ROLES.RECRUITER) {
    return recruiterNavLinks;
  }
  if (role === ROLES.APPLICANT) {
    return applicantNavLinks;
  }
  return guestNavLinks;
}
