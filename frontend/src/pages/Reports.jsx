import React, { useState, useEffect } from 'react';
// import { apiService } from '../api'; // Tạm thời comment lại
import { TrendingUp, TrendingDown, DollarSign, Calendar, BarChart3 } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

// --- KHU VỰC DỮ LIỆU MẪU (MOCK DATA) ---

const mockMonthData = {
  summary: {
    tong_doanh_thu: 45000000,
    loi_nhuan: 31875000,
    ky_bao_cao: "Tháng 01-2026",
    growth: 12,
    tax: 675000
  },
  details: [
    { ky_bao_cao: "01-05/01", tong_doanh_thu: 5000000, loi_nhuan: 3500000 },
    { ky_bao_cao: "06-10/01", tong_doanh_thu: 6500000, loi_nhuan: 4550000 },
    { ky_bao_cao: "11/01", tong_doanh_thu: 780000, loi_nhuan: 552500 },
    { ky_bao_cao: "12/01", tong_doanh_thu: 2500000, loi_nhuan: 1770833 },
    { ky_bao_cao: "13/01", tong_doanh_thu: 2045000, loi_nhuan: 1448541 },
    { ky_bao_cao: "14/01", tong_doanh_thu: 3310000, loi_nhuan: 2344583 },
    { ky_bao_cao: "15/01", tong_doanh_thu: 1650000, loi_nhuan: 1168750 },
    { ky_bao_cao: "16-20/01", tong_doanh_thu: 0, loi_nhuan: 0 },
    { ky_bao_cao: "21-31/01", tong_doanh_thu: 0, loi_nhuan: 0 },
  ]
};

const mockWeekData = {
  summary: {
    tong_doanh_thu: 10285000,
    loi_nhuan: 7285207,
    ky_bao_cao: "Tuần 2 (T1/2026)",
    growth: 5.4,
    tax: 154275
  },
  details: [
    { ky_bao_cao: "11/01", tong_doanh_thu: 780000, loi_nhuan: 552500 },
    { ky_bao_cao: "12/01", tong_doanh_thu: 2500000, loi_nhuan: 1770833 },
    { ky_bao_cao: "13/01", tong_doanh_thu: 2045000, loi_nhuan: 1448541 },
    { ky_bao_cao: "14/01", tong_doanh_thu: 3310000, loi_nhuan: 2344583 },
    { ky_bao_cao: "15/01", tong_doanh_thu: 1650000, loi_nhuan: 1168750 },
    { ky_bao_cao: "16/01", tong_doanh_thu: 0, loi_nhuan: 0 },
    { ky_bao_cao: "17/01", tong_doanh_thu: 0, loi_nhuan: 0 },
  ]
};

// Tạo thêm dữ liệu cho "Hôm qua" để tránh lỗi khi click
const mockYesterdayData = {
    summary: {
      tong_doanh_thu: 3310000,
      loi_nhuan: 2344583,
      ky_bao_cao: "14/01/2026",
      growth: -2.1,
      tax: 45000
    },
    details: [
      { ky_bao_cao: "Sáng", tong_doanh_thu: 1100000, loi_nhuan: 800000 },
      { ky_bao_cao: "Chiều", tong_doanh_thu: 1500000, loi_nhuan: 1100000 },
      { ky_bao_cao: "Tối", tong_doanh_thu: 710000, loi_nhuan: 444583 },
    ]
};

// --- COMPONENT CHÍNH ---

const Reports = () => {
  const [reportData, setReportData] = useState(null);
  const [period, setPeriod] = useState('last_week'); 
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchReport();
  }, [period]);

  const fetchReport = () => {
    setIsLoading(true);
    
    // Giả lập độ trễ mạng (Network Latency) để tạo cảm giác thật
    setTimeout(() => {
        let data;
        switch (period) {
            case 'last_month':
                data = mockMonthData;
                break;
            case 'last_week':
                data = mockWeekData;
                break;
            case 'yesterday':
                data = mockYesterdayData;
                break;
            default:
                data = mockWeekData;
        }

        setReportData(data);
        setIsLoading(false);
    }, 600); // Delay 0.6s
  };

  if (isLoading || !reportData) return <div className="p-10 text-center text-gray-500 font-medium">Đang tổng hợp số liệu tài chính...</div>;

  const { summary, details } = reportData;

  return (
    <div className="p-6 bg-gray-50 min-h-screen font-sans">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
        <div>
          <h1 className="text-2xl font-black text-gray-800 tracking-tight">BÁO CÁO TÀI CHÍNH</h1>
          <p className="text-gray-500 flex items-center gap-2 mt-1">
            <Calendar size={16} className="text-blue-500" /> 
            <span className="font-medium">Kỳ báo cáo: {summary.ky_bao_cao}</span>
          </p>
        </div>
        
        {/* Bộ lọc thời gian */}
        <div className="flex bg-white shadow-sm rounded-xl p-1 border border-gray-200">
          {['yesterday', 'last_week', 'last_month'].map((p) => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className={`px-4 py-2 rounded-lg text-sm font-bold transition-all duration-200 ${
                period === p 
                ? 'bg-blue-600 text-white shadow-md transform scale-105' 
                : 'text-gray-500 hover:bg-gray-100'
              }`}
            >
              {p === 'yesterday' ? 'Hôm qua' : p === 'last_week' ? 'Tuần này' : 'Tháng này'}
            </button>
          ))}
        </div>
      </div>

      {/* TỔNG HỢP CHỈ SỐ */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        {/* Thẻ Doanh thu */}
        <div className="bg-white p-6 rounded-3xl shadow-sm border border-gray-100 relative overflow-hidden group hover:shadow-md transition-shadow">
          <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
            <DollarSign size={100} className="text-blue-500"/>
          </div>
          <div className="flex justify-between items-center relative z-10">
            <span className="text-gray-500 font-semibold text-sm uppercase tracking-wider">Tổng doanh thu</span>
            <div className="p-2 bg-blue-50 text-blue-600 rounded-full"><DollarSign size={20}/></div>
          </div>
          <h2 className="text-2xl font-black mt-4 text-gray-800 tracking-tighter relative z-10">
            {summary.tong_doanh_thu.toLocaleString()} <span className="text-lg font-normal text-gray-500">đ</span>
          </h2>
        </div>

        {/* Thẻ Lợi nhuận ròng */}
        <div className={`bg-white p-6 rounded-3xl shadow-sm border border-gray-100 relative overflow-hidden group hover:shadow-md transition-shadow`}>
          <div className={`absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity ${summary.loi_nhuan >= 0 ? 'text-green-500' : 'text-red-500'}`}>
            {summary.loi_nhuan >= 0 ? <TrendingUp size={100}/> : <TrendingDown size={100}/>}
          </div>
          <div className="flex justify-between items-center relative z-10">
            <span className="text-gray-500 font-semibold text-sm uppercase tracking-wider">Lợi nhuận ròng</span>
            <div className={`p-2 rounded-full ${summary.loi_nhuan >= 0 ? 'bg-green-50 text-green-600' : 'bg-red-50 text-red-600'}`}>
              {summary.loi_nhuan >= 0 ? <TrendingUp size={20}/> : <TrendingDown size={20}/>}
            </div>
          </div>
          <h2 className={`text-2xl font-black mt-4 tracking-tighter relative z-10 ${summary.loi_nhuan >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {summary.loi_nhuan.toLocaleString()} <span className="text-lg font-normal text-gray-500">đ</span>
          </h2>
          <p className="text-xs text-gray-400 mt-2 italic relative z-10">* Đã trừ thuế và chi phí vận hành.</p>
        </div>
      </div>

      {/* BIỂU ĐỒ TRỰC QUAN */}
      <div className="bg-white p-6 rounded-3xl shadow-sm border border-gray-100 mb-8">
        <h3 className="text-lg font-bold mb-6 flex items-center gap-2 text-gray-800">
          <BarChart3 className="text-blue-600" /> Biến động Doanh thu & Lợi nhuận
        </h3>
        <div className="h-80 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={details} barGap={8}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
              <XAxis 
                dataKey="ky_bao_cao" 
                fontSize={12} 
                tickMargin={15} 
                tickLine={false} 
                axisLine={false}
                stroke="#9ca3af"
              />
              <YAxis 
                fontSize={12} 
                axisLine={false} 
                tickLine={false}
                stroke="#9ca3af"
                tickFormatter={(value) => `${value / 1000000}M`}
              />
              <Tooltip 
                cursor={{fill: '#f3f4f6'}}
                contentStyle={{ borderRadius: '16px', border: 'none', boxShadow: '0 20px 25px -5px rgb(0 0 0 / 0.1)', padding: '12px' }}
                formatter={(value) => [value.toLocaleString() + ' đ']}
                labelStyle={{ fontWeight: 'bold', color: '#374151', marginBottom: '8px' }}
              />
              <Bar dataKey="tong_doanh_thu" name="Doanh thu" fill="#3b82f6" radius={[6, 6, 0, 0]} maxBarSize={50} />
              <Bar dataKey="loi_nhuan" name="Lợi nhuận" fill="#10b981" radius={[6, 6, 0, 0]} maxBarSize={50} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* BẢNG CHI TIẾT SỐ LIỆU */}
      <div className="bg-white rounded-3xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="p-4 border-b bg-gray-50">
            <h3 className="font-bold text-gray-700">Chi tiết theo kỳ</h3>
        </div>
        <div className="overflow-x-auto">
            <table className="w-full text-left">
            <thead className="bg-white border-b">
                <tr>
                <th className="p-4 text-sm font-semibold text-gray-500 uppercase tracking-wider">Thời gian</th>
                <th className="p-4 text-sm font-semibold text-gray-500 uppercase tracking-wider text-right">Doanh thu</th>
                <th className="p-4 text-sm font-semibold text-gray-500 uppercase tracking-wider text-right">Lợi nhuận</th>
                </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
                {details.map((row, index) => (
                <tr key={index} className="hover:bg-blue-50 transition-colors group">
                    <td className="p-4 text-gray-800 font-medium">{row.ky_bao_cao}</td>
                    <td className="p-4 text-right text-blue-600 font-bold group-hover:text-blue-700 transition-colors">
                        {row.tong_doanh_thu.toLocaleString()}đ
                    </td>
                    <td className={`p-4 text-right font-bold ${row.loi_nhuan >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {row.loi_nhuan.toLocaleString()}đ
                    </td>
                </tr>
                ))}
            </tbody>
            </table>
        </div>
      </div>
    </div>
  );
};

export default Reports;