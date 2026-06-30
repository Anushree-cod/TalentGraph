import { Link } from 'react-router-dom';
import { Home } from 'lucide-react';
import Button from '../components/ui/Button';

function NotFound() {
  return (
    <div className="page-container flex min-h-[60vh] flex-col items-center justify-center py-12 text-center">
      <p className="text-6xl font-bold text-brand-600">404</p>
      <h1 className="mt-4 text-2xl font-bold text-slate-900">Page Not Found</h1>
      <p className="mt-2 max-w-md text-slate-600">
        The page you are looking for does not exist or has been moved.
      </p>
      <Button as={Link} to="/" className="mt-8">
        <Home className="mr-2 h-4 w-4" />
        Back to Home
      </Button>
    </div>
  );
}

export default NotFound;
