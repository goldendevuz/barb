import React, { useState, useEffect } from 'react';
import { Table, Button, Space, Modal, Form, Input, InputNumber, message } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import api from '../services/api';

const Clients = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [form] = Form.useForm();

  const fetchClients = async () => {
    setLoading(true);
    try {
      const response = await api.get('/clients/');
      setData(response.data);
    } catch (error) {
      message.error("Xatolik yuz berdi");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchClients();
  }, []);

  const handleAdd = () => {
    setEditingId(null);
    form.resetFields();
    setIsModalVisible(true);
  };

  const handleEdit = (record) => {
    setEditingId(record.id);
    form.setFieldsValue(record);
    setIsModalVisible(true);
  };

  const handleDelete = async (id) => {
    try {
      await api.delete(`/clients/${id}/`);
      message.success("Mijoz o'chirildi");
      fetchClients();
    } catch (error) {
      message.error("Xatolik yuz berdi");
    }
  };

  const onFinish = async (values) => {
    try {
      if (editingId) {
        await api.put(`/clients/${editingId}/`, values);
        message.success("Mijoz yangilandi");
      } else {
        await api.post('/clients/', values);
        message.success("Yangi mijoz qo'shildi");
      }
      setIsModalVisible(false);
      fetchClients();
    } catch (error) {
      message.error("Xatolik yuz berdi");
    }
  };

  const columns = [
    { title: 'ID', dataIndex: 'id', key: 'id' },
    { title: 'Telegram ID', dataIndex: 'telegram_id', key: 'telegram_id' },
    { title: 'Ism', dataIndex: 'name', key: 'name' },
    { title: 'Telefon', dataIndex: 'phone', key: 'phone' },
    { 
      title: 'Qo\'shilgan sana', 
      dataIndex: 'created_at', 
      key: 'created_at',
      render: (date) => new Date(date).toLocaleDateString()
    },
    {
      title: 'Amallar',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button icon={<EditOutlined />} onClick={() => handleEdit(record)} type="primary" ghost />
          <Button icon={<DeleteOutlined />} onClick={() => {
            Modal.confirm({
              title: "O'chirishni tasdiqlaysizmi?",
              onOk: () => handleDelete(record.id)
            })
          }} danger />
        </Space>
      )
    }
  ];

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">Mijozlar</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd} className="bg-indigo-600">
          Qo'shish
        </Button>
      </div>
      
      <Table columns={columns} dataSource={data} rowKey="id" loading={loading} scroll={{ x: true }} />

      <Modal
        title={editingId ? "Mijozni tahrirlash" : "Yangi mijoz"}
        open={isModalVisible}
        onCancel={() => setIsModalVisible(false)}
        footer={null}
      >
        <Form form={form} layout="vertical" onFinish={onFinish}>
          <Form.Item name="telegram_id" label="Telegram ID (Raqam)" rules={[{ required: true }]}>
            <InputNumber className="w-full" />
          </Form.Item>
          <Form.Item name="name" label="Ism" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="phone" label="Telefon" rules={[{ required: false }]}>
            <Input />
          </Form.Item>
          <Form.Item className="mb-0 text-right">
            <Button onClick={() => setIsModalVisible(false)} className="mr-2">Bekor qilish</Button>
            <Button type="primary" htmlType="submit">Saqlash</Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Clients;
