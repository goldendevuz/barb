import React, { useState, useEffect } from 'react';
import { Table, Tag, Switch, message } from 'antd';
import api from '../services/api';

const Barbers = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);

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

  const toggleActive = async (checked, record) => {
    try {
      await api.patch(`/barbers/${record.id}/`, { active: checked });
      message.success("Holat o'zgardi");
      fetchBarbers();
    } catch (error) {
      message.error("Xatolik!");
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
  ];

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm">
      <h2 className="text-xl font-semibold mb-4">Sartaroshlar</h2>
      <Table columns={columns} dataSource={data} rowKey="id" loading={loading} />
    </div>
  );
};

export default Barbers;
