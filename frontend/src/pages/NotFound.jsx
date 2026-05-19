import React from 'react';
import { Result, Button } from 'antd';
import { useNavigate } from 'react-router-dom';
import { HomeOutlined } from '@ant-design/icons';

const NotFound = () => {
  const navigate = useNavigate();

  return (
    <div className="flex items-center justify-center min-h-[80vh] px-4">
      <Result
        status="404"
        title={<span className="text-8xl font-extrabold text-indigo-600 drop-shadow-md">404</span>}
        subTitle={
          <div className="mt-4">
            <h3 className="text-2xl font-bold text-gray-800">Sahifa topilmadi!</h3>
            <p className="text-gray-500 mt-2 max-w-md mx-auto">
              Uzr, siz qidirayotgan sahifa mavjud emas yoki o'chirilgan bo'lishi mumkin. 
              Iltimos, manzilni to'g'riligini tekshiring.
            </p>
          </div>
        }
        extra={
          <Button 
            type="primary" 
            icon={<HomeOutlined />} 
            size="large"
            onClick={() => navigate('/')}
            className="bg-indigo-600 hover:bg-indigo-700 h-12 px-8 rounded-lg text-base font-medium transition-all shadow-md hover:shadow-lg"
          >
            Bosh sahifaga qaytish
          </Button>
        }
        className="bg-white p-12 md:p-16 rounded-2xl shadow-sm border border-gray-100 max-w-xl w-full text-center"
      />
    </div>
  );
};

export default NotFound;
