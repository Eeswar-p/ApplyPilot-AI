import { useState, useEffect, useRef, type ChangeEvent, type DragEvent } from 'react';
import {
  FileText,
  UploadCloud,
  CheckCircle2,
  Trash2,
  Star,
  Eye,
  AlertCircle,
  Loader2,
  X,
  FileCheck,
} from 'lucide-react';
import { resumesApi, type ResumeData } from '../services/api';

export default function ResumeManager() {
  const [resumes, setResumes] = useState<ResumeData[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Preview Modal
  const [previewResume, setPreviewResume] = useState<ResumeData | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);

  // Drag & drop state
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadResumes = async () => {
    try {
      setLoading(true);
      const data = await resumesApi.list();
      setResumes(data.resumes);
    } catch (err: any) {
      setErrorMessage(err.response?.data?.error || 'Failed to load resumes');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadResumes();
  }, []);

  const handleFileUpload = async (file: File) => {
    const validExtensions = ['pdf', 'docx'];
    const ext = file.name.split('.').pop()?.toLowerCase();

    if (!ext || !validExtensions.includes(ext)) {
      setErrorMessage('Please upload a valid PDF (.pdf) or Word document (.docx)');
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setErrorMessage('File size exceeds the 10 MB limit');
      return;
    }

    try {
      setUploading(true);
      setErrorMessage(null);
      await resumesApi.upload(file);
      setSuccessMessage(`Resume "${file.name}" uploaded and parsed successfully!`);
      setTimeout(() => setSuccessMessage(null), 4000);
      await loadResumes();
    } catch (err: any) {
      setErrorMessage(err.response?.data?.error || 'Failed to upload resume');
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const onFileInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileUpload(e.target.files[0]);
    }
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  const handleSetPrimary = async (id: number) => {
    try {
      await resumesApi.setPrimary(id);
      setSuccessMessage('Primary resume updated');
      setTimeout(() => setSuccessMessage(null), 3000);
      await loadResumes();
    } catch (err: any) {
      setErrorMessage(err.response?.data?.error || 'Failed to update primary resume');
    }
  };

  const handleDelete = async (id: number, filename: string) => {
    if (!window.confirm(`Are you sure you want to delete "${filename}"?`)) {
      return;
    }
    try {
      await resumesApi.delete(id);
      setSuccessMessage('Resume deleted successfully');
      setTimeout(() => setSuccessMessage(null), 3000);
      await loadResumes();
    } catch (err: any) {
      setErrorMessage(err.response?.data?.error || 'Failed to delete resume');
    }
  };

  const handleOpenPreview = async (id: number) => {
    try {
      setPreviewLoading(true);
      const data = await resumesApi.getById(id);
      setPreviewResume(data.resume);
    } catch (err: any) {
      setErrorMessage(err.response?.data?.error || 'Failed to load preview');
    } finally {
      setPreviewLoading(false);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  return (
    <div className="space-y-6 max-w-5xl pb-12">
      {/* Page Title */}
      <div>
        <h1 className="text-3xl font-bold text-white tracking-tight">Resume Management</h1>
        <p className="text-slate-400 text-sm mt-1">
          Upload PDF or DOCX resumes. The automation engine extracts key qualifications and submits your designated primary resume to application forms.
        </p>
      </div>

      {/* Status Banners */}
      {successMessage && (
        <div className="p-3.5 bg-green-500/10 border border-green-500/30 rounded-xl flex items-center gap-2.5 text-green-400 text-sm">
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          <span>{successMessage}</span>
        </div>
      )}
      {errorMessage && (
        <div className="p-3.5 bg-red-500/10 border border-red-500/30 rounded-xl flex items-center gap-2.5 text-red-400 text-sm">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Upload Drop Zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`glass-panel p-8 sm:p-12 rounded-2xl border-2 border-dashed transition-all cursor-pointer text-center flex flex-col items-center justify-center ${
          isDragging
            ? 'border-primary-500 bg-primary-500/10 scale-[1.01]'
            : 'border-slate-700/80 hover:border-primary-500/50 hover:bg-surfaceHighlight/30'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
          onChange={onFileInputChange}
          className="hidden"
        />

        <div className="w-14 h-14 rounded-2xl bg-primary-500/10 border border-primary-500/20 flex items-center justify-center mb-4 text-primary-400">
          {uploading ? (
            <Loader2 className="w-7 h-7 animate-spin" />
          ) : (
            <UploadCloud className="w-7 h-7" />
          )}
        </div>

        <h3 className="text-base font-semibold text-white">
          {uploading ? 'Uploading and parsing document...' : 'Click or drag and drop your resume here'}
        </h3>
        <p className="text-xs text-slate-400 mt-1 max-w-sm">
          Supports PDF and Microsoft Word (.docx) up to 10 MB.
        </p>

        <button
          type="button"
          disabled={uploading}
          className="btn-primary mt-5 text-xs py-2 px-5 flex items-center gap-2"
        >
          <UploadCloud className="w-4 h-4" />
          <span>Select Document</span>
        </button>
      </div>

      {/* Resumes List */}
      <div className="space-y-3">
        <h2 className="text-lg font-semibold text-white tracking-tight">Your Resumes ({resumes.length})</h2>

        {loading ? (
          <div className="glass-panel p-8 rounded-xl flex items-center justify-center text-slate-400 gap-3">
            <Loader2 className="w-5 h-5 animate-spin text-primary-500" />
            <span className="text-sm">Loading resumes...</span>
          </div>
        ) : resumes.length === 0 ? (
          <div className="glass-panel p-12 text-center rounded-2xl text-slate-400">
            <FileText className="w-12 h-12 mx-auto mb-3 opacity-30 text-primary-400" />
            <p className="font-medium text-white">No resumes uploaded yet</p>
            <p className="text-xs text-slate-500 mt-1">Upload your primary resume above to enable automated applications.</p>
          </div>
        ) : (
          <div className="grid gap-3">
            {resumes.map((resume) => (
              <div
                key={resume.id}
                className={`glass-panel p-5 rounded-2xl flex flex-col sm:flex-row sm:items-center justify-between gap-4 transition-all ${
                  resume.is_primary ? 'border-primary-500/40 bg-primary-500/5 shadow-lg shadow-primary-500/5' : ''
                }`}
              >
                <div className="flex items-start gap-4">
                  <div className={`p-3 rounded-xl shrink-0 ${
                    resume.file_type === 'pdf'
                      ? 'bg-red-500/10 text-red-400 border border-red-500/20'
                      : 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
                  }`}>
                    <FileText className="w-6 h-6" />
                  </div>

                  <div>
                    <div className="flex items-center gap-2.5 flex-wrap">
                      <h4 className="font-semibold text-white text-base">{resume.filename}</h4>
                      {resume.is_primary && (
                        <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-primary-500/20 text-primary-300 border border-primary-500/30 flex items-center gap-1">
                          <Star className="w-3 h-3 fill-primary-400 text-primary-400" /> Primary
                        </span>
                      )}
                    </div>

                    <div className="flex items-center gap-3 mt-1.5 text-xs text-slate-400">
                      <span className="uppercase font-mono text-[11px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">
                        {resume.file_type}
                      </span>
                      <span>{formatFileSize(resume.file_size)}</span>
                      <span>•</span>
                      <span>Uploaded {new Date(resume.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2 self-end sm:self-center">
                  {!resume.is_primary && (
                    <button
                      onClick={() => handleSetPrimary(resume.id)}
                      className="px-3 py-1.5 text-xs font-medium text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg transition-colors flex items-center gap-1.5 cursor-pointer"
                    >
                      <FileCheck className="w-3.5 h-3.5 text-primary-400" /> Set Primary
                    </button>
                  )}

                  <button
                    onClick={() => handleOpenPreview(resume.id)}
                    className="p-2 text-slate-400 hover:text-white hover:bg-surfaceHighlight rounded-lg transition-colors cursor-pointer"
                    title="Preview extracted text"
                  >
                    <Eye className="w-4 h-4" />
                  </button>

                  <button
                    onClick={() => handleDelete(resume.id, resume.filename)}
                    className="p-2 text-slate-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors cursor-pointer"
                    title="Delete resume"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Preview Extracted Text Modal */}
      {previewResume && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-panel w-full max-w-3xl max-h-[85vh] rounded-2xl flex flex-col overflow-hidden border-slate-700">
            <div className="p-5 border-b border-slate-700/60 flex items-center justify-between bg-surface/70">
              <div className="flex items-center gap-2.5">
                <FileText className="w-5 h-5 text-primary-400" />
                <h3 className="font-semibold text-white text-base truncate max-w-md">
                  Extracted Content: {previewResume.filename}
                </h3>
              </div>
              <button
                onClick={() => setPreviewResume(null)}
                className="p-1.5 text-slate-400 hover:text-white hover:bg-surfaceHighlight rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 overflow-y-auto flex-1 text-sm text-slate-300 font-mono whitespace-pre-wrap leading-relaxed bg-slate-950/60">
              {previewLoading ? (
                <div className="flex items-center justify-center py-12 text-slate-400 gap-2">
                  <Loader2 className="w-5 h-5 animate-spin" /> Loading content...
                </div>
              ) : previewResume.parsed_text ? (
                previewResume.parsed_text
              ) : (
                <span className="text-slate-500 italic">No text could be extracted from this document.</span>
              )}
            </div>

            <div className="p-4 border-t border-slate-700/60 flex justify-end bg-surface/50">
              <button
                onClick={() => setPreviewResume(null)}
                className="btn-primary text-xs py-2 px-5"
              >
                Close Preview
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
