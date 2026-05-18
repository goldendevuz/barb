import React, { useState, useEffect } from 'react';
import { Table, Tag, Button, Space, message, Modal } from 'antd';
import { PlusOutlined, DeleteOutlined } from '@ant-design/icons';
import api from '../services/api';

const Bookings = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchBookings = async () => {
    setLoading(true);
    try {
      const response = await api.get('/bookings/');
      setData(response.data);
    } catch (error) {
      message.error("Buyurtmalarni yuklashda xatolik!");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBookings();
  }, []);

  const handleDelete = async (id) => {
    try {
      await api.delete(`/bookings/${id}/`);
      message.success("Buyurtma o'chirildi");
      fetchBookings();
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
      title: 'Harakat',
      key: 'action',
      render: (_, record) => (
        <Space size="middle">
          <Button 
            danger 
            icon={<DeleteOutlined />} 
            onClick={() => {
              Modal.confirm({
                title: "Rostdan ham o'chirasizmi?",
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
        <Button type="primary" icon={<PlusOutlined />} className="bg-indigo-600">
          Yangi qo'shish
        </Button>
      </div>
      <Table 
        columns={columns} 
        dataSource={data} 
        rowKey="id" 
        loading={loading}
        scroll={{ x: true }}
      />
    </div>
  );
};

export default Bookings;
