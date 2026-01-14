import { TrendingUp, TrendingDown } from 'lucide-react';

const Dashboard = () => {
  return (
    <div className="space-y-6">
      {/* Header Doanh thu */}
      <div className="bg-primary p-6 rounded-b-3xl -mx-4 -mt-4 text-white shadow-md">
        <p className="opacity-80 text-sm">Doanh thu hôm nay</p>
        <h1 className="text-3xl font-bold">12,500,000 ₫</h1>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white p-4 rounded-2xl shadow-sm border border-gray-100">
          <div className="flex items-center text-green-600 mb-1">
            <TrendingUp size={16} className="mr-1" />
            <span className="text-xs font-bold uppercase">Lãi tháng</span>
          </div>
          <p className="text-xl font-bold text-gray-800">+45.2m</p>
        </div>
        <div className="bg-white p-4 rounded-2xl shadow-sm border border-gray-100">
          <div className="flex items-center text-red-500 mb-1">
            <TrendingDown size={16} className="mr-1" />
            <span className="text-xs font-bold uppercase">Chi phí</span>
          </div>
          <p className="text-xl font-bold text-gray-800">-12.8m</p>
        </div>
      </div>

      {/* Recent Activity */}
      <div>
        <h3 className="text-gray-800 font-bold mb-3">Hoạt động gần đây</h3>
        <div className="space-y-3">
          {[
            { id: 1, title: 'Bán hàng (POS)', time: '10:30 AM', amount: '+500,000 ₫', type: 'in' },
            { id: 2, title: 'Hóa đơn điện', time: '08:15 AM', amount: '-1,200,000 ₫', type: 'out' },
          ].map(act => (
            <div key={act.id} className="bg-white p-4 rounded-xl flex justify-between items-center shadow-sm">
              <div className="flex items-center gap-3">
                <div className={`p-2 rounded-lg ${act.type === 'in' ? 'bg-green-100' : 'bg-red-100'}`}>
                  {act.type === 'in' ? <TrendingUp className="text-green-600" size={20} /> : <TrendingDown className="text-red-500" size={20} />}
                </div>
                <div>
                  <p className="font-semibold text-gray-800">{act.title}</p>
                  <p className="text-xs text-gray-400">{act.time}</p>
                </div>
              </div>
              <p className={`font-bold ${act.type === 'in' ? 'text-green-600' : 'text-red-500'}`}>{act.amount}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;