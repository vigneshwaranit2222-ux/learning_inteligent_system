import React, { useState, useEffect } from 'react';
import { apiClient } from '../../services/api';
import { JobDescription, MatchingResult } from '../../types';
import { Briefcase, MapPin, Building, Target, CheckCircle2, AlertTriangle, ArrowRight, Sparkles } from 'lucide-react';
import { Link } from 'react-router-dom';

export const JobExplorer: React.FC = () => {
  const [jobs, setJobs] = useState<JobDescription[]>([]);
  const [selectedJob, setSelectedJob] = useState<JobDescription | null>(null);
  const [matchingResult, setMatchingResult] = useState<MatchingResult | null>(null);
  const [isMatching, setIsMatching] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const res = await apiClient.get('/jobs/');
        setJobs(res.data);
        if (res.data.length > 0) {
          setSelectedJob(res.data[0]);
        }
      } catch (err) {
        console.error('Failed to load jobs:', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchJobs();
  }, []);

  const handleRunMatch = async (jobId: string) => {
    setIsMatching(true);
    setMatchingResult(null);
    try {
      const res = await apiClient.post(`/matching/match/${jobId}`);
      setMatchingResult(res.data);
    } catch (err) {
      console.error('Matching failed:', err);
    } finally {
      setIsMatching(false);
    }
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
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Job Market Alignment & Gap Analysis</h1>
        <p className="text-sm text-slate-500 mt-1">
          Compare your demonstrated profile against target employer requirements using deterministic matching formulas.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Job Cards */}
        <div className="space-y-4">
          <h2 className="text-xs font-bold text-slate-500 uppercase tracking-wider">Available Positions</h2>
          {jobs.map((j) => (
            <div
              key={j.id}
              onClick={() => { setSelectedJob(j); setMatchingResult(null); }}
              className={`p-5 rounded-xl border transition cursor-pointer ${
                selectedJob?.id === j.id
                  ? 'bg-blue-50/50 border-blue-600 shadow-sm'
                  : 'bg-white border-slate-200 hover:border-slate-300'
              }`}
            >
              <h3 className="text-sm font-bold text-slate-900">{j.title}</h3>
              <p className="text-xs text-slate-600 flex items-center mt-1">
                <Building className="w-3.5 h-3.5 mr-1 text-slate-400" />
                {j.company_name}
              </p>
              <p className="text-xs text-slate-500 flex items-center mt-1">
                <MapPin className="w-3.5 h-3.5 mr-1 text-slate-400" />
                {j.location || 'Remote'}
              </p>
            </div>
          ))}
        </div>

        {/* Right: Job Details & Matching Engine */}
        <div className="lg:col-span-2 space-y-6">
          {selectedJob && (
            <div className="bg-white p-7 rounded-2xl border border-slate-200 shadow-sm space-y-6">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-100 pb-5">
                <div>
                  <h2 className="text-xl font-bold text-slate-900">{selectedJob.title}</h2>
                  <p className="text-sm text-slate-500 font-medium mt-0.5">{selectedJob.company_name} • {selectedJob.employment_type}</p>
                </div>
                <button
                  onClick={() => handleRunMatch(selectedJob.id)}
                  disabled={isMatching}
                  className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg text-xs shadow-md transition flex items-center justify-center disabled:opacity-50"
                >
                  {isMatching ? (
                    'Evaluating Alignment...'
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4 mr-2" />
                      Evaluate My Readiness
                    </>
                  )}
                </button>
              </div>

              {/* Requirements Tags */}
              <div>
                <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2.5">
                  Required Competencies ({selectedJob.requirements?.length || 0})
                </h4>
                <div className="flex flex-wrap gap-2">
                  {selectedJob.requirements?.map((req) => (
                    <span
                      key={req.id}
                      className={`text-xs px-2.5 py-1 rounded-lg font-medium border ${
                        req.requirement_type === 'mandatory'
                          ? 'bg-red-50 text-red-700 border-red-200'
                          : 'bg-slate-50 text-slate-700 border-slate-200'
                      }`}
                    >
                      {req.skill?.name} (L{req.required_level}) - {req.requirement_type}
                    </span>
                  ))}
                </div>
              </div>

              {/* Raw Job Excerpt */}
              <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 text-xs text-slate-600 leading-relaxed font-mono whitespace-pre-wrap">
                {selectedJob.raw_text}
              </div>

              {/* Matching Result Display */}
              {matchingResult && (
                <div className="border-t border-slate-200 pt-6 space-y-6">
                  <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-xl border border-blue-200 flex items-center justify-between">
                    <div>
                      <span className="text-xs font-bold text-blue-700 uppercase tracking-wider">Calculated Readiness Score</span>
                      <div className="text-3xl font-extrabold text-blue-950 mt-1">
                        {matchingResult.readiness_score}%
                      </div>
                      <p className="text-xs text-blue-700 mt-1">
                        Matched {matchingResult.matched_count} of {matchingResult.total_required_skills} competencies.
                      </p>
                    </div>
                    <div className="flex space-x-2">
                      <Link
                        to="/recommendations"
                        className="px-4 py-2 bg-blue-600 text-white font-semibold text-xs rounded-lg hover:bg-blue-700 transition shadow"
                      >
                        View Recommendations
                      </Link>
                      <Link
                        to="/reports"
                        className="px-4 py-2 bg-white text-slate-800 border border-slate-200 font-semibold text-xs rounded-lg hover:bg-slate-50 transition"
                      >
                        Generate PDF Report
                      </Link>
                    </div>
                  </div>

                  {/* Skill Gaps Breakdown */}
                  {matchingResult.gaps?.length > 0 && (
                    <div>
                      <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-3">
                        Identified Skill Gaps ({matchingResult.gaps.length})
                      </h4>
                      <div className="space-y-2">
                        {matchingResult.gaps.map((g, idx) => (
                          <div
                            key={idx}
                            className={`p-3 rounded-lg border text-xs flex items-center justify-between ${
                              g.gap_severity === 'critical'
                                ? 'bg-red-50/50 border-red-200 text-red-900'
                                : 'bg-amber-50/50 border-amber-200 text-amber-900'
                            }`}
                          >
                            <div className="flex items-center space-x-2">
                              <AlertTriangle className={`w-4 h-4 ${g.gap_severity === 'critical' ? 'text-red-500' : 'text-amber-500'}`} />
                              <span className="font-bold">{g.skill_name}</span>
                              <span className="text-slate-500">({g.category})</span>
                            </div>
                            <div className="flex items-center space-x-3">
                              <span>Current: L{g.current_level} &rarr; Target: L{g.required_level}</span>
                              <span className={`px-2 py-0.5 rounded-full font-bold uppercase text-[10px] ${
                                g.gap_severity === 'critical' ? 'bg-red-100 text-red-700' : 'bg-amber-100 text-amber-700'
                              }`}>
                                {g.gap_severity}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
