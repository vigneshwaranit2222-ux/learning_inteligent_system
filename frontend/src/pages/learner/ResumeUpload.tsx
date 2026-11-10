import React, { useState } from 'react';
import { apiClient } from '../../services/api';
import { UploadCloud, FileText, CheckCircle2, AlertCircle, Sparkles } from 'lucide-react';

export const ResumeUpload: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError('');
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setIsUploading(true);
    setError('');
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await apiClient.post('/resumes/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setResult(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to upload and process resume.');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Resume Ingestion & AI Skill Extraction</h1>
        <p className="text-sm text-slate-500 mt-1">
          Upload PDF, DOCX, or TXT resumes. The hybrid extraction engine matches canonical technologies, detects aliases, and extracts verbatim quotes as audit evidence.
        </p>
      </div>

      <div className="bg-white p-8 rounded-2xl border-2 border-dashed border-slate-300 hover:border-blue-500 transition-colors text-center shadow-sm">
        <input
          type="file"
          id="resume-file"
          accept=".pdf,.docx,.doc,.txt"
          onChange={handleFileChange}
          className="hidden"
        />
        <label htmlFor="resume-file" className="cursor-pointer flex flex-col items-center">
          <div className="w-16 h-16 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center mb-4">
            <UploadCloud className="w-8 h-8" />
          </div>
          <span className="text-sm font-semibold text-slate-800">
            {file ? file.name : 'Click to select or drag and drop your resume'}
          </span>
          <span className="text-xs text-slate-400 mt-1">Supported formats: PDF, DOCX, TXT (Max 10MB)</span>
        </label>

        {file && (
          <div className="mt-6 flex items-center justify-center space-x-3">
            <button
              onClick={handleUpload}
              disabled={isUploading}
              className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg text-sm shadow-md transition disabled:opacity-50 flex items-center"
            >
              {isUploading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2" />
                  Extracting Skills & Evidence...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 mr-2" />
                  Process & Extract Skills
                </>
              )}
            </button>
          </div>
        )}
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm flex items-center">
          <AlertCircle className="w-5 h-5 mr-3 flex-shrink-0" />
          {error}
        </div>
      )}

      {result && (
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center space-x-3 text-emerald-600">
            <CheckCircle2 className="w-6 h-6" />
            <div>
              <h3 className="text-base font-bold text-slate-900">{result.message}</h3>
              <p className="text-xs text-slate-500">Document ID: {result.resume_id}</p>
            </div>
          </div>

          <div className="border-t border-slate-100 pt-4">
            <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-3">
              Extracted Skills & Context Snippets ({result.skills?.length || 0})
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {result.skills?.map((item: any, idx: number) => (
                <div key={idx} className="p-3 bg-slate-50 rounded-lg border border-slate-200 text-xs">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-bold text-slate-900">{item.canonical_name}</span>
                    <span className="text-[10px] bg-blue-100 text-blue-800 font-semibold px-2 py-0.5 rounded-full">
                      {Math.round(item.confidence * 100)}% Conf
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-500 mb-1">Category: {item.category}</p>
                  <p className="text-slate-600 italic bg-white p-2 rounded border border-slate-100">
                    "{item.evidence_snippet}"
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
