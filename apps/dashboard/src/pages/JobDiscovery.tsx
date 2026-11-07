import { useState, useEffect } from 'react';
import {
  Compass,
  Search,
  Building,
  MapPin,
  ExternalLink,
  RotateCw,
  CheckCircle2,
  AlertCircle,
  Briefcase,
  IndianRupee,
  Sparkles,
  X,
  Loader2,
  ChevronLeft,
  ChevronRight,
  ShieldCheck,
} from 'lucide-react';
import { jobsApi, eligibilityApi, type JobItemData, type EligibilityEvaluationData } from '../services/api';

export default function JobDiscovery() {
  const [jobs, setJobs] = useState<JobItemData[]>([]);
  const [loading, setLoading] = useState(true);
  const [discovering, setDiscovering] = useState(false);
  const [evaluating, setEvaluating] = useState(false);
  const [search, setSearch] = useState('');
  const [sourceFilter, setSourceFilter] = useState('all');
  const [typeFilter, setTypeFilter] = useState('all');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalJobs, setTotalJobs] = useState(0);

  // Modal & Detailed evaluation state
  const [selectedJob, setSelectedJob] = useState<JobItemData | null>(null);
  const [evaluationData, setEvaluationData] = useState<EligibilityEvaluationData | null>(null);
  const [evalLoading, setEvalLoading] = useState(false);

  // Status messages
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const fetchJobs = async () => {
    try {
      setLoading(true);
      const data = await jobsApi.list({
        search: search || undefined,
        source: sourceFilter !== 'all' ? sourceFilter : undefined,
        employment_type: typeFilter !== 'all' ? typeFilter : undefined,
        page,
        per_page: 9,
      });
      setJobs(data.jobs);
      setTotalPages(data.pages);
      setTotalJobs(data.total);
    } catch (err: any) {
      setErrorMessage(err.response?.data?.error || 'Failed to load jobs');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, [page, sourceFilter, typeFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchJobs();
  };

  const handleRunDiscovery = async () => {
    try {
      setDiscovering(true);
      setErrorMessage(null);
      const res = await jobsApi.discover();
      setSuccessMessage(
        `Discovery completed! Evaluated ${res.stats?.total_evaluated || 0} feeds, linked ${res.stats?.new_applications_linked || 0} relevant matches.`
      );
      setTimeout(() => setSuccessMessage(null), 4500);
      setPage(1);
      await fetchJobs();
    } catch (err: any) {
      setErrorMessage(err.response?.data?.error || 'Discovery scan failed');
    } finally {
      setDiscovering(false);
    }
  };

  const handleBatchEvaluate = async () => {
    try {
      setEvaluating(true);
      setErrorMessage(null);
      const res = await eligibilityApi.evaluate();
      setSuccessMessage(res.message);
      setTimeout(() => setSuccessMessage(null), 4500);
      await fetchJobs();
    } catch (err: any) {
      setErrorMessage(err.response?.data?.error || 'Eligibility evaluation failed');
    } finally {
      setEvaluating(false);
    }
  };

  const openJobModal = async (job: JobItemData) => {
    setSelectedJob(job);
    setEvaluationData(null);
    setEvalLoading(true);
    try {
      const res = await eligibilityApi.getBreakdown(job.id);
      setEvaluationData(res.evaluation);
    } catch {
      // Fallback silently if breakdown cannot be loaded immediately
    } finally {
      setEvalLoading(false);
    }
  };

  const getSourceBadge = (source: string) => {
    const s = source.toLowerCase();
    if (s === 'linkedin') {
      return <span className="px-2 py-0.5 rounded-full text-[11px] font-semibold bg-blue-500/20 text-blue-400 border border-blue-500/30">LinkedIn</span>;
    }
    if (s === 'internshala') {
      return <span className="px-2 py-0.5 rounded-full text-[11px] font-semibold bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">Internshala</span>;
    }
    if (s === 'indeed') {
      return <span className="px-2 py-0.5 rounded-full text-[11px] font-semibold bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">Indeed</span>;
    }
    return <span className="px-2 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">Career Portal</span>;
  };

  const getScoreBadge = (score?: number, category?: string) => {
    if (!score || score === 0) {
      return (
        <span className="px-2 py-0.5 rounded-full text-[10px] font-medium bg-slate-800 text-slate-400 border border-slate-700">
          Unranked
        </span>
      );
    }
    if (score >= 75) {
      return (
        <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-green-500/20 text-green-300 border border-green-500/40 flex items-center gap-1 shadow-sm shadow-green-500/20">
          <Sparkles className="w-3 h-3 text-green-400" /> {score}% Match
        </span>
      );
    }
    if (score >= 50) {
      return (
        <span className="px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-amber-500/20 text-amber-300 border border-amber-500/30 flex items-center gap-1">
          {score}% Match
        </span>
      );
    }
    return (
      <span className="px-2 py-0.5 rounded-full text-[10px] font-medium bg-red-500/10 text-red-400 border border-red-500/20">
        {score}% Match ({category || 'Low'})
      </span>
    );
  };

  return (
    <div className="space-y-6 max-w-6xl pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight flex items-center gap-3">
            <Compass className="w-8 h-8 text-primary-500" />
            Job Discovery & Eligibility
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Automated multi-platform discovery with transparent AI eligibility scoring.
          </p>
        </div>

        <div className="flex items-center gap-2.5 self-start sm:self-auto flex-wrap">
          <button
            onClick={handleBatchEvaluate}
            disabled={evaluating || jobs.length === 0}
            className="px-4 py-2.5 rounded-xl border border-primary-500/30 bg-primary-500/10 hover:bg-primary-500/20 text-primary-300 font-semibold text-sm flex items-center gap-2 cursor-pointer transition-colors disabled:opacity-50"
          >
            {evaluating ? <Loader2 className="w-4 h-4 animate-spin" /> : <ShieldCheck className="w-4 h-4" />}
            <span>{evaluating ? 'Evaluating...' : 'Evaluate Eligibility'}</span>
          </button>

          <button
            onClick={handleRunDiscovery}
            disabled={discovering}
            className="btn-primary flex items-center gap-2 px-5 py-2.5 text-sm font-semibold cursor-pointer shadow-lg shadow-primary-500/20"
          >
            {discovering ? <Loader2 className="w-4 h-4 animate-spin" /> : <RotateCw className="w-4 h-4" />}
            <span>{discovering ? 'Scanning Platforms...' : 'Run Discovery Scan'}</span>
          </button>
        </div>
      </div>

      {/* Notifications */}
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

      {/* Search & Filters */}
      <div className="glass-panel p-4 rounded-2xl space-y-3">
        <form onSubmit={handleSearchSubmit} className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by role, company, technology (e.g. Python, Razorpay, Frontend)..."
              className="input-field w-full pl-10 text-sm"
            />
          </div>
          <button type="submit" className="btn-primary text-xs px-4">
            Search
          </button>
        </form>

        <div className="flex flex-wrap items-center justify-between gap-3 pt-1 border-t border-slate-700/40">
          {/* Source filters */}
          <div className="flex items-center gap-1.5 flex-wrap">
            <span className="text-[11px] text-slate-400 uppercase font-semibold mr-1">Platform:</span>
            {[
              { id: 'all', label: 'All Platforms' },
              { id: 'linkedin', label: 'LinkedIn' },
              { id: 'internshala', label: 'Internshala' },
              { id: 'indeed', label: 'Indeed' },
              { id: 'portal', label: 'Portals' },
            ].map((src) => (
              <button
                key={src.id}
                type="button"
                onClick={() => {
                  setSourceFilter(src.id);
                  setPage(1);
                }}
                className={`px-3 py-1 text-xs rounded-lg transition-colors cursor-pointer ${
                  sourceFilter === src.id
                    ? 'bg-primary-600 text-white font-medium'
                    : 'bg-surfaceHighlight/40 text-slate-300 hover:bg-surfaceHighlight'
                }`}
              >
                {src.label}
              </button>
            ))}
          </div>

          {/* Type filters */}
          <div className="flex items-center gap-1.5">
            <span className="text-[11px] text-slate-400 uppercase font-semibold mr-1">Type:</span>
            {[
              { id: 'all', label: 'All' },
              { id: 'full-time', label: 'Full-time' },
              { id: 'internship', label: 'Internship' },
            ].map((t) => (
              <button
                key={t.id}
                type="button"
                onClick={() => {
                  setTypeFilter(t.id);
                  setPage(1);
                }}
                className={`px-2.5 py-1 text-xs rounded-lg transition-colors cursor-pointer ${
                  typeFilter === t.id
                    ? 'bg-primary-500/20 text-primary-300 border border-primary-500/40 font-medium'
                    : 'bg-surfaceHighlight/30 text-slate-400 hover:text-white'
                }`}
              >
                {t.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Opportunities Count */}
      <div className="flex items-center justify-between text-xs text-slate-400">
        <span>Found <strong className="text-white">{totalJobs}</strong> matching opportunities</span>
        {totalJobs > 0 && <span>Page {page} of {totalPages}</span>}
      </div>

      {/* Jobs Grid */}
      {loading ? (
        <div className="glass-panel p-16 rounded-2xl flex flex-col items-center justify-center text-slate-400 gap-3">
          <Loader2 className="w-8 h-8 animate-spin text-primary-500" />
          <p className="text-sm">Fetching discovered opportunities...</p>
        </div>
      ) : jobs.length === 0 ? (
        <div className="glass-panel p-16 rounded-2xl text-center text-slate-400">
          <Compass className="w-12 h-12 mx-auto mb-3 opacity-30 text-primary-400" />
          <h3 className="text-base font-semibold text-white">No jobs discovered yet</h3>
          <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto">
            Click "Run Discovery Scan" above to scan supported platforms against your career profile and job preferences.
          </p>
          <button
            onClick={handleRunDiscovery}
            className="btn-primary mt-4 text-xs py-2 px-5 inline-flex items-center gap-2"
          >
            <RotateCw className="w-4 h-4" /> Start First Discovery Scan
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {jobs.map((job) => (
            <div
              key={job.id}
              className="glass-panel p-5 rounded-2xl flex flex-col justify-between hover:border-primary-500/40 transition-all hover:scale-[1.01] group"
            >
              <div className="space-y-3">
                {/* Header tags */}
                <div className="flex items-center justify-between gap-2 flex-wrap">
                  {getSourceBadge(job.source)}
                  <div className="flex items-center gap-1.5">
                    {getScoreBadge(job.match_score, job.relevance_category)}
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium border ${
                      job.application_status === 'Eligible'
                        ? 'bg-green-500/10 text-green-400 border-green-500/30'
                        : job.application_status === 'Skipped'
                        ? 'bg-slate-800 text-slate-500 border-slate-700'
                        : 'bg-slate-800 text-slate-300 border-slate-700'
                    }`}>
                      {job.application_status || 'Discovered'}
                    </span>
                  </div>
                </div>

                {/* Job Title & Company */}
                <div>
                  <h3 className="font-bold text-white text-base group-hover:text-primary-400 transition-colors line-clamp-1">
                    {job.title}
                  </h3>
                  <div className="flex items-center gap-1.5 text-xs text-slate-300 mt-1">
                    <Building className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                    <span className="font-medium truncate">{job.company}</span>
                  </div>
                </div>

                {/* Info pills */}
                <div className="space-y-1.5 text-xs text-slate-400 pt-1">
                  <div className="flex items-center gap-1.5 truncate">
                    <MapPin className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                    <span className="truncate">{job.location}</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <Briefcase className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                    <span>{job.employment_type} • {job.experience_required}</span>
                  </div>
                  {job.salary_range && (
                    <div className="flex items-center gap-1.5 text-emerald-400 font-medium">
                      <IndianRupee className="w-3.5 h-3.5 shrink-0" />
                      <span>{job.salary_range}</span>
                    </div>
                  )}
                </div>

                {/* Description snippet */}
                <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed pt-1">
                  {job.description}
                </p>
              </div>

              {/* Card Footer Actions */}
              <div className="pt-4 mt-4 border-t border-slate-700/50 flex items-center justify-between">
                <button
                  onClick={() => openJobModal(job)}
                  className="text-xs font-semibold text-primary-400 hover:text-primary-300 flex items-center gap-1 cursor-pointer"
                >
                  Inspect & Eligibility
                </button>

                <a
                  href={job.external_job_url}
                  target="_blank"
                  rel="noreferrer"
                  className="p-1.5 text-slate-400 hover:text-white hover:bg-surfaceHighlight rounded-lg transition-colors"
                  title="Open job posting"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2 pt-4">
          <button
            onClick={() => setPage(Math.max(1, page - 1))}
            disabled={page === 1}
            className="p-2 rounded-lg bg-surfaceHighlight/50 border border-slate-700 disabled:opacity-40 hover:bg-slate-700"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <span className="text-xs text-slate-400 px-3">
            Page {page} of {totalPages}
          </span>
          <button
            onClick={() => setPage(Math.min(totalPages, page + 1))}
            disabled={page === totalPages}
            className="p-2 rounded-lg bg-surfaceHighlight/50 border border-slate-700 disabled:opacity-40 hover:bg-slate-700"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Job Details & Eligibility Breakdown Modal */}
      {selectedJob && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-panel w-full max-w-2xl max-h-[85vh] rounded-2xl flex flex-col overflow-hidden border-slate-700">
            <div className="p-6 border-b border-slate-700/60 flex items-start justify-between bg-surface/70">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  {getSourceBadge(selectedJob.source)}
                  <span className="text-xs text-slate-400">{selectedJob.employment_type}</span>
                </div>
                <h2 className="text-xl font-bold text-white tracking-tight">{selectedJob.title}</h2>
                <p className="text-sm text-primary-400 font-medium mt-0.5">{selectedJob.company} • {selectedJob.location}</p>
              </div>
              <button
                onClick={() => setSelectedJob(null)}
                className="p-1.5 text-slate-400 hover:text-white hover:bg-surfaceHighlight rounded-lg cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 overflow-y-auto space-y-6 text-sm text-slate-300">
              {/* Eligibility Breakdown Card */}
              <div className="p-5 rounded-xl bg-gradient-to-br from-surface to-surfaceHighlight/40 border border-primary-500/30 space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 font-semibold text-white">
                    <ShieldCheck className="w-5 h-5 text-primary-400" />
                    <span>AI Eligibility Evaluation</span>
                  </div>
                  {evaluationData && getScoreBadge(evaluationData.match_score, evaluationData.relevance_category)}
                </div>

                {evalLoading ? (
                  <div className="flex items-center justify-center py-6 text-slate-400 gap-2">
                    <Loader2 className="w-5 h-5 animate-spin" /> Evaluating profile alignment...
                  </div>
                ) : evaluationData ? (
                  <div className="space-y-3">
                    {/* Score Breakdown Pills */}
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-center text-xs">
                      <div className="p-2 rounded-lg bg-surfaceHighlight/50 border border-slate-700/50">
                        <span className="text-slate-400 block text-[10px] uppercase font-bold">Skills (40%)</span>
                        <strong className="text-white text-sm">{evaluationData.score_breakdown.skills}/40</strong>
                      </div>
                      <div className="p-2 rounded-lg bg-surfaceHighlight/50 border border-slate-700/50">
                        <span className="text-slate-400 block text-[10px] uppercase font-bold">Education (25%)</span>
                        <strong className="text-white text-sm">{evaluationData.score_breakdown.education}/25</strong>
                      </div>
                      <div className="p-2 rounded-lg bg-surfaceHighlight/50 border border-slate-700/50">
                        <span className="text-slate-400 block text-[10px] uppercase font-bold">Experience (20%)</span>
                        <strong className="text-white text-sm">{evaluationData.score_breakdown.experience}/20</strong>
                      </div>
                      <div className="p-2 rounded-lg bg-surfaceHighlight/50 border border-slate-700/50">
                        <span className="text-slate-400 block text-[10px] uppercase font-bold">Location (15%)</span>
                        <strong className="text-white text-sm">{evaluationData.score_breakdown.location}/15</strong>
                      </div>
                    </div>

                    {/* Matched Skills */}
                    {evaluationData.matched_skills.length > 0 && (
                      <div>
                        <span className="text-[11px] text-slate-400 uppercase font-semibold block mb-1.5">Matched Candidate Skills:</span>
                        <div className="flex flex-wrap gap-1.5">
                          {evaluationData.matched_skills.map((s) => (
                            <span key={s} className="px-2.5 py-0.5 rounded-md text-xs font-medium bg-green-500/15 text-green-300 border border-green-500/30 flex items-center gap-1">
                              <CheckCircle2 className="w-3 h-3 text-green-400" /> {s}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Missing Skills */}
                    {evaluationData.missing_skills.length > 0 && (
                      <div>
                        <span className="text-[11px] text-slate-400 uppercase font-semibold block mb-1.5">Target Skills to Expand:</span>
                        <div className="flex flex-wrap gap-1.5">
                          {evaluationData.missing_skills.map((s) => (
                            <span key={s} className="px-2.5 py-0.5 rounded-md text-xs font-medium bg-amber-500/15 text-amber-300 border border-amber-500/30">
                              {s}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Explanation */}
                    <p className="text-xs text-slate-300 leading-relaxed bg-black/20 p-3 rounded-lg border border-slate-700/40">
                      <strong>Analysis:</strong> {evaluationData.relevance_reason}
                    </p>
                  </div>
                ) : null}
              </div>

              {selectedJob.salary_range && (
                <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-xl flex items-center gap-2 text-emerald-400 font-medium">
                  <IndianRupee className="w-4 h-4 shrink-0" />
                  <span>Compensation: {selectedJob.salary_range}</span>
                </div>
              )}

              <div>
                <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Role Overview</h4>
                <p className="leading-relaxed whitespace-pre-wrap text-slate-300 bg-surfaceHighlight/20 p-4 rounded-xl border border-slate-700/40">
                  {selectedJob.description}
                </p>
              </div>

              <div>
                <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Qualifications & Skills Required</h4>
                <p className="leading-relaxed whitespace-pre-wrap text-slate-300 bg-surfaceHighlight/20 p-4 rounded-xl border border-slate-700/40">
                  {selectedJob.requirements}
                </p>
              </div>
            </div>

            <div className="p-4 border-t border-slate-700/60 flex items-center justify-between bg-surface/50">
              <span className="text-xs text-slate-400">
                Method: <strong className="text-slate-200 capitalize">{selectedJob.application_method}</strong>
              </span>

              <div className="flex items-center gap-3">
                <a
                  href={selectedJob.external_job_url}
                  target="_blank"
                  rel="noreferrer"
                  className="btn-primary text-xs py-2 px-4 flex items-center gap-1.5"
                >
                  <span>Open Job on Platform</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
