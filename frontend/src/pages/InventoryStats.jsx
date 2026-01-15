import React, { useState, useEffect } from 'react';
import { apiService } from '../api';

const InventoryStats = () => {
  const [products, setProducts] = useState([]);

  useEffect(() => {
    const fetchStock = async () => {
      const res = await apiService.getPOSProducts();
      setProducts(res.data.data);
    };
    fetchStock();
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Thống kê tồn kho</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {products.map(p => (
          <div key={p.id} className={`p-4 border rounded-lg shadow-sm ${p.canh_bao ? 'bg-red-50 border-red-200' : 'bg-white'}`}>
            <div className="flex justify-between items-start">
              <div>
                <h3 className="font-bold text-lg">{p.ten_san_pham}</h3>
                <p className="text-sm text-gray-500">Mã: {p.ma_san_pham}</p>
              </div>
              {p.canh_bao && <span className="bg-red-600 text-white text-xs px-2 py-1 rounded-full animate-pulse">Sắp hết!</span>}
            </div>
            <div className="mt-4 flex justify-between items-end">
              <div>
                <span className="text-3xl font-bold">{p.so_luong_ton_kho}</span>
                <span className="ml-1 text-gray-500">{p.don_vi_tinh}</span>
              </div>
              <p className={`text-sm ${p.canh_bao ? 'text-red-600 font-bold' : 'text-green-600'}`}>
                {p.trang_thai_kho}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default InventoryStats;