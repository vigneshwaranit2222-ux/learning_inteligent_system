import React, { useState, useEffect } from 'react';
import { apiClient } from '../../services/api';
import { 
  Users, FileText, BookOpen, Briefcase, Award, 
  Activity, ShieldCheck, UserCheck, CheckCircle2 
} from 'lucide-react';

export const AdminDashboard: React.FC = () => {
  const [analytics, setAnalytics] = useState<any>(null);
  const [users, setUsers] = useState<any[]>([]);
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchAdminData = async () => {
      try {
        const [anRes, userRes, logRes] = await Promise.all([
          apiClient.get('/admin/analytics'),
          apiClient.get('/admin/users'),
          apiClient.get('/admin/audit-logs')
        ]);
        setAnalytics(anRes.data);
        setUsers(userRes.data);
        setAuditLogs(logRes.data);
      } catch (err) {
        console.error('Failed to load admin dashboard:', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchAdminData();
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const kpis = [
    { title: 'Total Users', value: analytics?.total_users || 0, icon: Users, color: 'text-blue-600 bg-blue-50' },
    { title: 'Registered Learners', value: analytics?.total_learners || 0, icon: UserCheck, color: 'text-indigo-600 bg-indigo-50' },
    { title: 'Resumes Processed', value: analytics?.total_resumes_uploaded || 0, icon: FileText, color: 'text-emerald-600 bg-emerald-50' },
    { title: 'Master Skills', value: analytics?.total_skills_cataloged || 0, icon: ShieldCheck, color: 'text-purple-600 bg-purple-50' },
    { title: 'Courses Ingested', value: analytics?.total_courses_available || 0, icon: BookOpen, color: 'text-cyan-600 bg-cyan-50' },
    { title: 'Assessments Taken', value: analytics?.total_assessments_taken || 0, icon: CheckCircle2, color: 'text-amber-600 bg-amber-50' },
    { title: 'Active Jobs', value: analytics?.total_job_descriptions || 0, icon: Briefcase, color: 'text-teal-600 bg-teal-50' },
    { title: 'Reports Generated', value: analytics?.total_career_reports || 0, icon: Award, color: 'text-rose-600 bg-rose-50' },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">System Administration & Analytics</h1>
        <p className="text-sm text-slate-500 mt-1">
          Monitor system metrics, manage user roles, and inspect security audit trails in real time.
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {kpis.map((k, idx) => {
          const Icon = k.icon;
          return (
            <div key={idx} className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center space-x-4">
              <div className={`p-3 rounded-xl ${k.color}`}>
                <Icon className="w-5 h-5" />
              </div>
              <div>
                <span className="text-xs font-semibold text-slate-500 block">{k.title}</span>
                <span className="text-xl font-extrabold text-slate-900 block mt-0.5">{k.value}</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* User Management Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-6 border-b border-slate-200">
          <h3 className="text-base font-bold text-slate-900">User Management</h3>
          <p className="text-xs text-slate-500 mt-0.5">Active user accounts and assigned role privileges</p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-600 uppercase font-semibold">
              <tr>
                <th className="px-6 py-3">Full Name</th>
                <th className="px-6 py-3">Email</th>
                <th className="px-6 py-3">Role</th>
                <th className="px-6 py-3">Status</th>
                <th className="px-6 py-3">Registered On</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {users.map((u) => (
                <tr key={u.id} className="hover:bg-slate-50/50">
                  <td className="px-6 py-3.5 font-bold text-slate-900">{u.full_name}</td>
                  <td className="px-6 py-3.5 text-slate-600">{u.email}</td>
                  <td className="px-6 py-3.5">
                    <span className="px-2 py-0.5 rounded font-bold uppercase text-[10px] bg-slate-100 text-slate-700">
                      {u.role}
                    </span>
                  </td>
                  <td className="px-6 py-3.5">
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                      u.is_active ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-700'
                    }`}>
                      {u.is_active ? 'ACTIVE' : 'DEACTIVATED'}
                    </span>
                  </td>
                  <td className="px-6 py-3.5 text-slate-500">{new Date(u.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Security Audit Trail */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-6 border-b border-slate-200">
          <h3 className="text-base font-bold text-slate-900">Security Audit Logs</h3>
          <p className="text-xs text-slate-500 mt-0.5">Immutable audit event logs with correlation IDs</p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-600 uppercase font-semibold">
              <tr>
                <th className="px-6 py-3">Timestamp</th>
                <th className="px-6 py-3">Action</th>
                <th className="px-6 py-3">Entity</th>
                <th className="px-6 py-3">Correlation ID</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {auditLogs.slice(0, 10).map((log) => (
                <tr key={log.id} className="hover:bg-slate-50/50">
                  <td className="px-6 py-3 text-slate-500 font-mono text-[11px]">{new Date(log.created_at).toLocaleString()}</td>
                  <td className="px-6 py-3 font-bold text-slate-800">{log.action}</td>
                  <td className="px-6 py-3 text-slate-600">{log.entity_name}</td>
                  <td className="px-6 py-3 font-mono text-[10px] text-slate-400">{log.correlation_id || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
