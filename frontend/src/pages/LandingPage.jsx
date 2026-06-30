import PageShell from '../components/layout/PageShell';
import HeroSection from '../components/landing/HeroSection';
import DashboardPreview from '../components/landing/DashboardPreview';
import FeaturesSection from '../components/landing/FeaturesSection';
import CTASection from '../components/landing/CTASection';
import LandingFooter from '../components/landing/LandingFooter';

function LandingPage() {
  return (
    <PageShell>
      <main className="relative">
        <HeroSection />
        <DashboardPreview />
        <FeaturesSection />
        <CTASection />
        <LandingFooter />
      </main>
    </PageShell>
  );
}

export default LandingPage;
