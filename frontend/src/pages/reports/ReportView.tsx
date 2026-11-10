import React, { useState, useEffect } from 'react';
import { apiClient } from '../../services/api';
import { CareerReport } from '../../types';
import { Award, Download, FileText, Calendar, Building, Sparkles } from 'lucide-react';

export const ReportView: React.FC = () => {
  const [reports, setReports] = useState<CareerReport[]>([]);
  const [selectedReport, setSelectedReport] = useState<CareerReport | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchReports = async () => {
      try {
        const res = await apiClient.get('/reports/');
        setReports(res.data);
        if (res.data.length > 0) {
          setSelectedReport(res.data[0]);
        }
      } catch (err) {
        console.error('Failed to load reports:', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchReports();
  }, []);

  const handleDownloadPDF = (reportId: string) => {
    window.open(`http://localhost:8000/api/v1/reports/${reportId}/pdf`, '_blank');
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Career Readiness Audit Reports</h1>
        <p className="text-sm text-slate-500 mt-1">
          Detailed, explainable audits with mathematical breakdown and downloadable PDF reports.
        </p>
      </div>

      {reports.length === 0 ? (
        <div className="bg-white p-12 text-center rounded-2xl border border-slate-200 shadow-sm space-y-3">
          <Award className="w-12 h-12 text-slate-400 mx-auto" />
          <h3 className="text-base font-bold text-slate-800">No Career Reports Generated Yet</h3>
          <p className="text-xs text-slate-500 max-w-md mx-auto">
            Evaluate your skills against a target role in the Job Explorer to generate your first audit report.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column: Report List */}
          <div className="space-y-3">
            <h2 className="text-xs font-bold text-slate-500 uppercase tracking-wider">Report History</h2>
            {reports.map((r) => (
              <div
                key={r.id}
                onClick={() => setSelectedReport(r)}
                className={`p-4 rounded-xl border transition cursor-pointer ${
                  selectedReport?.id === r.id
                    ? 'bg-blue-50/50 border-blue-600 shadow-sm'
                    : 'bg-white border-slate-200 hover:border-slate-300'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-bold text-slate-900">{r.job_title}</span>
                  <span className="text-xs font-extrabold text-blue-600">{r.overall_readiness_score}%</span>
                </div>
                <p className="text-xs text-slate-500">{r.company_name}</p>
                <p className="text-[11px] text-slate-400 mt-2 flex items-center">
                  <Calendar className="w-3 h-3 mr-1" />
                  {new Date(r.generated_at).toLocaleDateString()}
                </p>
              </div>
            ))}
          </div>

          {/* Right Column: Active Report View */}
          <div className="lg:col-span-2">
            {selectedReport && (
              <div className="bg-white p-8 rounded-2xl border border-slate-200 shadow-sm space-y-6">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-100 pb-6">
                  <div>
                    <span className="text-xs font-bold text-blue-600 uppercase tracking-wider">Official Audit Report</span>
                    <h2 className="text-2xl font-extrabold text-slate-900 mt-1">{selectedReport.job_title}</h2>
                    <p className="text-sm text-slate-500 flex items-center mt-1">
                      <Building className="w-4 h-4 mr-1 text-slate-400" />
                      {selectedReport.company_name} • Generated {new Date(selectedReport.generated_at).toLocaleDateString()}
                    </p>
                  </div>
                  <button
                    onClick={() => handleDownloadPDF(selectedReport.id)}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg text-xs shadow-md transition flex items-center self-start sm:self-auto"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Download PDF Report
                  </button>
                </div>

                {/* Score Summary Box */}
                <div className="p-6 bg-slate-50 rounded-xl border border-slate-200 flex items-center justify-between">
                  <div>
                    <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Overall Readiness Score</span>
                    <div className="text-4xl font-extrabold text-slate-900 mt-1">
                      {selectedReport.overall_readiness_score}%
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Status</span>
                    <div className="text-base font-bold text-blue-600 mt-1">
                      {selectedReport.overall_readiness_score >= 80 ? 'Job Ready' : selectedReport.overall_readiness_score >= 50 ? 'Developing' : 'Upskilling Required'}
                    </div>
                  </div>
                </div>

                {/* Executive Summary */}
                <div>
                  <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">Executive Summary</h4>
                  <p className="text-xs text-slate-700 leading-relaxed bg-white p-4 rounded-xl border border-slate-200">
                    {selectedReport.executive_summary}
                  </p>
                </div>

                {/* Matches Table */}
                {selectedReport.breakdown?.matches && (
                  <div>
                    <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-3">
                      Competency Verification Trace ({selectedReport.breakdown.matches.length})
                    </h4>
                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-xs">
                        <thead className="bg-slate-50 text-slate-600 uppercase font-semibold">
                          <tr>
                            <th className="px-4 py-2.5">Competency</th>
                            <th className="px-4 py-2.5">Status</th>
                            <th className="px-4 py-2.5">Demonstrated</th>
                            <th className="px-4 py-2.5">Required</th>
                            <th className="px-4 py-2.5">Weight</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                          {selectedReport.breakdown.matches.map((m: any, idx: number) => (
                            <tr key={idx} className="hover:bg-slate-50/50">
                              <td className="px-4 py-2.5 font-bold text-slate-900">{m.skill_name}</td>
                              <td className="px-4 py-2.5">
                                <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${
                                  m.match_type === 'matched' ? 'bg-emerald-100 text-emerald-800' :
                                  m.match_type === 'exceeds' ? 'bg-green-100 text-green-800' :
                                  m.match_type === 'partial' ? 'bg-amber-100 text-amber-800' : 'bg-red-100 text-red-800'
                                }`}>
                                  {m.match_type}
                                </span>
                              </td>
                              <td className="px-4 py-2.5 text-slate-600">Level {m.learner_level}</td>
                              <td className="px-4 py-2.5 text-slate-600">Level {m.required_level}</td>
                              <td className="px-4 py-2.5 text-slate-500">{m.importance_weight}x</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
