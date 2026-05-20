import React from 'react';
import { Result, Button, Space } from 'antd';
import { useNavigate } from 'react-router-dom';
import { HomeOutlined, LoginOutlined } from '@ant-design/icons';
import { useAuthStore } from '../store/useStore';

const NotFound = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuthStore();

  return (
    <div className="flex items-center justify-center min-h-screen md:min-h-[80vh] px-4 bg-gray-50 md:bg-transparent">
      <Result
        status="404"
        title={<span className="text-8xl font-extrabold text-indigo-600 drop-shadow-md">404</span>}
        subTitle={
          <div>
            <h3 className="text-2xl font-bold text-gray-800">Sahifa topilmadi!</h3>
            <p className="text-gray-500 mt-2 max-w-md mx-auto">
              Uzr, siz qidirayotgan sahifa mavjud emas yoki o&apos;chirilgan bo&apos;lishi mumkin.
              Iltimos, manzilni to&apos;g&apos;riligini tekshiring.
            </p>
          </div>
        }
        extra={
          <Space wrap className="justify-center">
            {isAuthenticated ? (
              <Button
                type="primary"
                icon={<HomeOutlined />}
                size="large"
                onClick={() => navigate('/')}
                className="bg-indigo-600 hover:bg-indigo-700 h-12 px-8 rounded-lg text-base font-medium"
              >
                Bosh sahifaga qaytish
              </Button>
            ) : (
              <Button
                type="primary"
                icon={<LoginOutlined />}
                size="large"
                onClick={() => navigate('/login')}
                className="bg-indigo-600 hover:bg-indigo-700 h-12 px-8 rounded-lg text-base font-medium"
              >
                Tizimga kirish
              </Button>
            )}
          </Space>
        }
        className="bg-white p-12 md:p-16 rounded-2xl shadow-sm border border-gray-100 max-w-xl w-full text-center"
      />
    </div>
  );
};

export default NotFound;
