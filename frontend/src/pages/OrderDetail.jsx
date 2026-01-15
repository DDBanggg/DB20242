import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Printer, Share2, CheckCircle2, Package, User, MapPin } from 'lucide-react';
import { apiService } from '../api';

const OrderDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [order, setOrder] = useState(null);

  // DỮ LIỆU FAKE CHI TIẾT ĐƠN HÀNG ĐỂ DEMO
  const fakeOrderDetails = {
    1025: {
      id: 1025,
      time: '10:30 - 15/01/2026',
      customer: 'Nguyễn Văn A',
      address: 'Tại cửa hàng',
      status: 'Hoàn tất',
      payment: 'Tiền mặt',
      items: [
        { name: 'Áo sơ mi nam Oxford', qty: 2, price: 150000 },
        { name: 'Quần tây lửng', qty: 1, price: 150000 },
      ]
    },
    1024: {
      id: 1024,
      time: '09:15 - 15/01/2026',
      customer: 'Khách lẻ',
      address: 'Giao tận nơi - Quận 1',
      status: 'Hoàn tất',
      payment: 'Chuyển khoản',
      items: [
        { name: 'Váy hoa nhí', qty: 3, price: 400000 },
      ]
    }
  };

  useEffect(() => {
    // Ưu tiên lấy từ fake data để demo, nếu không có thì lấy mặc định
    const data = fakeOrderDetails[id] || fakeOrderDetails[1025];
    setOrder(data);
  }, [id]);

  if (!order) return <div className="p-10 text-center">Đang tải chi tiết...</div>;

  // Tính toán số liệu (VAT 10% như Feature 5)
  const subtotal = order.items.reduce((sum, item) => sum + (item.qty * item.price), 0);
  const vat = subtotal * 0.1;
  const total = subtotal + vat;

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* HEADER TÍCH HỢP NÚT QUAY LẠI */}
      <header className="bg-white p-4 flex items-center justify-between border-b sticky top-0 z-10">
        <button onClick={() => navigate('/history')} className="p-2 -ml-2">
          <ArrowLeft size={24} className="text-gray-600" />
        </button>
        <h1 className="font-bold text-lg text-gray-800">Chi tiết hóa đơn #{order.id}</h1>
        <div className="flex gap-2">
          <Printer size={20} className="text-gray-400" />
          <Share2 size={20} className="text-gray-400" />
        </div>
      </header>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* TRẠNG THÁI ĐƠN HÀNG */}
        <div className="bg-white p-6 rounded-[32px] shadow-sm text-center space-y-2">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-green-50 text-green-500 rounded-full mb-2">
            <CheckCircle2 size={32} />
          </div>
          <h2 className="text-2xl font-black text-gray-800">{total.toLocaleString()}đ</h2>
          <p className="text-xs font-bold text-green-600 uppercase tracking-widest">{order.status}</p>
        </div>

        {/* THÔNG TIN KHÁCH HÀNG & GIAO HÀNG */}
        <div className="bg-white p-5 rounded-[24px] shadow-sm space-y-4 border border-gray-50">
          <div className="flex items-start gap-4">
            <User className="text-gray-400 mt-1" size={18} />
            <div>
              <p className="text-[10px] text-gray-400 font-bold uppercase">Khách hàng</p>
              <p className="font-bold text-gray-800">{order.customer}</p>
            </div>
          </div>
          <div className="flex items-start gap-4">
            <MapPin className="text-gray-400 mt-1" size={18} />
            <div>
              <p className="text-[10px] text-gray-400 font-bold uppercase">Địa chỉ giao hàng</p>
              <p className="text-sm text-gray-600">{order.address}</p>
            </div>
          </div>
        </div>

        {/* DANH SÁCH SẢN PHẨM TRONG HÓA ĐƠN */}
        <div className="bg-white p-5 rounded-[24px] shadow-sm border border-gray-50">
          <div className="flex items-center gap-2 mb-4">
            <Package size={18} className="text-primary" />
            <h3 className="font-bold text-gray-800">Danh sách món</h3>
          </div>
          
          <div className="space-y-4">
            {order.items.map((item, index) => (
              <div key={index} className="flex justify-between items-center py-2 border-b border-gray-50 last:border-0">
                <div>
                  <p className="font-bold text-sm text-gray-800">{item.name}</p>
                  <p className="text-xs text-gray-400">{item.price.toLocaleString()}đ x {item.qty}</p>
                </div>
                <p className="font-bold text-gray-800">{(item.price * item.qty).toLocaleString()}đ</p>
              </div>
            ))}
          </div>
        </div>

        {/* CHI TIẾT THANH TOÁN & THUẾ (Feature 5) */}
        <div className="bg-white p-5 rounded-[24px] shadow-sm border border-gray-50 space-y-3">
          <div className="flex justify-between text-sm text-gray-500 font-medium">
            <span>Tiền hàng</span>
            <span>{subtotal.toLocaleString()}đ</span>
          </div>
          <div className="flex justify-between text-sm text-gray-500 font-medium">
            <span>VAT (10%)</span>
            <span>{vat.toLocaleString()}đ</span>
          </div>
          <div className="flex justify-between text-sm text-gray-500 font-medium">
            <span>Phương thức</span>
            <span className="text-gray-800">{order.payment}</span>
          </div>
          <div className="flex justify-between text-lg font-black pt-3 border-t text-primary">
            <span>TỔNG CỘNG</span>
            <span>{total.toLocaleString()}đ</span>
          </div>
        </div>

        <div className="text-center pb-10">
          <p className="text-[10px] text-gray-400 uppercase font-bold tracking-widest">{order.time}</p>
        </div>
      </div>
    </div>
  );
};

export default OrderDetail;