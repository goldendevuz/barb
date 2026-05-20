import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { ConfigProvider, Button, Drawer } from 'antd';
import { MenuOutlined } from '@ant-design/icons';
import { useAuthStore } from './store/useStore';

// Components
import Sidebar from './components/Sidebar';
import api from './services/api';

// Pages
import Login from './pages/Login';
import Signup from './pages/Signup';
import Pricing from './pages/Pricing';
import Dashboard from './pages/Dashboard';
import Bookings from './pages/Bookings';
import Barbers from './pages/Barbers';
import Services from './pages/Services';
import Clients from './pages/Clients';
import NotFound from './pages/NotFound';

const ProtectedLayout = () => {
  const { isAuthenticated } = useAuthStore();
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return <AppLayout />;
};

const AppLayout = () => {
  const [mobileVisible, setMobileVisible] = useState(false);
  const [tgLink, setTgLink] = useState(null);
  const [showBanner, setShowBanner] = useState(false);

  React.useEffect(() => {
    const checkTgLink = async () => {
      try {
        const response = await api.get('/staff/telegram-link/');
        if (response.data && !response.data.is_linked) {
          setTgLink(response.data.link);
          setShowBanner(true);
        }
      } catch (err) {
        // Silently skip if superuser or no staff profile exists
      }
    };
    checkTgLink();
  }, []);

  return (
    <div className="flex h-screen overflow-hidden bg-gray-100 flex-col md:flex-row">
      {/* Mobile Header */}
      <div className="flex items-center justify-between p-4 bg-white border-b border-gray-200 md:hidden">
        <h1 className="text-xl font-bold text-indigo-600 tracking-wide m-0">🪒 BarbCRM</h1>
        <Button 
          type="text" 
          icon={<MenuOutlined style={{ fontSize: '20px' }} />} 
          onClick={() => setMobileVisible(true)} 
        />
      </div>

      {/* Desktop Sidebar */}
      <div className="hidden md:block">
        <Sidebar />
      </div>

      {/* Mobile Drawer Sidebar */}
      <Drawer
        title={<h1 className="text-xl font-bold text-indigo-600 tracking-wide m-0">🪒 BarbCRM</h1>}
        placement="left"
        onClose={() => setMobileVisible(false)}
        onOpenChange={(open) => setMobileVisible(open)}
        open={mobileVisible}
        styles={{ body: { padding: 0 } }}
        width={250}
      >
        <Sidebar isMobile={true} closeDrawer={() => setMobileVisible(false)} />
      </Drawer>

      {/* Main Content */}
      <div className="flex-1 p-4 md:p-8 overflow-y-auto overflow-x-hidden">
        {showBanner && tgLink && (
          <div className="bg-gradient-to-r from-amber-500 via-orange-500 to-red-500 text-white px-6 py-5 rounded-2xl shadow-lg mb-6 flex flex-col lg:flex-row items-center justify-between gap-4 border border-orange-400/20">
            <div className="flex items-center gap-4 text-center lg:text-left flex-col lg:flex-row">
              <span className="text-4xl">🔔</span>
              <div>
                <h4 className="font-extrabold text-lg m-0 text-white tracking-wide">
                  Mijozlar buyurtma qilganida real-vaqtda Telegram xabar olishni xohlaysizmi?
                </h4>
                <p className="text-sm text-orange-50 m-0 mt-1 opacity-90 font-medium">
                  Tizimda barcha yangi uchrashuvlarni bevosita Telegram bot orqali boshqarish uchun profilingizni bog'lang.
                </p>
              </div>
            </div>
            <a 
              href={tgLink} 
              target="_blank" 
              rel="noopener noreferrer" 
              className="no-underline inline-block whitespace-nowrap shrink-0"
            >
              <button className="bg-white hover:bg-orange-50 text-orange-600 font-extrabold px-6 py-3 rounded-xl border-none cursor-pointer shadow-md transition-all duration-300 transform hover:scale-105 active:scale-95 flex items-center gap-2 text-sm">
                ✈️ Telegram Botni Ulash
              </button>
            </a>
          </div>
        )}
        <Outlet />
      </div>
    </div>
  );
};


const App = () => {
  return (
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: '#4f46e5', // Tailwind Indigo 600
          borderRadius: 6,
        },
      }}
    >
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />

          <Route element={<ProtectedLayout />}>
            <Route index element={<Dashboard />} />
            <Route path="bookings" element={<Bookings />} />
            <Route path="barbers" element={<Barbers />} />
            <Route path="services" element={<Services />} />
            <Route path="clients" element={<Clients />} />
            <Route path="pricing" element={<Pricing />} />
            <Route path="*" element={<NotFound />} />
          </Route>

          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </ConfigProvider>
  );
};


export default App;
