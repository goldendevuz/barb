import React, { useState, useEffect } from 'react';
import { Table, Tag, Button, Space, message, Modal, Form, InputNumber, Select, DatePicker, TimePicker } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import moment from 'moment';
import api from '../services/api';

const { Option } = Select;

const Bookings = () => {
  const [data, setData] = useState([]);
  const [clients, setClients] = useState([]);
  const [barbers, setBarbers] = useState([]);
  const [services, setServices] = useState([]);
  
  const [loading, setLoading] = useState(false);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [form] = Form.useForm();

  const fetchData = async () => {
    setLoading(true);
    try {
      const [bookRes, cliRes, barRes, serRes] = await Promise.all([
        api.get('/bookings/'),
        api.get('/clients/'),
        api.get('/barbers/'),
        api.get('/services/')
      ]);
      setData(bookRes.data);
      setClients(cliRes.data);
      setBarbers(barRes.data);
      setServices(serRes.data);
    } catch (error) {
      message.error("Ma'lumotlarni yuklashda xatolik!");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleAdd = () => {
    setEditingId(null);
    form.resetFields();
    setIsModalVisible(true);
  };

  const handleEdit = (record) => {
    setEditingId(record.id);
    form.setFieldsValue({
      ...record,
      date: moment(record.date, 'YYYY-MM-DD'),
      time: moment(record.time, 'HH:mm:ss')
    });
    setIsModalVisible(true);
  };

  const handleDelete = async (id) => {
    try {
      await api.delete(`/bookings/${id}/`);
      message.success("Buyurtma o'chirildi");
      fetchData();
    } catch (error) {
      message.error("Xatolik yuz berdi");
    }
  };

  const onFinish = async (values) => {
    const payload = {
      ...values,
      date: values.date.format('YYYY-MM-DD'),
      time: values.time.format('HH:mm:ss'),
    };

    try {
      if (editingId) {
        await api.put(`/bookings/${editingId}/`, payload);
        message.success("Buyurtma yangilandi");
      } else {
        await api.post('/bookings/', payload);
        message.success("Yangi buyurtma qo'shildi");
      }
      setIsModalVisible(false);
      fetchData();
    } catch (error) {
      message.error("Xatolik yuz berdi");
    }
  };

  const columns = [
    { title: 'ID', dataIndex: 'id', key: 'id' },
    { title: 'Mijoz', dataIndex: 'client_name', key: 'client_name' },
    { title: 'Sartarosh', dataIndex: 'barber_name', key: 'barber_name' },
    { title: 'Xizmat', dataIndex: 'service_name', key: 'service_name' },
    { title: 'Sana', dataIndex: 'date', key: 'date' },
    { title: 'Vaqt', dataIndex: 'time', key: 'time' },
    { title: 'Narx', dataIndex: 'price', key: 'price', render: (p) => `${parseFloat(p).toLocaleString()} so'm` },
    { 
      title: 'Holat', 
      dataIndex: 'status', 
      key: 'status',
      render: (status) => {
        let color = 'blue';
        if (status === 'confirmed') color = 'green';
        if (status === 'cancelled') color = 'red';
        if (status === 'done') color = 'purple';
        return <Tag color={color}>{status.toUpperCase()}</Tag>;
      }
    },
    {
      title: 'Amallar',
      key: 'action',
      render: (_, record) => (
        <Space size="small">
          <Button icon={<EditOutlined />} onClick={() => handleEdit(record)} type="primary" ghost />
          <Button 
            danger 
            icon={<DeleteOutlined />} 
            onClick={() => {
              Modal.confirm({
                title: "O'chirishni tasdiqlaysizmi?",
                onOk: () => handleDelete(record.id)
              });
            }} 
          />
        </Space>
      ),
    },
  ];

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">Buyurtmalar</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd} className="bg-indigo-600">
          Qo'shish
        </Button>
      </div>
      
      <Table 
        columns={columns} 
        dataSource={data} 
        rowKey="id" 
        loading={loading}
        scroll={{ x: true }}
      />

      <Modal
        title={editingId ? "Buyurtmani tahrirlash" : "Yangi buyurtma"}
        open={isModalVisible}
        onCancel={() => setIsModalVisible(false)}
        footer={null}
      >
        <Form form={form} layout="vertical" onFinish={onFinish} initialValues={{ status: 'pending' }}>
          <Form.Item name="client" label="Mijoz" rules={[{ required: true }]}>
            <Select showSearch optionFilterProp="children">
              {clients.map(c => <Option key={c.id} value={c.id}>{c.name}</Option>)}
            </Select>
          </Form.Item>
          <Form.Item name="barber" label="Sartarosh" rules={[{ required: true }]}>
            <Select>
              {barbers.filter(b => b.active).map(b => <Option key={b.id} value={b.id}>{b.name}</Option>)}
            </Select>
          </Form.Item>
          <Form.Item name="service" label="Xizmat" rules={[{ required: true }]}>
            <Select onChange={(val) => {
              const svc = services.find(s => s.id === val);
              if (svc && !editingId) form.setFieldsValue({ price: svc.price });
            }}>
              {services.filter(s => s.active).map(s => <Option key={s.id} value={s.id}>{s.name} - {parseFloat(s.price).toLocaleString()} so'm</Option>)}
            </Select>
          </Form.Item>
          
          <Space className="w-full">
            <Form.Item name="date" label="Sana" rules={[{ required: true }]}>
              <DatePicker />
            </Form.Item>
            <Form.Item name="time" label="Vaqt" rules={[{ required: true }]}>
              <TimePicker format="HH:mm" />
            </Form.Item>
          </Space>

          <Form.Item name="price" label="Narxi (so'm)" rules={[{ required: true }]}>
            <InputNumber className="w-full" min={0} />
          </Form.Item>
          <Form.Item name="status" label="Holat" rules={[{ required: true }]}>
            <Select>
              <Option value="pending">Kutilmoqda</Option>
              <Option value="confirmed">Tasdiqlangan</Option>
              <Option value="cancelled">Bekor qilingan</Option>
              <Option value="done">Bajarilgan</Option>
            </Select>
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

export default Bookings;
