import { useState } from 'react';
import Navbar from '../components/common/Navbar';
import Footer from '../components/common/Footer';
import Sidebar from '../components/common/Sidebar';
import AnimatedOutlet from '../components/layout/AnimatedOutlet';

function MainLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex min-h-screen flex-col bg-slate-50 dark:bg-black">
      <Navbar onMenuToggle={() => setSidebarOpen((prev) => !prev)} />

      <div className="flex flex-1">
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

        <main className="flex flex-1 flex-col">
          <div className="flex-1">
            <AnimatedOutlet />
          </div>
          <Footer />
        </main>
      </div>
    </div>
  );
}

export default MainLayout;
