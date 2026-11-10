import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { DashboardLayout } from '../layouts/DashboardLayout';
import { Login } from '../pages/auth/Login';
import { Register } from '../pages/auth/Register';
import { LearnerDashboard } from '../pages/learner/Dashboard';
import { Profile } from '../pages/learner/Profile';
import { ResumeUpload } from '../pages/learner/ResumeUpload';
import { CourseCatalog } from '../pages/courses/CourseCatalog';
import { AssessmentQuiz } from '../pages/assessments/AssessmentQuiz';
import { JobExplorer } from '../pages/jobs/JobExplorer';
import { RecommendationsList } from '../pages/recommendations/RecommendationsList';
import { ReportView } from '../pages/reports/ReportView';
import { AdminDashboard } from '../pages/admin/AdminDashboard';

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
};

const AdminRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { role, isAuthenticated, isLoading } = useAuth();
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (role !== 'admin') return <Navigate to="/dashboard" replace />;
  return <>{children}</>;
};

export const AppRoutes: React.FC = () => {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      <Route
        path="/"
        element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<LearnerDashboard />} />
        <Route path="profile" element={<Profile />} />
        <Route path="resumes" element={<ResumeUpload />} />
        <Route path="courses" element={<CourseCatalog />} />
        <Route path="assessments" element={<AssessmentQuiz />} />
        <Route path="jobs" element={<JobExplorer />} />
        <Route path="recommendations" element={<RecommendationsList />} />
        <Route path="reports" element={<ReportView />} />
        
        {/* Admin only */}
        <Route
          path="admin"
          element={
            <AdminRoute>
              <AdminDashboard />
            </AdminRoute>
          }
        />
      </Route>

      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
};
