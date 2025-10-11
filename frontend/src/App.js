import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from '@/contexts/AuthContext';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import { Login } from '@/pages/Login';
import { Register } from '@/pages/Register';
import { Dashboard } from '@/pages/Dashboard';
import { Properties } from '@/pages/Properties';
import { TechnicianTasks } from '@/pages/TechnicianTasks';
import { MeterReading } from '@/pages/MeterReading';
import { CustomerData } from '@/pages/CustomerData';
import { TaskMap } from '@/pages/TaskMap';
import { BalancePurchase } from '@/pages/BalancePurchase';
import { PurchaseHistory } from '@/pages/PurchaseHistory';
import { PurchaseReceipt } from '@/pages/PurchaseReceipt';
import { AdminPaymentSettings } from '@/pages/AdminPaymentSettings';
import { AdminDashboard } from '@/pages/AdminDashboard';
import { UserManagement } from '@/pages/UserManagement';
import "@/App.css";

// Placeholder pages (will be created in next phases)
const Devices = () => (
  <div className="p-6">
    <h1 className="text-2xl font-bold">Devices Page</h1>
    <p>Coming in Phase 2...</p>
  </div>
);

const Users = () => (
  <div className="p-6">
    <h1 className="text-2xl font-bold">Users Page</h1>
    <p>Coming soon...</p>
  </div>
);

const Customers = () => (
  <div className="p-6">
    <h1 className="text-2xl font-bold">Customers Page</h1>
    <p>Coming soon...</p>
  </div>
);

const MyDevices = () => (
  <div className="p-6">
    <h1 className="text-2xl font-bold">My Devices</h1>
    <p>Coming soon...</p>
  </div>
);

const Transactions = () => (
  <div className="p-6">
    <h1 className="text-2xl font-bold">Transactions</h1>
    <p>Coming soon...</p>
  </div>
);

const Unauthorized = () => (
  <div className="min-h-screen flex items-center justify-center bg-gray-50">
    <div className="text-center">
      <h1 className="text-4xl font-bold text-gray-900 mb-4">403</h1>
      <p className="text-xl text-gray-600 mb-6">Unauthorized Access</p>
      <p className="text-gray-500 mb-8">You don't have permission to access this page</p>
      <a href="/dashboard" className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg inline-block">
        Go to Dashboard
      </a>
    </div>
  </div>
);

// Dashboard router based on role
const DashboardRouter = () => {
  const { user } = useAuth();
  
  if (user?.role === 'admin') {
    return <AdminDashboard />;
  }
  
  return <Dashboard />;
};

const AppRoutes = () => {
  const { isAuthenticated } = useAuth();

  return (
    <Routes>
      {/* Public routes */}
      <Route 
        path="/login" 
        element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <Login />} 
      />
      <Route 
        path="/register" 
        element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <Register />} 
      />
      
      {/* Protected routes */}
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <DashboardRouter />
          </ProtectedRoute>
        }
      />
      
      <Route
        path="/users"
        element={
          <ProtectedRoute allowedRoles={['admin']}>
            <UserManagement />
          </ProtectedRoute>
        }
      />
      
      <Route
        path="/customers"
        element={
          <ProtectedRoute allowedRoles={['admin']}>
            <Customers />
          </ProtectedRoute>
        }
      />
      
      <Route
        path="/payment-settings"
        element={
          <ProtectedRoute allowedRoles={['admin']}>
            <AdminPaymentSettings />
          </ProtectedRoute>
        }
      />
      
      <Route
        path="/properties"
        element={
          <ProtectedRoute allowedRoles={['admin', 'technician']}>
            <Properties />
          </ProtectedRoute>
        }
      />
      
      <Route
        path="/devices"
        element={
          <ProtectedRoute allowedRoles={['admin', 'technician']}>
            <Devices />
          </ProtectedRoute>
        }
      />
      
      <Route
        path="/tasks"
        element={
          <ProtectedRoute allowedRoles={['admin', 'technician']}>
            <TechnicianTasks />
          </ProtectedRoute>
        }
      />
      
      <Route
        path="/meter-reading"
        element={
          <ProtectedRoute allowedRoles={['technician']}>
            <MeterReading />
          </ProtectedRoute>
        }
      />
      
      <Route
        path="/customer-data"
        element={
          <ProtectedRoute allowedRoles={['admin', 'technician']}>
            <CustomerData />
          </ProtectedRoute>
        }
      />
      
      <Route
        path="/task-map"
        element={
          <ProtectedRoute allowedRoles={['technician']}>
            <TaskMap />
          </ProtectedRoute>
        }
      />
      
      <Route
        path="/my-devices"
        element={
          <ProtectedRoute allowedRoles={['customer']}>
            <MyDevices />
          </ProtectedRoute>
        }
      />
      
      <Route
        path="/balance-purchase"
        element={
          <ProtectedRoute allowedRoles={['customer']}>
            <BalancePurchase />
          </ProtectedRoute>
        }
      />
      
      <Route
        path="/purchase-history"
        element={
          <ProtectedRoute allowedRoles={['customer']}>
            <PurchaseHistory />
          </ProtectedRoute>
        }
      />
      
      <Route
        path="/purchase-receipt/:referenceId"
        element={
          <ProtectedRoute allowedRoles={['customer']}>
            <PurchaseReceipt />
          </ProtectedRoute>
        }
      />
      
      <Route
        path="/transactions"
        element={
          <ProtectedRoute allowedRoles={['customer']}>
            <Transactions />
          </ProtectedRoute>
        }
      />
      
      <Route path="/unauthorized" element={<Unauthorized />} />
      
      {/* Redirect root to dashboard or login */}
      <Route 
        path="/" 
        element={<Navigate to={isAuthenticated ? "/dashboard" : "/login"} replace />} 
      />
      
      {/* 404 route */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
        <Toaster 
          position="top-right"
          toastOptions={{
            duration: 3000,
            style: {
              background: '#363636',
              color: '#fff',
            },
            success: {
              duration: 3000,
              iconTheme: {
                primary: '#10B981',
                secondary: '#fff',
              },
            },
            error: {
              duration: 4000,
              iconTheme: {
                primary: '#EF4444',
                secondary: '#fff',
              },
            },
          }}
        />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
