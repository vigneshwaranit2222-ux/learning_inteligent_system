import React, { useState, useEffect } from 'react';
import { apiClient } from '../../services/api';
import { Course } from '../../types';
import { BookOpen, Clock, Award, CheckCircle2, Search, ExternalLink } from 'lucide-react';

export const CourseCatalog: React.FC = () => {
  const [courses, setCourses] = useState<Course[]>([]);
  const [query, setQuery] = useState('');
  const [difficulty, setDifficulty] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [completingId, setCompletingId] = useState<string | null>(null);
  const [completedMap, setCompletedMap] = useState<Record<string, boolean>>({});

  const fetchCourses = async () => {
    try {
      const params: any = {};
      if (query) params.query = query;
      if (difficulty) params.difficulty = difficulty;
      const res = await apiClient.get('/courses/', { params });
      setCourses(res.data);
    } catch (err) {
      console.error('Failed to load courses:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchCourses();
  }, [difficulty]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchCourses();
  };

  const handleComplete = async (courseId: string) => {
    setCompletingId(courseId);
    try {
      await apiClient.post('/courses/complete', {
        course_id: courseId,
        completion_date: new Date().toISOString().split('T')[0],
        grade: 'Passed with Honors'
      });
      setCompletedMap(prev => ({ ...prev, [courseId]: true }));
    } catch (err) {
      console.error('Failed to submit completion:', err);
    } finally {
      setCompletingId(null);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Structured Course Catalog</h1>
          <p className="text-sm text-slate-500 mt-1">
            Complete accredited modules to fulfill verified learning outcomes and raise your demonstrated proficiency.
          </p>
        </div>

        <form onSubmit={handleSearch} className="flex items-center space-x-2">
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Search course title..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="pl-9 pr-4 py-2 bg-white border border-slate-200 rounded-lg text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-600"
            />
          </div>
          <select
            value={difficulty}
            onChange={(e) => setDifficulty(e.target.value)}
            className="px-3 py-2 bg-white border border-slate-200 rounded-lg text-xs text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-600"
          >
            <option value="">All Difficulties</option>
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>
          <button
            type="submit"
            className="px-4 py-2 bg-blue-600 text-white rounded-lg text-xs font-semibold hover:bg-blue-700 shadow"
          >
            Search
          </button>
        </form>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center min-h-[40vh]">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {courses.map((c) => {
            const isDone = completedMap[c.id];
            return (
              <div key={c.id} className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 flex flex-col justify-between hover:border-blue-400 transition-all">
                <div className="space-y-3">
                  <div className="flex items-start justify-between">
                    <span className="text-[11px] font-bold text-blue-600 bg-blue-50 px-2.5 py-1 rounded-full uppercase tracking-wider">
                      {c.difficulty}
                    </span>
                    <span className="text-xs text-slate-400 flex items-center">
                      <Clock className="w-3.5 h-3.5 mr-1" />
                      {c.estimated_hours}h
                    </span>
                  </div>

                  <h3 className="text-base font-bold text-slate-900 leading-snug">{c.title}</h3>
                  <p className="text-xs text-slate-500 font-medium">Provider: {c.provider}</p>
                  <p className="text-xs text-slate-600 line-clamp-2 leading-relaxed">{c.description}</p>

                  {/* Modules */}
                  {c.modules?.length > 0 && (
                    <div className="pt-2 border-t border-slate-100">
                      <p className="text-[11px] font-bold text-slate-700 uppercase tracking-wider mb-1.5">Syllabus Modules</p>
                      <ul className="text-xs text-slate-600 space-y-1">
                        {c.modules.map(m => (
                          <li key={m.id} className="truncate">• {m.title}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Learning Outcomes */}
                  {c.learning_outcomes?.length > 0 && (
                    <div className="pt-2 border-t border-slate-100">
                      <p className="text-[11px] font-bold text-slate-700 uppercase tracking-wider mb-1">Target Outcomes</p>
                      <div className="flex flex-wrap gap-1.5">
                        {c.learning_outcomes.map(lo => (
                          <span key={lo.id} className="text-[10px] bg-slate-100 text-slate-700 font-medium px-2 py-0.5 rounded">
                            Target Level {lo.target_proficiency}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between">
                  {c.url ? (
                    <a
                      href={c.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-blue-600 font-semibold flex items-center hover:underline"
                    >
                      Official Page <ExternalLink className="w-3 h-3 ml-1" />
                    </a>
                  ) : <div />}

                  <button
                    onClick={() => handleComplete(c.id)}
                    disabled={isDone || completingId === c.id}
                    className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold shadow-sm flex items-center transition ${
                      isDone
                        ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                        : 'bg-slate-900 text-white hover:bg-slate-800'
                    }`}
                  >
                    {isDone ? (
                      <>
                        <CheckCircle2 className="w-3.5 h-3.5 mr-1 text-emerald-600" />
                        Completed
                      </>
                    ) : completingId === c.id ? (
                      'Recording...'
                    ) : (
                      'Mark Completed'
                    )}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
