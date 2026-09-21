import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Login } from './pages/Login';
import { Wardrobe } from './pages/Wardrobe';

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <>{children}</>;
};

const AppRoutes = () => {
  const { isAuthenticated } = useAuth();
  
  return (
    <Routes>
      <Route 
        path="/" 
        element={<Navigate to={isAuthenticated ? "/wardrobe" : "/login"} replace />} 
      />
      <Route 
        path="/login" 
        element={isAuthenticated ? <Navigate to="/wardrobe" replace /> : <Login />} 
      />
      <Route 
        path="/wardrobe" 
        element={
          <ProtectedRoute>
            <Wardrobe />
          </ProtectedRoute>
        } 
      />
    </Routes>
  );
};

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
