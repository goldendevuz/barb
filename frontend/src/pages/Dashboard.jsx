import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Statistic, Spin, Alert } from 'antd';
import { 
  DollarOutlined, 
  CalendarOutlined, 
  UserOutlined, 
  RiseOutlined 
} from '@ant-design/icons';
import api from '../services/api';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await api.get('/dashboard-stats/');
        setStats(response.data);
      } catch (err) {
        setError("Ma'lumotlarni yuklashda xatolik yuz berdi");
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  if (loading) return <div className="flex justify-center items-center h-full"><Spin size="large" /></div>;
  if (error) return <Alert message="Xatolik" description={error} type="error" showIcon />;

  return (
    <div>
      <h2 className="text-2xl font-semibold mb-6 text-gray-800">Umumiy ko'rsatkichlar</h2>
      
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card bordered={false} className="shadow-sm rounded-lg border-l-4 border-l-blue-500">
            <Statistic
              title="Bugungi buyurtmalar"
              value={stats?.today_bookings_count}
              prefix={<CalendarOutlined className="text-blue-500 mr-2" />}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card bordered={false} className="shadow-sm rounded-lg border-l-4 border-l-green-500">
            <Statistic
              title="Bugungi daromad"
              value={stats?.today_income}
              suffix="so'm"
              prefix={<DollarOutlined className="text-green-500 mr-2" />}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card bordered={false} className="shadow-sm rounded-lg border-l-4 border-l-purple-500">
            <Statistic
              title="Oylik daromad"
              value={stats?.monthly_income}
              suffix="so'm"
              prefix={<RiseOutlined className="text-purple-500 mr-2" />}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card bordered={false} className="shadow-sm rounded-lg border-l-4 border-l-orange-500">
            <Statistic
              title="Faol sartaroshlar"
              value={stats?.active_barbers}
              prefix={<UserOutlined className="text-orange-500 mr-2" />}
            />
          </Card>
        </Col>
      </Row>

      {/* Placeholder for charts or recent tables */}
      <div className="mt-8 bg-white p-6 rounded-lg shadow-sm">
        <h3 className="text-lg font-medium text-gray-800 mb-4">Tezkor amallar</h3>
        <p className="text-gray-500">Bu yerda yaqinda qo'shilgan buyurtmalar ro'yxati chiqadi...</p>
      </div>
    </div>
  );
};

export default Dashboard;
