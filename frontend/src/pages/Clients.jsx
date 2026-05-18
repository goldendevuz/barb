import React, { useState, useEffect } from 'react';
import { Table, message } from 'antd';
import api from '../services/api';

const Clients = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
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
    fetchClients();
  }, []);

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
  ];

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm">
      <h2 className="text-xl font-semibold mb-4">Mijozlar</h2>
      <Table columns={columns} dataSource={data} rowKey="id" loading={loading} />
    </div>
  );
};

export default Clients;
