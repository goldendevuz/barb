import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider, Button, Drawer } from 'antd';
import { MenuOutlined } from '@ant-design/icons';
import { useAuthStore } from './store/useStore';

// Components
import Sidebar from './components/Sidebar';

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

// Private Route Wrapper
const PrivateRoute = ({ children }) => {
  const { isAuthenticated } = useAuthStore();
  return isAuthenticated ? children : <Navigate to="/login" />;
};

const AppLayout = ({ children }) => {
  const [mobileVisible, setMobileVisible] = useState(false);

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
        open={mobileVisible}
        styles={{ body: { padding: 0 } }}
        width={250}
      >
        <Sidebar isMobile={true} closeDrawer={() => setMobileVisible(false)} />
      </Drawer>

      {/* Main Content */}
      <div className="flex-1 p-4 md:p-8 overflow-y-auto overflow-x-hidden">
        {children}
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
          
          <Route path="/" element={
            <PrivateRoute>
              <AppLayout><Dashboard /></AppLayout>
            </PrivateRoute>
          } />
          <Route path="/bookings" element={
            <PrivateRoute>
              <AppLayout><Bookings /></AppLayout>
            </PrivateRoute>
          } />
          <Route path="/barbers" element={
            <PrivateRoute>
              <AppLayout><Barbers /></AppLayout>
            </PrivateRoute>
          } />
          <Route path="/services" element={
            <PrivateRoute>
              <AppLayout><Services /></AppLayout>
            </PrivateRoute>
          } />
          <Route path="/clients" element={
            <PrivateRoute>
              <AppLayout><Clients /></AppLayout>
            </PrivateRoute>
          } />
          <Route path="/pricing" element={
            <PrivateRoute>
              <AppLayout><Pricing /></AppLayout>
            </PrivateRoute>
          } />
          
          <Route path="*" element={
            <PrivateRoute>
              <AppLayout><NotFound /></AppLayout>
            </PrivateRoute>
          } />
        </Routes>
      </BrowserRouter>
    </ConfigProvider>
  );
};


export default App;
