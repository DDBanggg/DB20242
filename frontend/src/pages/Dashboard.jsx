import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Percent, Wallet, Receipt, ShoppingBag, CreditCard } from 'lucide-react';
import { apiService } from '../api';

const Dashboard = () => {
  // THIẾT LẬP SỐ LIỆU FAKE ĐỂ DEMO (Khớp logic 1.5% thuế)
  // Giả sử: Doanh thu 45tr, Thuế HKD = 45tr * 1.5% = 675k, Lợi nhuận ròng ~15tr
  const [stats, setStats] = useState({ 
    revenue: 45000000, 
    profit: 31875000, 
    taxHKD: 675000 
  });
  
  const [isLoading, setIsLoading] = useState(false); // Để false để hiện số liệu fake ngay

  // Phần này có thể giữ lại để sau này kết nối DB thật, hiện tại demo dùng số liệu trên
  useEffect(() => {
    // fetchStats(); 
  }, []);

  // BỔ SUNG NHIỀU KHOẢN THU (Bán hàng) ĐỂ LÀM ĐẸP DANH SÁCH
  const recentActivities = [
    { id: 1, title: 'Bán hàng (Hóa đơn #125)', time: 'Vừa xong', amount: '+450,000 ₫', type: 'in' },
    { id: 2, title: 'Bán hàng (Hóa đơn #124)', time: '5 phút trước', amount: '+1,200,000 ₫', type: 'in' },
    { id: 3, title: 'Bán hàng (Hóa đơn #123)', time: '15 phút trước', amount: '+850,000 ₫', type: 'in' },
    { id: 4, title: 'Bán hàng (Hóa đơn #122)', time: '1 giờ trước', amount: '+2,100,000 ₫', type: 'in' },
    { id: 5, title: 'Thanh toán tiền Internet', time: '09:00 AM', amount: '-350,000 ₫', type: 'out' },
    { id: 6, title: 'Bán hàng (Hóa đơn #121)', time: 'Hôm qua', amount: '+550,000 ₫', type: 'in' },
    { id: 7, title: 'Bán hàng (Hóa đơn #120)', time: 'Hôm qua', amount: '+1,500,000 ₫', type: 'in' },
    { id: 8, title: 'Mua văn phòng phẩm', time: 'Hôm qua', amount: '-150,000 ₫', type: 'out' },
    { id: 9, title: 'Bán hàng (Hóa đơn #119)', time: '2 ngày trước', amount: '+3,200,000 ₫', type: 'in' },
    { id: 10, title: 'Nhập hàng bổ sung', time: '3 ngày trước', amount: '-10,000,000 ₫', type: 'out' },
  ];

  return (
    <div className="space-y-6">
      {/* 1. DOANH THU THÁNG NÀY (Đã đổi tên và số liệu) */}
      <div className="bg-primary p-6 rounded-b-[40px] -mx-4 -mt-4 text-white shadow-xl shadow-primary/20">
        <p className="opacity-80 text-xs font-bold uppercase tracking-widest">Doanh thu tháng này</p>
        <h1 className="text-4xl font-black mt-1">{stats.revenue.toLocaleString()} ₫</h1>
      </div>

      {/* 2. CÁC THẺ TÀI CHÍNH */}
      <div className="space-y-4 px-1">
        {/* THUẾ HKD PHẢI ĐÓNG (1.5%) */}
        <div className="bg-orange-50 border-2 border-orange-100 p-4 rounded-3xl flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="bg-orange-500 text-white p-2 rounded-xl shadow-md shadow-orange-200"><Percent size={18}/></div>
            <div>
              <p className="text-[10px] text-orange-600 font-bold uppercase">Thuế HKD phải nộp (1.5%)</p>
              <h3 className="text-xl font-black text-orange-800">{stats.taxHKD.toLocaleString()} ₫</h3>
            </div>
          </div>
          <div className="text-[10px] bg-orange-200 text-orange-700 px-2 py-1 rounded-full font-bold">CƠ QUAN THUẾ</div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          {/* Lợi nhuận thực tế */}
          <div className="bg-white p-4 rounded-3xl shadow-sm border border-gray-50">
            <div className="flex items-center text-green-600 mb-2 gap-1">
              <Wallet size={16} />
              <span className="text-[10px] font-black uppercase">Lợi nhuận ròng</span>
            </div>
            <p className="text-lg font-black text-gray-800">+{stats.profit.toLocaleString()}₫</p>
            <p className="text-[9px] text-gray-400 mt-1 italic">Đã trừ thuế 1.5%</p>
          </div>

          {/* Chi phí (Fix số liệu) */}
          <div className="bg-white p-4 rounded-3xl shadow-sm border border-gray-50">
            <div className="flex items-center text-red-500 mb-2 gap-1">
              <CreditCard size={16} />
              <span className="text-[10px] font-black uppercase">Tổng chi phí</span>
            </div>
            <p className="text-lg font-black text-gray-800">-12,450,000₫</p>
            <p className="text-[9px] text-gray-400 mt-1 italic">Vận hành & Nhập hàng</p>
          </div>
        </div>
      </div>

      {/* 3. HOẠT ĐỘNG GẦN ĐÂY (Nhiều khoản thu hơn) */}
      <div className="px-1">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-gray-900 font-black text-lg">Hoạt động gần đây</h3>
          <span className="text-primary text-xs font-bold">Xem báo cáo</span>
        </div>
        
        <div className="space-y-3 pb-4">
          {recentActivities.map(act => (
            <div key={act.id} className="bg-white p-4 rounded-2xl flex justify-between items-center shadow-sm border border-gray-50 active:scale-[0.98] transition">
              <div className="flex items-center gap-4">
                <div className={`p-3 rounded-xl ${act.type === 'in' ? 'bg-green-50 text-green-600' : 'bg-red-50 text-red-500'}`}>
                  {act.type === 'in' ? <Receipt size={20} /> : <ShoppingBag size={20} />}
                </div>
                <div>
                  <p className="font-bold text-gray-800 text-sm">{act.title}</p>
                  <p className="text-[10px] text-gray-400 font-medium uppercase tracking-tighter">{act.time}</p>
                </div>
              </div>
              <p className={`font-black text-sm ${act.type === 'in' ? 'text-green-600' : 'text-red-500'}`}>
                {act.amount}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;