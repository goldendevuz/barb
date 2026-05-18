import React, { useState, useEffect } from 'react';
import { Table, message } from 'antd';
import api from '../services/api';

const Services = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchServices = async () => {
      setLoading(true);
      try {
        const response = await api.get('/services/');
        setData(response.data);
      } catch (error) {
        message.error("Xatolik yuz berdi");
      } finally {
        setLoading(false);
      }
    };
    fetchServices();
  }, []);

  const columns = [
    { title: 'ID', dataIndex: 'id', key: 'id' },
    { title: 'Xizmat nomi', dataIndex: 'name', key: 'name' },
    { 
      title: 'Narxi', 
      dataIndex: 'price', 
      key: 'price',
      render: (price) => `${parseFloat(price).toLocaleString()} so'm`
    },
    { 
      title: 'Davomiyligi', 
      dataIndex: 'duration', 
      key: 'duration',
      render: (d) => `${d} daq.`
    },
  ];

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm">
      <h2 className="text-xl font-semibold mb-4">Xizmatlar</h2>
      <Table columns={columns} dataSource={data} rowKey="id" loading={loading} />
    </div>
  );
};

export default Services;
