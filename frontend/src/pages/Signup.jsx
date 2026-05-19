import React, { useState } from 'react';
import { Card, Form, Input, Button, message } from 'antd';
import { UserOutlined, LockOutlined, PhoneOutlined, SolutionOutlined, ShopOutlined } from '@ant-design/icons';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { BASE_URL } from '../services/api';

const Signup = () => {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const onFinish = async (values) => {
    setLoading(false);
    try {
      setLoading(true);
      await axios.post(`${BASE_URL}/staff/signup/`, {
        username: values.username,
        password: values.password,
        first_name: values.first_name,
        phone: values.phone,
        barbershop_name: values.barbershop_name,
      });

      message.success("Sartarosh hisobi muvaffaqiyatli yaratildi! Tizimga kirishingiz mumkin.");
      navigate('/login');
    } catch (error) {
      if (error.response && error.response.data) {
        const errors = error.response.data;
        Object.keys(errors).forEach((key) => {
          message.error(`${key}: ${errors[key]}`);
        });
      } else {
        message.error("Ro'yxatdan o'tishda xatolik yuz berdi. Iltimos qaytadan urinib ko'ring.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <Card className="w-full max-w-md shadow-2xl rounded-2xl border-0 bg-white">
        <div className="text-center mb-8">
          <span className="text-5xl">💈</span>
          <h2 className="mt-4 text-3xl font-extrabold text-gray-900 tracking-tight">CRM Ro'yxatdan o'tish</h2>
          <p className="mt-2 text-sm text-gray-600">
            Sartarosh yoki filial boshqaruvchisi sifatida ro'yxatdan o'ting
          </p>
        </div>

        <Form
          name="signup"
          onFinish={onFinish}
          size="large"
          layout="vertical"
          requiredMark={false}
        >
          <Form.Item
            name="first_name"
            label="Ism (Sartarosh ismi)"
            rules={[{ required: true, message: 'Iltimos ismingizni kiriting!' }]}
          >
            <Input prefix={<SolutionOutlined className="text-gray-400" />} placeholder="Masalan: Jasur" />
          </Form.Item>

          <Form.Item
            name="phone"
            label="Telefon raqamingiz"
            rules={[{ required: true, message: 'Iltimos telefon raqamingizni kiriting!' }]}
          >
            <Input prefix={<PhoneOutlined className="text-gray-400" />} placeholder="+998901234567" />
          </Form.Item>

          <Form.Item
            name="barbershop_name"
            label="Sartaroshxona nomi (Yangi filial ochish)"
            rules={[{ required: false }]}
          >
            <Input prefix={<ShopOutlined className="text-gray-400" />} placeholder="Masalan: Masters Barbershop (Ixtiyoriy)" />
          </Form.Item>

          <Form.Item
            name="username"
            label="Tizim uchun login"
            rules={[{ required: true, message: 'Iltimos kirish uchun foydalanuvchi nomini kiriting!' }]}
          >
            <Input prefix={<UserOutlined className="text-gray-400" />} placeholder="Foydalanuvchi nomi" />
          </Form.Item>

          <Form.Item
            name="password"
            label="Xavfsiz parol"
            rules={[
              { required: true, message: 'Iltimos parolingizni kiriting!' },
              { min: 6, message: "Parol kamida 6 ta belgidan iborat bo'lishi kerak!" }
            ]}
          >
            <Input.Password prefix={<LockOutlined className="text-gray-400" />} placeholder="Parol" />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              className="w-full bg-indigo-600 hover:bg-indigo-500 rounded-lg h-12 text-lg font-medium"
              loading={loading}
            >
              Sartarosh sifatida ro'yxatdan o'tish
            </Button>
          </Form.Item>
        </Form>

        <div className="text-center mt-6">
          <span className="text-gray-600">Sizda allaqachon profil bormi? </span>
          <Link to="/login" className="text-indigo-600 font-semibold hover:text-indigo-500">
            Tizimga kirish
          </Link>
        </div>
      </Card>
    </div>
  );
};

export default Signup;
