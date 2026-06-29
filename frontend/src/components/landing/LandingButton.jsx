import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowRight } from 'lucide-react';

const variants = {
  primary: 'tg-primary-btn',
  secondary: 'tg-secondary-btn',
};

const MotionLink = motion(Link);

function LandingButton({
  to,
  variant = 'primary',
  showArrow = false,
  className = '',
  children,
  ...props
}) {
  return (
    <MotionLink
      to={to}
      whileHover={{ y: -1 }}
      whileTap={{ scale: 0.98 }}
      transition={{ duration: 0.15 }}
      className={`${variants[variant]} ${className}`}
      {...props}
    >
      {children}
      {showArrow && <ArrowRight className="h-4 w-4" />}
    </MotionLink>
  );
}

export default LandingButton;
