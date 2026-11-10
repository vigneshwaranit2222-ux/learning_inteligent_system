import React, { useState, useEffect } from 'react';
import { apiClient } from '../../services/api';
import { Recommendation } from '../../types';
import { Compass, CheckCircle2, Clock, ExternalLink, ArrowUpRight, Filter } from 'lucide-react';

export const RecommendationsList: React.FC = () => {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [filterPriority, setFilterPriority] = useState<string>('all');
  const [isLoading, setIsLoading] = useState(true);

  const fetchRecommendations = async () => {
    try {
      const res = await apiClient.get('/recommendations/');
      setRecommendations(res.data);
    } catch (err) {
      console.error('Failed to load recommendations:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const handleUpdateStatus = async (id: string, newStatus: string) => {
    try {
      await apiClient.patch(`/recommendations/${id}/status`, { status: newStatus });
      setRecommendations(prev =>
        prev.map(r => r.id === id ? { ...r, status: newStatus as any } : r)
      );
    } catch (err) {
      console.error('Failed to update status:', err);
    }
  };

  const filtered = recommendations.filter(r => {
    if (filterPriority === 'all') return true;
    return r.priority.toLowerCase() === filterPriority.toLowerCase();
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Personalized Learning Roadmap</h1>
          <p className="text-sm text-slate-500 mt-1">
            Actionable learning pathways targeting verified skill gaps with expected competencies and verified resources.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <Filter className="w-4 h-4 text-slate-400" />
          <select
            value={filterPriority}
            onChange={(e) => setFilterPriority(e.target.value)}
            className="px-3 py-1.5 bg-white border border-slate-200 rounded-lg text-xs font-semibold text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-600"
          >
            <option value="all">All Priorities</option>
            <option value="high">High Priority Gaps</option>
            <option value="medium">Medium Priority</option>
            <option value="low">Low Priority</option>
          </select>
        </div>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center min-h-[40vh]">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      ) : filtered.length === 0 ? (
        <div className="bg-white p-12 text-center rounded-2xl border border-slate-200 shadow-sm space-y-3">
          <Compass className="w-12 h-12 text-slate-400 mx-auto" />
          <h3 className="text-base font-bold text-slate-800">No Active Recommendations</h3>
          <p className="text-xs text-slate-500 max-w-md mx-auto">
            Evaluate your profile against a job description in the Job Explorer to generate customized recommendations.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {filtered.map((r) => {
            const priorityColors = {
              high: 'bg-red-50 text-red-700 border-red-200',
              medium: 'bg-amber-50 text-amber-700 border-amber-200',
              low: 'bg-blue-50 text-blue-700 border-blue-200',
            };

            return (
              <div
                key={r.id}
                className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center md:justify-between gap-5 hover:border-blue-400 transition"
              >
                <div className="space-y-2 flex-1">
                  <div className="flex items-center space-x-2.5">
                    <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-bold uppercase border ${priorityColors[r.priority] || 'bg-slate-100 text-slate-700'}`}>
                      {r.priority} Priority
                    </span>
                    <span className="text-xs font-bold text-slate-900 bg-slate-100 px-2 py-0.5 rounded">
                      Skill: {r.skill?.name}
                    </span>
                    {r.resource?.estimated_hours && (
                      <span className="text-xs text-slate-400 flex items-center">
                        <Clock className="w-3.5 h-3.5 mr-1" />
                        {r.resource.estimated_hours} hrs
                      </span>
                    )}
                  </div>

                  <h3 className="text-base font-bold text-slate-900">
                    {r.resource?.title || `Mastering ${r.skill?.name}`}
                  </h3>

                  <p className="text-xs text-slate-600 leading-relaxed">
                    <span className="font-semibold text-slate-700">Reason: </span>{r.reason}
                  </p>

                  <p className="text-xs text-blue-700 bg-blue-50/70 p-2.5 rounded-lg border border-blue-100">
                    <span className="font-semibold">Expected Outcome: </span>{r.expected_outcome}
                  </p>
                </div>

                <div className="flex md:flex-col items-center md:items-end justify-between md:justify-center gap-3">
                  {r.resource?.url && (
                    <a
                      href={r.resource.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold shadow-sm transition flex items-center"
                    >
                      Access Resource <ExternalLink className="w-3.5 h-3.5 ml-1.5" />
                    </a>
                  )}

                  <select
                    value={r.status}
                    onChange={(e) => handleUpdateStatus(r.id, e.target.value)}
                    className="px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs font-medium text-slate-700 focus:outline-none"
                  >
                    <option value="active">Active</option>
                    <option value="in_progress">In Progress</option>
                    <option value="completed">Completed</option>
                    <option value="dismissed">Dismissed</option>
                  </select>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
