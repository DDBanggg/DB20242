import axios from 'axios';

// Địa chỉ Backend chạy thực tế (Dữ liệu thật từ Database)
const API_URL = 'http://localhost:8000'; 

const api = axios.create({
  baseURL: API_URL,
});

export const apiService = {
  // --- 1. QUẢN LÝ DANH MỤC (Router 1) ---
  getCategories: () => api.get('/categories/'),
  createCategory: (data) => api.post('/categories/', data),
  updateCategory: (id, data) => api.put(`/categories/${id}`, data),

  // --- 2. SẢN PHẨM & TỒN KHO (Router 2) ---
  // Lấy dữ liệu thật từ DB: Tên, Mã, Giá hiện hành và Tồn kho thực tế
  getPOSProducts: (tu_khoa = '') => api.get(`/san-pham/danh-sach?tu_khoa=${tu_khoa}`),
  
  // --- 3. NGHIỆP VỤ BÁN HÀNG & TRỪ KHO (Router 7) ---
  // Bước A: Tạo đơn hàng mới trong bảng DonHangBan
  createOrder: (orderData) => api.post('/donhangban/', orderData),
  
  // Bước B: Thêm sản phẩm (Tại đây Trigger DB sẽ tự động thực hiện trừ kho thật)
  addItemToOrder: (itemData) => api.post('/donhangban/add-item', itemData),
  
  // Lấy chi tiết hóa đơn (bao gồm tính toán Thuế 11.5% từ Backend)
  getOrderDetail: (id) => api.get(`/donhangban/chitiet/${id}`),
  
  // Lấy danh sách lịch sử tất cả hóa đơn
  getAllOrders: (params = {}) => api.get('/donhangban/', { params }),

  // Cập nhật trạng thái đơn hàng (Duyệt, Hủy, Hoàn tất)
  updateOrderStatus: (id, statusData) => api.put(`/donhangban/update-status/${id}`, statusData),

  // --- 4. BÁO CÁO TÀI CHÍNH LÃI/LỖ (Router 10) ---
  // Lấy báo cáo Doanh thu & Lợi nhuận ròng (đã trừ Thuế & Giá vốn)
  getFinancialReport: (period = 'last_week', start = null, end = null) => {
    let url = `/baocao/taichinh/?period=${period}`;
    if (start && end) {
      url += `&start_date=${start}&end_date=${end}`;
    }
    return api.get(url);
  },
};

export default api;