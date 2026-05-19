import React, { useState, useEffect } from 'react';
import { Table, Button, Space, Modal, Form, Input, Switch, message } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import api from '../services/api';

const Barbers = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [form] = Form.useForm();

  const fetchBarbers = async () => {
    setLoading(true);
    try {
      const response = await api.get('/barbers/');
      setData(response.data);
    } catch (error) {
      message.error("Ma'lumot yuklashda xato!");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBarbers();
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
      await api.delete(`/barbers/${id}/`);
      message.success("Sartarosh o'chirildi");
      fetchBarbers();
    } catch (error) {
      message.error("Xatolik yuz berdi");
    }
  };

  const toggleActive = async (checked, record) => {
    try {
      await api.patch(`/barbers/${record.id}/`, { active: checked });
      message.success("Holat o'zgardi");
      fetchBarbers();
    } catch (error) {
      message.error("Xatolik!");
    }
  };

  const onFinish = async (values) => {
    try {
      if (editingId) {
        await api.put(`/barbers/${editingId}/`, values);
        message.success("Sartarosh yangilandi");
      } else {
        await api.post('/barbers/', values);
        message.success("Yangi sartarosh qo'shildi");
      }
      setIsModalVisible(false);
      fetchBarbers();
    } catch (error) {
      message.error("Xatolik yuz berdi");
    }
  };

  const columns = [
    { title: 'ID', dataIndex: 'id', key: 'id' },
    { title: 'Ism', dataIndex: 'name', key: 'name' },
    { title: 'Telefon', dataIndex: 'phone', key: 'phone' },
    { 
      title: 'Faol', 
      dataIndex: 'active', 
      key: 'active',
      render: (active, record) => (
        <Switch checked={active} onChange={(c) => toggleActive(c, record)} />
      )
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
        <h2 className="text-xl font-semibold">Sartaroshlar</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd} className="bg-indigo-600">
          Qo'shish
        </Button>
      </div>
      
      <Table columns={columns} dataSource={data} rowKey="id" loading={loading} scroll={{ x: true }} />

      <Modal
        title={editingId ? "Sartaroshni tahrirlash" : "Yangi sartarosh"}
        open={isModalVisible}
        onCancel={() => setIsModalVisible(false)}
        footer={null}
      >
        <Form form={form} layout="vertical" onFinish={onFinish} initialValues={{ active: true }}>
          <Form.Item name="name" label="Ism" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="phone" label="Telefon" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="active" label="Faol" valuePropName="checked">
            <Switch />
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

export default Barbers;
