const USERS_KEY = 'talentgraph-users';
const SESSION_KEY = 'talentgraph-session';

function readUsers() {
  try {
    return JSON.parse(localStorage.getItem(USERS_KEY) || '[]');
  } catch {
    return [];
  }
}

function writeUsers(users) {
  localStorage.setItem(USERS_KEY, JSON.stringify(users));
}

export function signUp({ name, email, password, company }) {
  const users = readUsers();
  const normalizedEmail = email.trim().toLowerCase();

  if (users.some((user) => user.email === normalizedEmail)) {
    throw new Error('An account with this email already exists.');
  }

  const user = {
    id: crypto.randomUUID(),
    name: name.trim(),
    email: normalizedEmail,
    password,
    company: company?.trim() || '',
    createdAt: new Date().toISOString(),
  };

  users.push(user);
  writeUsers(users);
  localStorage.setItem(SESSION_KEY, JSON.stringify({ id: user.id, email: user.email, name: user.name }));

  return { id: user.id, name: user.name, email: user.email };
}

export function signIn({ email, password }) {
  const users = readUsers();
  const normalizedEmail = email.trim().toLowerCase();
  const user = users.find((u) => u.email === normalizedEmail && u.password === password);

  if (!user) {
    throw new Error('Invalid email or password.');
  }

  localStorage.setItem(SESSION_KEY, JSON.stringify({ id: user.id, email: user.email, name: user.name }));
  return { id: user.id, name: user.name, email: user.email };
}

export function signOut() {
  localStorage.removeItem(SESSION_KEY);
}

export function getSession() {
  try {
    return JSON.parse(localStorage.getItem(SESSION_KEY) || 'null');
  } catch {
    return null;
  }
}
