import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import { useAuthStore } from './store/useStore';

// Components
import Sidebar from './components/Sidebar';

// Pages
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Bookings from './pages/Bookings';
import Barbers from './pages/Barbers';
import Services from './pages/Services';
import Clients from './pages/Clients';

// Private Route Wrapper
const PrivateRoute = ({ children }) => {
  const { isAuthenticated } = useAuthStore();
  return isAuthenticated ? children : <Navigate to="/login" />;
};

const AppLayout = ({ children }) => {
  return (
    <div className="flex min-h-screen bg-gray-100">
      <Sidebar />
      <div className="flex-1 p-8 overflow-y-auto">
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
          
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </BrowserRouter>
    </ConfigProvider>
  );
};

export default App;
