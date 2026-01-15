import React, { useState, useEffect } from 'react';
import { apiService } from '../api';

const CategoryManager = () => {
  const [categories, setCategories] = useState([]);
  const [formData, setFormData] = useState({ ma_danh_muc: '', ten_danh_muc: '', mo_ta: '' });
  const [isEditing, setIsEditing] = useState(null);

  useEffect(() => {
    loadCategories();
  }, []);

  const loadCategories = async () => {
    try {
      const res = await apiService.getCategories();
      setCategories(res.data);
    } catch (err) {
      alert("Lỗi tải danh mục");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (isEditing) {
        await apiService.updateCategory(isEditing, formData);
      } else {
        await apiService.createCategory(formData);
      }
      setFormData({ ma_danh_muc: '', ten_danh_muc: '', mo_ta: '' });
      setIsEditing(null);
      loadCategories();
    } catch (err) {
      alert("Lỗi khi lưu: " + (err.response?.data?.detail || "Dữ liệu không hợp lệ"));
    }
  };

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <h1 className="text-2xl font-bold mb-6 text-blue-700">Quản lý Danh mục Sản phẩm</h1>
      
      {/* Form Thêm/Sửa */}
      <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow-md mb-8 grid grid-cols-1 md:grid-cols-3 gap-4">
        <input 
          className="border p-2 rounded" 
          placeholder="Mã danh mục (VD: MP01)" 
          value={formData.ma_danh_muc}
          onChange={(e) => setFormData({...formData, ma_danh_muc: e.target.value})}
          required
        />
        <input 
          className="border p-2 rounded" 
          placeholder="Tên danh mục" 
          value={formData.ten_danh_muc}
          onChange={(e) => setFormData({...formData, ten_danh_muc: e.target.value})}
          required
        />
        <input 
          className="border p-2 rounded" 
          placeholder="Mô tả" 
          value={formData.mo_ta}
          onChange={(e) => setFormData({...formData, mo_ta: e.target.value})}
        />
        <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
          {isEditing ? "Cập nhật" : "Thêm danh mục"}
        </button>
      </form>

      {/* Danh sách */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-gray-100">
            <tr>
              <th className="p-3">Mã</th>
              <th className="p-3">Tên danh mục</th>
              <th className="p-3">Mô tả</th>
              <th className="p-3">Thao tác</th>
            </tr>
          </thead>
          <tbody>
            {categories.map((cat) => (
              <tr key={cat.id} className="border-t hover:bg-gray-50">
                <td className="p-3 font-semibold text-gray-700">{cat.ma_danh_muc}</td>
                <td className="p-3">{cat.ten_danh_muc}</td>
                <td className="p-3 text-gray-500">{cat.mo_ta}</td>
                <td className="p-3">
                  <button 
                    onClick={() => {setIsEditing(cat.id); setFormData(cat);}}
                    className="text-blue-600 hover:underline"
                  >Sửa</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default CategoryManager;