import LandingNavbar from '../landing/LandingNavbar';

function PageShell({ children }) {
  return (
    <div className="tg-page">
      <div aria-hidden className="tg-page-glow" />
      <LandingNavbar />
      {children}
    </div>
  );
}

export default PageShell;
