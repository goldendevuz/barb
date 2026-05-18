import React, { useState } from 'react';
import { Card, Form, Input, Button, message, Checkbox } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/useStore';
import axios from 'axios';

const Login = () => {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuthStore();

  const onFinish = async (values) => {
    setLoading(true);
    try {
      const response = await axios.post('http://localhost:8000/api/login/', {
        username: values.username,
        password: values.password,
      });
      
      login(response.data.access, response.data.refresh);
      message.success('Tizimga muvaffaqiyatli kirdingiz!');
      navigate('/');
    } catch (error) {
      message.error('Login yoki parol noto\'g\'ri!');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <Card className="w-full max-w-md shadow-lg rounded-xl border-0">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-indigo-600 mb-2">🪒</h1>
          <h2 className="text-2xl font-semibold text-gray-800">Tizimga kirish</h2>
          <p className="text-gray-500">Barbershop CRM boshqaruv paneli</p>
        </div>

        <Form
          name="login"
          initialValues={{ remember: true }}
          onFinish={onFinish}
          size="large"
          layout="vertical"
        >
          <Form.Item
            name="username"
            rules={[{ required: true, message: 'Iltimos loginni kiriting!' }]}
          >
            <Input prefix={<UserOutlined className="text-gray-400" />} placeholder="Login (admin)" />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: 'Iltimos parolni kiriting!' }]}
          >
            <Input.Password prefix={<LockOutlined className="text-gray-400" />} placeholder="Parol (admin)" />
          </Form.Item>

          <div className="flex justify-between items-center mb-6">
            <Form.Item name="remember" valuePropName="checked" noStyle>
              <Checkbox>Eslab qolish</Checkbox>
            </Form.Item>
          </div>

          <Form.Item>
            <Button type="primary" htmlType="submit" className="w-full bg-indigo-600 hover:bg-indigo-500" loading={loading}>
              Kirish
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default Login;
