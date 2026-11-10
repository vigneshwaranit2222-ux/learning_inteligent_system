import React, { useState, useEffect } from 'react';
import { apiClient } from '../../services/api';
import { DashboardStats, LearnerSkill } from '../../types';
import { 
  Award, CheckCircle2, AlertTriangle, Compass, 
  BookOpen, Target, ArrowRight, ShieldCheck, Sparkles 
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { 
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, 
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar 
} from 'recharts';

export const LearnerDashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [skills, setSkills] = useState<LearnerSkill[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const [statsRes, skillsRes] = await Promise.all([
          apiClient.get('/learners/dashboard'),
          apiClient.get('/learners/skills')
        ]);
        setStats(statsRes.data);
        setSkills(skillsRes.data);
      } catch (err) {
        console.error('Failed to load dashboard data:', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchDashboard();
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Calculate radar chart data for skills
  const radarData = skills.slice(0, 6).map(s => ({
    skill: s.skill?.name || 'Skill',
    level: s.proficiency_level,
    fullMark: 4
  }));

  // Category breakdown for bar chart
  const categoryCount: Record<string, number> = {};
  skills.forEach(s => {
    const cat = s.skill?.category?.name || 'General';
    categoryCount[cat] = (categoryCount[cat] || 0) + 1;
  });
  const barData = Object.entries(categoryCount).map(([category, count]) => ({ category, count }));

  return (
    <div className="space-y-8">
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-blue-900 via-blue-800 to-indigo-900 rounded-2xl p-8 text-white shadow-lg relative overflow-hidden">
        <div className="relative z-10 max-w-2xl">
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-blue-700/60 text-blue-200 border border-blue-500/30 mb-3">
            <Sparkles className="w-3.5 h-3.5 mr-1 text-blue-300" />
            AI Career Readiness Engine Active
          </span>
          <h1 className="text-3xl font-extrabold tracking-tight">
            Targeting: {stats?.target_job_title || 'Software Engineering'}
          </h1>
          <p className="mt-2 text-sm text-blue-200 leading-relaxed">
            Your capabilities are evaluated through deterministic multi-evidence scoring across resume records, verified projects, and assessments.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link
              to="/resumes"
              className="px-4 py-2 bg-white text-blue-900 text-xs font-bold rounded-lg hover:bg-blue-50 transition shadow"
            >
              Upload New Resume
            </Link>
            <Link
              to="/reports"
              className="px-4 py-2 bg-blue-700/60 border border-blue-400/30 text-white text-xs font-bold rounded-lg hover:bg-blue-700 transition"
            >
              View Readiness Report
            </Link>
          </div>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Career Readiness</span>
            <div className="p-2 bg-blue-50 text-blue-600 rounded-lg">
              <Award className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline">
            <span className="text-3xl font-extrabold text-slate-900">
              {stats?.career_readiness_score?.toFixed(1) || '0.0'}%
            </span>
            <span className="ml-2 text-xs text-slate-500">Skill Alignment</span>
          </div>
          <div className="w-full bg-slate-100 rounded-full h-1.5 mt-3">
            <div 
              className="bg-blue-600 h-1.5 rounded-full transition-all duration-500" 
              style={{ width: `${Math.min(100, stats?.career_readiness_score || 0)}%` }}
            />
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Identified Skills</span>
            <div className="p-2 bg-emerald-50 text-emerald-600 rounded-lg">
              <CheckCircle2 className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline">
            <span className="text-3xl font-extrabold text-slate-900">{stats?.total_skills_identified || 0}</span>
            <span className="ml-2 text-xs text-emerald-600 font-semibold">{stats?.matched_job_skills || 0} Job Matched</span>
          </div>
          <p className="text-xs text-slate-400 mt-2">Verified through resume & code</p>
        </div>

        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Skill Gaps</span>
            <div className="p-2 bg-amber-50 text-amber-600 rounded-lg">
              <AlertTriangle className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline">
            <span className="text-3xl font-extrabold text-slate-900">{stats?.skill_gaps || 0}</span>
            <span className="ml-2 text-xs text-amber-600 font-semibold">Priority Action Items</span>
          </div>
          <Link to="/jobs" className="text-xs text-blue-600 font-semibold mt-2 inline-block hover:underline">
            Inspect Gap Analysis &rarr;
          </Link>
        </div>

        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Recommendations</span>
            <div className="p-2 bg-indigo-50 text-indigo-600 rounded-lg">
              <Compass className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline">
            <span className="text-3xl font-extrabold text-slate-900">{stats?.active_recommendations || 0}</span>
            <span className="ml-2 text-xs text-indigo-600 font-semibold">Learning Actions</span>
          </div>
          <Link to="/recommendations" className="text-xs text-blue-600 font-semibold mt-2 inline-block hover:underline">
            Explore Learning Path &rarr;
          </Link>
        </div>
      </div>

      {/* Visualizations Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-base font-bold text-slate-900">Verified Proficiency Profile</h3>
            <span className="text-xs text-slate-500">Max Level: Expert (4)</span>
          </div>
          {radarData.length > 0 ? (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart data={radarData}>
                  <PolarGrid stroke="#e2e8f0" />
                  <PolarAngleAxis dataKey="skill" tick={{ fill: '#64748b', fontSize: 11 }} />
                  <PolarRadiusAxis domain={[0, 4]} tick={{ fill: '#94a3b8', fontSize: 10 }} />
                  <Radar name="Demonstrated Level" dataKey="level" stroke="#2563eb" fill="#3b82f6" fillOpacity={0.4} />
                  <Tooltip />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="h-64 flex flex-col items-center justify-center text-slate-400">
              <BookOpen className="w-10 h-10 mb-2 stroke-1" />
              <p className="text-sm">No skill evidence recorded yet.</p>
              <Link to="/resumes" className="text-xs text-blue-600 font-semibold mt-1">Upload Resume to Start</Link>
            </div>
          )}
        </div>

        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-base font-bold text-slate-900">Skills by Domain Category</h3>
            <span className="text-xs text-slate-500">Total: {skills.length}</span>
          </div>
          {barData.length > 0 ? (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={barData}>
                  <XAxis dataKey="category" tick={{ fill: '#64748b', fontSize: 11 }} />
                  <YAxis tick={{ fill: '#94a3b8', fontSize: 10 }} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="h-64 flex flex-col items-center justify-center text-slate-400">
              <Target className="w-10 h-10 mb-2 stroke-1" />
              <p className="text-sm">Categories will appear after skill extraction.</p>
            </div>
          )}
        </div>
      </div>

      {/* Identified Skills Table with Verifiable Evidence */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-6 border-b border-slate-200 flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-slate-900">Demonstrated Skills & Stored Evidence</h3>
            <p className="text-xs text-slate-500 mt-0.5">Every skill level is supported by stored evidence records</p>
          </div>
          <Link to="/resumes" className="text-xs text-blue-600 font-semibold hover:underline flex items-center">
            Upload More Evidence <ArrowRight className="w-3.5 h-3.5 ml-1" />
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-slate-600 text-xs uppercase font-semibold border-b border-slate-200">
              <tr>
                <th className="px-6 py-3">Skill</th>
                <th className="px-6 py-3">Category</th>
                <th className="px-6 py-3">Proficiency Level</th>
                <th className="px-6 py-3">Confidence</th>
                <th className="px-6 py-3">Supporting Evidence</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {skills.map((item) => {
                const levelLabels = ["Unrated", "Beginner", "Intermediate", "Advanced", "Expert"];
                const levelColors = [
                  "bg-slate-100 text-slate-600",
                  "bg-blue-50 text-blue-700 border-blue-200",
                  "bg-indigo-50 text-indigo-700 border-indigo-200",
                  "bg-purple-50 text-purple-700 border-purple-200",
                  "bg-emerald-50 text-emerald-700 border-emerald-200"
                ];

                return (
                  <tr key={item.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="px-6 py-4 font-semibold text-slate-900">
                      {item.skill?.name}
                    </td>
                    <td className="px-6 py-4 text-slate-600 text-xs">
                      {item.skill?.category?.name || 'General'}
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${levelColors[item.proficiency_level] || 'bg-slate-100 text-slate-700'}`}>
                        L{item.proficiency_level} - {levelLabels[item.proficiency_level] || 'Intermediate'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-xs font-medium text-slate-600">
                      {Math.round(item.confidence_score * 100)}%
                    </td>
                    <td className="px-6 py-4 text-xs text-slate-500 max-w-md truncate">
                      {item.evidence_summary || (item.evidence_list?.[0]?.text_snippet) || 'Evidence stored in database'}
                    </td>
                  </tr>
                );
              })}
              {skills.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-slate-400">
                    No skills identified yet. Upload a resume to automatically extract verified skills.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
