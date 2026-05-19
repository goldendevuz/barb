import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Statistic, Spin, Alert, Table, Button, Modal, Form, Input, message } from 'antd';
import { 
  DollarOutlined, 
  CalendarOutlined, 
  UserOutlined, 
  RiseOutlined,
  ShopOutlined,
  PlusOutlined,
  EnvironmentOutlined
} from '@ant-design/icons';
import api from '../services/api';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [isSuperUser, setIsSuperUser] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Superuser Branch Management
  const [branches, setBranches] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [form] = Form.useForm();
  const [submitting, setSubmitting] = useState(false);

  const loadDashboardData = async () => {
    setLoading(true);
    setError(null);
    try {
      // 1. First attempt to load global superuser stats
      const adminResponse = await api.get('/admin/global-stats/');
      setStats(adminResponse.data);
      setIsSuperUser(true);
      
      // Load branches for superuser management
      const branchRes = await api.get('/barbershops/');
      setBranches(branchRes.data.results || branchRes.data);
    } catch (err) {
      // 2. If forbidden, fall back to standard barber/branch stats
      if (err.response && err.response.status === 403) {
        try {
          const barberResponse = await api.get('/dashboard-stats/');
          setStats(barberResponse.data);
          setIsSuperUser(false);
        } catch (barberErr) {
          setError("Ma'lumotlarni yuklashda xatolik yuz berdi");
        }
      } else {
        setError("Boshqaruv paneli yuklanmadi. Aloqani tekshiring.");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const handleAddBranch = async (values) => {
    setSubmitting(true);
    try {
      await api.post('/barbershops/', {
        name: values.name,
        address: values.address,
        latitude: parseFloat(values.latitude) || 41.278385,
        longitude: parseFloat(values.longitude) || 69.202356
      });
      message.success("Yangi sartaroshxona filiali muvaffaqiyatli qo'shildi!");
      setIsModalOpen(false);
      form.resetFields();
      loadDashboardData();
    } catch (err) {
      message.error("Filial qo'shishda xatolik yuz berdi.");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <div className="flex justify-center items-center h-full min-h-[400px]"><Spin size="large" /></div>;
  if (error) return <Alert message="Xatolik" description={error} type="error" showIcon className="m-4" />;

  // Superuser Branch Table Columns
  const columns = [
    { title: 'Filial nomi', dataIndex: 'name', key: 'name', render: text => <strong>{text}</strong> },
    { title: 'Manzili', dataIndex: 'address', key: 'address' },
    { title: 'Kenglik (Latitude)', dataIndex: 'latitude', key: 'latitude', render: val => val || "41.278385" },
    { title: 'Uzunlik (Longitude)', dataIndex: 'longitude', key: 'longitude', render: val => val || "69.202356" }
  ];

  return (
    <div className="p-1 md:p-4">
      {/* Dynamic Header */}
      <div className="flex justify-between items-center mb-8 flex-wrap gap-4">
        <div>
          <h2 className="text-3xl font-extrabold text-gray-900 tracking-tight">
            {isSuperUser ? "🌍 Global SaaS Tizim Boshqaruvi" : "🪒 Filial Boshqaruv Paneli"}
          </h2>
          <p className="text-gray-500 text-sm mt-1">
            {isSuperUser ? "Tizimdagi barcha filiallar, sartaroshlar va to'lovlar statistikasi" : "Sizga tegishli sartaroshxona va ish faoliyati hisoboti"}
          </p>
        </div>
        
        {isSuperUser && (
          <Button 
            type="primary" 
            icon={<PlusOutlined />} 
            size="large"
            className="bg-indigo-600 hover:bg-indigo-500 rounded-lg"
            onClick={() => setIsModalOpen(true)}
          >
            Yangi Filial Qo'shish
          </Button>
        )}
      </div>
      
      {/* ── SUPERUSER PANEL ── */}
      {isSuperUser ? (
        <>
          <Row gutter={[20, 20]} className="mb-10">
            <Col xs={24} sm={12} lg={6}>
              <Card bordered={false} className="shadow-md hover:shadow-lg transition-all duration-300 rounded-xl border-l-4 border-l-blue-600 bg-white">
                <Statistic
                  title="Tizim filiallari"
                  value={stats?.total_branches}
                  prefix={<ShopOutlined className="text-blue-600 mr-2" />}
                />
              </Card>
            </Col>
            
            <Col xs={24} sm={12} lg={6}>
              <Card bordered={false} className="shadow-md hover:shadow-lg transition-all duration-300 rounded-xl border-l-4 border-l-green-600 bg-white">
                <Statistic
                  title="Jami sartaroshlar"
                  value={stats?.total_barbers}
                  prefix={<UserOutlined className="text-green-600 mr-2" />}
                />
              </Card>
            </Col>
            
            <Col xs={24} sm={12} lg={6}>
              <Card bordered={false} className="shadow-md hover:shadow-lg transition-all duration-300 rounded-xl border-l-4 border-l-purple-600 bg-white">
                <Statistic
                  title="Jami mijozlar"
                  value={stats?.total_clients}
                  prefix={<RiseOutlined className="text-purple-600 mr-2" />}
                />
              </Card>
            </Col>
            
            <Col xs={24} sm={12} lg={6}>
              <Card bordered={false} className="shadow-md hover:shadow-lg transition-all duration-300 rounded-xl border-l-4 border-l-indigo-600 bg-white">
                <Statistic
                  title="SaaS Umumiy Daromadi"
                  value={stats?.total_revenue}
                  suffix="so'm"
                  prefix={<DollarOutlined className="text-indigo-600 mr-2" />}
                />
              </Card>
            </Col>
          </Row>

          <Card className="shadow-md rounded-2xl border-0 p-4 bg-white" title={<h3 className="text-lg font-bold text-gray-800 m-0">🏢 Mavjud Sartaroshxona Filiallari</h3>}>
            <Table 
              dataSource={branches} 
              columns={columns} 
              rowKey="id" 
              pagination={{ pageSize: 5 }}
              className="mt-2"
            />
          </Card>
        </>
      ) : (
        // ── STANDARD BARBER PANEL ──
        <>
          <Row gutter={[20, 20]} className="mb-10">
            <Col xs={24} sm={12} lg={6}>
              <Card bordered={false} className="shadow-md hover:shadow-lg transition-all duration-300 rounded-xl border-l-4 border-l-blue-500 bg-white">
                <Statistic
                  title="Bugungi bandliklar"
                  value={stats?.today_bookings_count}
                  prefix={<CalendarOutlined className="text-blue-500 mr-2" />}
                />
              </Card>
            </Col>
            
            <Col xs={24} sm={12} lg={6}>
              <Card bordered={false} className="shadow-md hover:shadow-lg transition-all duration-300 rounded-xl border-l-4 border-l-green-500 bg-white">
                <Statistic
                  title="Bugungi daromad"
                  value={stats?.today_income}
                  suffix="so'm"
                  prefix={<DollarOutlined className="text-green-500 mr-2" />}
                />
              </Card>
            </Col>
            
            <Col xs={24} sm={12} lg={6}>
              <Card bordered={false} className="shadow-md hover:shadow-lg transition-all duration-300 rounded-xl border-l-4 border-l-purple-500 bg-white">
                <Statistic
                  title="Oylik jami daromad"
                  value={stats?.monthly_income}
                  suffix="so'm"
                  prefix={<RiseOutlined className="text-purple-500 mr-2" />}
                />
              </Card>
            </Col>
            
            <Col xs={24} sm={12} lg={6}>
              <Card bordered={false} className="shadow-md hover:shadow-lg transition-all duration-300 rounded-xl border-l-4 border-l-orange-500 bg-white">
                <Statistic
                  title="Faol usta hamkasblar"
                  value={stats?.active_barbers}
                  prefix={<UserOutlined className="text-orange-500 mr-2" />}
                />
              </Card>
            </Col>
          </Row>

          <Card className="shadow-md rounded-2xl border-0 p-6 bg-white" title={<h3 className="text-lg font-bold text-gray-800 m-0">Tezkor Boshqaruv</h3>}>
            <p className="text-gray-500">Bugungi buyurtmalarni tekshirish yoki xizmatlarni yangilash uchun chap paneldagi tegishli sahifalarga o'ting.</p>
          </Card>
        </>
      )}

      {/* Superuser New Branch Modal */}
      <Modal
        title="🏢 Yangi filial (Barbershop) qo'shish"
        open={isModalOpen}
        onCancel={() => setIsModalOpen(false)}
        onOk={() => form.submit()}
        confirmLoading={submitting}
        okText="Qo'shish"
        cancelText="Bekor qilish"
        destroyOnClose
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleAddBranch}
          className="mt-4"
        >
          <Form.Item
            name="name"
            label="Filial nomi"
            rules={[{ required: true, message: 'Iltimos filial nomini kiriting!' }]}
          >
            <Input placeholder="Masalan: Chilonzor Elite Branch" />
          </Form.Item>

          <Form.Item
            name="address"
            label="Filial manzili"
            rules={[{ required: true, message: 'Iltimos filial manzilini kiriting!' }]}
          >
            <Input placeholder="Masalan: Lutfiy ko'chasi, 12-uy" />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="latitude"
                label="Kenglik (Latitude)"
                initialValue="41.278385"
              >
                <Input prefix={<EnvironmentOutlined />} placeholder="41.278385" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="longitude"
                label="Uzunlik (Longitude)"
                initialValue="69.202356"
              >
                <Input prefix={<EnvironmentOutlined />} placeholder="69.202356" />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>
    </div>
  );
};

export default Dashboard;
