import React, { useState, useEffect } from 'react';
import { apiClient } from '../../services/api';
import { Assessment, AssessmentQuestion } from '../../types';
import { HelpCircle, CheckCircle2, XCircle, ArrowRight, Award, RotateCcw } from 'lucide-react';

export const AssessmentQuiz: React.FC = () => {
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [selectedAssessment, setSelectedAssessment] = useState<Assessment | null>(null);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const loadData = async () => {
    try {
      const [assRes, histRes] = await Promise.all([
        apiClient.get('/assessments/'),
        apiClient.get('/assessments/my/history')
      ]);
      setAssessments(assRes.data);
      setHistory(histRes.data);
      if (assRes.data.length > 0 && !selectedAssessment) {
        setSelectedAssessment(assRes.data[0]);
      }
    } catch (err) {
      console.error('Failed to load assessment data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSelectOption = (qId: string, option: string) => {
    setAnswers(prev => ({ ...prev, [qId]: option }));
  };

  const handleSubmit = async () => {
    if (!selectedAssessment) return;
    setIsSubmitting(true);
    try {
      const res = await apiClient.post(`/assessments/${selectedAssessment.id}/submit`, {
        assessment_id: selectedAssessment.id,
        answers: answers
      });
      setResult(res.data);
      loadData();
    } catch (err) {
      console.error('Failed to submit assessment:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReset = () => {
    setAnswers({});
    setResult(null);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Competency Verification Assessments</h1>
        <p className="text-sm text-slate-500 mt-1">
          Passing technical evaluations provides objective verification to elevate your skill proficiency to Advanced (Level 3) and Expert (Level 4).
        </p>
      </div>

      {/* Assessment Selector */}
      <div className="flex flex-wrap gap-3">
        {assessments.map((a) => (
          <button
            key={a.id}
            onClick={() => { setSelectedAssessment(a); handleReset(); }}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition shadow-sm ${
              selectedAssessment?.id === a.id
                ? 'bg-blue-600 text-white'
                : 'bg-white text-slate-700 hover:bg-slate-100 border border-slate-200'
            }`}
          >
            {a.title}
          </button>
        ))}
      </div>

      {selectedAssessment && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-8 space-y-6">
          <div className="flex items-start justify-between border-b border-slate-100 pb-4">
            <div>
              <h2 className="text-lg font-bold text-slate-900">{selectedAssessment.title}</h2>
              <p className="text-xs text-slate-500 mt-1">{selectedAssessment.description}</p>
            </div>
            <div className="text-right">
              <span className="text-xs font-bold text-slate-600 block">Passing Threshold</span>
              <span className="text-sm font-extrabold text-blue-600">{selectedAssessment.passing_score}%</span>
            </div>
          </div>

          {result ? (
            <div className="p-6 bg-slate-50 rounded-xl border border-slate-200 text-center space-y-4">
              <div className={`w-14 h-14 mx-auto rounded-full flex items-center justify-center ${
                result.passed ? 'bg-emerald-100 text-emerald-600' : 'bg-red-100 text-red-600'
              }`}>
                {result.passed ? <CheckCircle2 className="w-8 h-8" /> : <XCircle className="w-8 h-8" />}
              </div>
              <div>
                <h3 className="text-xl font-extrabold text-slate-900">
                  {result.passed ? 'Assessment Passed!' : 'Did Not Pass'}
                </h3>
                <p className="text-sm text-slate-600 mt-1">
                  You scored <span className="font-bold text-slate-900">{result.score_percentage}%</span> ({result.correct_count} of {result.total_questions} correct).
                </p>
                {result.passed && (
                  <p className="text-xs text-emerald-600 font-semibold mt-2">
                    🌟 Proficiency level for this skill has been automatically updated with verified assessment evidence.
                  </p>
                )}
              </div>
              <button
                onClick={handleReset}
                className="inline-flex items-center px-4 py-2 bg-slate-900 text-white text-xs font-semibold rounded-lg hover:bg-slate-800 transition"
              >
                <RotateCcw className="w-3.5 h-3.5 mr-2" />
                Retake Assessment
              </button>
            </div>
          ) : (
            <div className="space-y-6">
              {selectedAssessment.questions?.map((q, idx) => (
                <div key={q.id} className="p-5 bg-slate-50 rounded-xl border border-slate-200 space-y-3">
                  <p className="text-sm font-bold text-slate-900">
                    {idx + 1}. {q.question_text}
                  </p>
                  <div className="space-y-2">
                    {q.options?.map((opt, optIdx) => {
                      const isSelected = answers[q.id] === opt;
                      return (
                        <button
                          key={optIdx}
                          type="button"
                          onClick={() => handleSelectOption(q.id, opt)}
                          className={`w-full text-left px-4 py-2.5 rounded-lg text-xs font-medium transition border flex items-center justify-between ${
                            isSelected
                              ? 'bg-blue-600 text-white border-blue-600 shadow-sm'
                              : 'bg-white text-slate-700 hover:bg-slate-100 border-slate-200'
                          }`}
                        >
                          <span>{opt}</span>
                          <span className={`w-3.5 h-3.5 rounded-full border flex items-center justify-center ${
                            isSelected ? 'border-white bg-white' : 'border-slate-300'
                          }`}>
                            {isSelected && <span className="w-1.5 h-1.5 rounded-full bg-blue-600" />}
                          </span>
                        </button>
                      );
                    })}
                  </div>
                </div>
              ))}

              <div className="pt-2 flex justify-end">
                <button
                  onClick={handleSubmit}
                  disabled={isSubmitting || Object.keys(answers).length === 0}
                  className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg text-xs shadow-md transition disabled:opacity-50 flex items-center"
                >
                  {isSubmitting ? 'Grading Answers...' : (
                    <>
                      Submit Assessment for Evaluation <ArrowRight className="w-3.5 h-3.5 ml-2" />
                    </>
                  )}
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* History Table */}
      {history.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="p-5 border-b border-slate-200">
            <h3 className="text-sm font-bold text-slate-900">Your Assessment Verification History</h3>
          </div>
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-600 uppercase font-semibold">
              <tr>
                <th className="px-5 py-3">Assessment Title</th>
                <th className="px-5 py-3">Score</th>
                <th className="px-5 py-3">Status</th>
                <th className="px-5 py-3">Date Taken</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {history.map((h) => (
                <tr key={h.id} className="hover:bg-slate-50">
                  <td className="px-5 py-3 font-semibold text-slate-800">{h.assessment_title}</td>
                  <td className="px-5 py-3 font-bold">{h.score_percentage}%</td>
                  <td className="px-5 py-3">
                    <span className={`px-2 py-0.5 rounded-full font-semibold ${
                      h.passed ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-700'
                    }`}>
                      {h.passed ? 'PASSED' : 'FAILED'}
                    </span>
                  </td>
                  <td className="px-5 py-3 text-slate-500">{new Date(h.taken_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
