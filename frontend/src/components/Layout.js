import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import ChatWidget from './ChatWidget';
import NotificationBell from './NotificationBell';
import { 
  LayoutDashboard, 
  Users, 
  Building2, 
  Gauge, 
  CreditCard,
  Settings,
  LogOut,
  Menu,
  X,
  Droplets,
  ClipboardList,
  FileText,
  UserCheck,
  Map,
  ShoppingCart,
  History,
  BarChart3,
  Target
} from 'lucide-react';

export const Layout = ({ children }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = React.useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const getNavItems = () => {
    const items = [
      { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard', roles: ['admin', 'technician', 'customer'] },
    ];

    if (user?.role === 'admin') {
      items.push(
        { path: '/users', icon: Users, label: 'Users', roles: ['admin'] },
        { path: '/customers', icon: Users, label: 'Customers', roles: ['admin'] },
        { path: '/properties', icon: Building2, label: 'Properties', roles: ['admin'] },
        { path: '/devices', icon: Gauge, label: 'Devices', roles: ['admin'] },
        { path: '/payment-settings', icon: Settings, label: 'Payment Settings', roles: ['admin'] },
      );
    }

    if (user?.role === 'technician') {
      items.push(
        { path: '/tasks', icon: ClipboardList, label: 'Work Orders', roles: ['technician'] },
        { path: '/task-map', icon: Map, label: 'Task Map', roles: ['technician'] },
        { path: '/meter-reading', icon: FileText, label: 'Meter Reading', roles: ['technician'] },
        { path: '/customer-data', icon: UserCheck, label: 'Customers', roles: ['technician'] },
        { path: '/properties', icon: Building2, label: 'Properties', roles: ['technician'] },
        { path: '/devices', icon: Gauge, label: 'Devices', roles: ['technician'] },
      );
    }

    if (user?.role === 'customer') {
      items.push(
        { path: '/my-devices', icon: Gauge, label: 'My Devices', roles: ['customer'] },
        { path: '/analytics', icon: BarChart3, label: 'Analytics', roles: ['customer'] },
        { path: '/budget-goals', icon: Target, label: 'Budget Goals', roles: ['customer'] },
        { path: '/balance-purchase', icon: ShoppingCart, label: 'Buy Balance', roles: ['customer'] },
        { path: '/purchase-history', icon: History, label: 'Purchase History', roles: ['customer'] },
        { path: '/transactions', icon: CreditCard, label: 'Transactions', roles: ['customer'] },
      );
    }
    
    // Analytics for admin
    if (user?.role === 'admin') {
      items.push(
        { path: '/analytics', icon: BarChart3, label: 'Analytics', roles: ['admin'] }
      );
    }

    return items;
  };

  const navItems = getNavItems();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`
        fixed top-0 left-0 z-50 h-full w-64 bg-white border-r border-gray-200 
        transform transition-transform duration-200 ease-in-out
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
            <div className="flex items-center space-x-2">
              <Droplets className="h-8 w-8 text-blue-600" />
              <span className="text-xl font-bold text-gray-900">IndoWater</span>
            </div>
            <button 
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden text-gray-500 hover:text-gray-700"
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          {/* User info */}
          <div className="px-6 py-4 border-b border-gray-200">
            <p className="text-sm font-medium text-gray-900">{user?.full_name}</p>
            <p className="text-xs text-gray-500">{user?.email}</p>
            <span className="inline-block mt-2 px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800 capitalize">
              {user?.role}
            </span>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-4 space-y-1 overflow-y-auto">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`
                    flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors
                    ${isActive 
                      ? 'bg-blue-50 text-blue-600 font-medium' 
                      : 'text-gray-700 hover:bg-gray-50'
                    }
                  `}
                  onClick={() => setSidebarOpen(false)}
                >
                  <Icon className="h-5 w-5" />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>

          {/* Logout button */}
          <div className="px-4 py-4 border-t border-gray-200">
            <button
              onClick={handleLogout}
              className="flex items-center space-x-3 w-full px-3 py-2 text-gray-700 hover:bg-gray-50 rounded-lg transition-colors"
            >
              <LogOut className="h-5 w-5" />
              <span>Logout</span>
            </button>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top bar */}
        <header className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
          <button
            onClick={() => setSidebarOpen(true)}
            className="lg:hidden text-gray-500 hover:text-gray-700"
          >
            <Menu className="h-6 w-6" />
          </button>
          
          <div className="flex items-center gap-4">
            <NotificationBell />
            <div className="text-sm text-gray-600">
              Welcome back, <span className="font-medium text-gray-900">{user?.full_name}</span>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="p-6">
          {children}
        </main>
      </div>

      {/* AI Chat Widget */}
      <ChatWidget />
    </div>
  );
};