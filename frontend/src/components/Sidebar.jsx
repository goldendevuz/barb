import React from 'react';
import { Layout, Menu } from 'antd';
import { 
  DashboardOutlined, 
  CalendarOutlined, 
  ScissorOutlined, 
  ShopOutlined, 
  UserOutlined,
  LogoutOutlined
} from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../store/useStore';

const { Sider } = Layout;

const Sidebar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const menuItems = [
    { key: '/', icon: <DashboardOutlined />, label: 'Boshqaruv' },
    { key: '/bookings', icon: <CalendarOutlined />, label: 'Buyurtmalar' },
    { key: '/barbers', icon: <ScissorOutlined />, label: 'Sartaroshlar' },
    { key: '/services', icon: <ShopOutlined />, label: 'Xizmatlar' },
    { key: '/clients', icon: <UserOutlined />, label: 'Mijozlar' },
    { type: 'divider' },
    { key: 'logout', icon: <LogoutOutlined />, label: 'Chiqish', onClick: handleLogout, danger: true },
  ];

  return (
    <Sider width={250} theme="light" className="h-screen shadow-md">
      <div className="p-5 flex items-center justify-center border-b border-gray-100">
        <h1 className="text-2xl font-bold text-indigo-600 tracking-wide m-0">🪒 BarbCRM</h1>
      </div>
      <Menu
        mode="inline"
        selectedKeys={[location.pathname]}
        items={menuItems}
        onClick={({ key }) => {
          if (key !== 'logout') navigate(key);
        }}
        className="mt-4 border-r-0"
      />
    </Sider>
  );
};

export default Sidebar;
