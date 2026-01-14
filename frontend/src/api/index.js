import axios from 'axios';

const API_URL = 'http://localhost:8000'; // Địa chỉ Backend của bạn

const api = axios.create({
  baseURL: API_URL,
});

export const apiService = {
  // Lấy danh sách sản phẩm (từ operation_2)
  getProducts: () => api.get('/sanpham/'),
  
  // Tạo đơn hàng mới (từ operation_7)
  createOrder: (orderData) => api.post('/donhangban/', orderData),
  
  // Lấy chi tiết hóa đơn bao gồm thuế VAT và thuế HKD (từ operation_7)
  getOrderDetail: (id) => api.get(`/donhangban/${id}`),
  
  // Lấy báo cáo tài chính lãi/lỗ thực tế (từ operation_10)
  getFinancialReport: (period = 'last_month') => 
    api.get(`/reports/financial?period=${period}`),
    
  // Lấy lịch sử tất cả hóa đơn
  getAllOrders: () => api.get('/donhangban/all'),
};

export default api;