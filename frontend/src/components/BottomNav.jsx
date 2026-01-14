import { Home, Receipt, Plus, BarChart3, Settings } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';

const BottomNav = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const navItems = [
    { icon: Home, path: '/', label: 'Home' },
    { icon: Receipt, path: '/history', label: 'Orders' },
    { isFab: true }, // Nút (+) ở giữa
    { icon: BarChart3, path: '/reports', label: 'Reports' },
    { icon: Settings, path: '/settings', label: 'Settings' },
  ];

  return (
    <nav className="fixed bottom-0 left-0 right-0 flex justify-center z-50">
      <div className="w-full max-w-md bg-white border-t flex justify-around items-center h-16 relative">
        {navItems.map((item, index) => {
          if (item.isFab) {
            return (
              <button
                key={index}
                onClick={() => navigate('/create')}
                className="bg-primary text-white p-4 rounded-full shadow-lg absolute -top-8 border-4 border-background transform active:scale-95 transition-transform"
              >
                <Plus size={32} />
              </button>
            );
          }
          const isActive = location.pathname === item.path;
          return (
            <button
              key={index}
              onClick={() => navigate(item.path)}
              className={`flex flex-col items-center ${isActive ? 'text-primary' : 'text-gray-400'}`}
            >
              <item.icon size={24} />
              <span className="text-[10px] mt-1 font-medium">{item.label}</span>
            </button>
          );
        })}
      </div>
    </nav>
  );
};

export default BottomNav;