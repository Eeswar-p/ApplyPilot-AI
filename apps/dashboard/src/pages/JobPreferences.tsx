import { useState, useEffect } from 'react';
import {
  Sliders,
  Briefcase,
  MapPin,
  Building,
  GraduationCap,
  IndianRupee,
  Save,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Sparkles,
  ShieldAlert,
} from 'lucide-react';
import { preferencesApi, type JobPreferenceData } from '../services/api';

const POPULAR_ROLES = [
  'Software Engineer',
  'Frontend Developer',
  'Full Stack Developer',
  'Backend Developer',
  'Python Developer',
  'React Developer',
  'Data Analyst',
  'AI / ML Engineer',
];

const POPULAR_CITIES = [
  'Remote',
  'Bengaluru',
  'Hyderabad',
  'Pune',
  'Mumbai',
  'Delhi NCR',
  'Chennai',
];

export default function JobPreferences() {
  const [preferences, setPreferences] = useState<JobPreferenceData>({
    id: 0,
    user_id: 0,
    desired_titles: '',
    desired_locations: '',
    remote_preference: 'any',
    min_salary: 0,
    employment_types: 'full-time, internship',
    experience_level: 'entry',
    fresh_graduate_friendly: true,
    skills_filter: '',
    companies_whitelist: '',
    companies_blacklist: '',
  });

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const loadPreferences = async () => {
    try {
      setLoading(true);
      const data = await preferencesApi.get();
      setPreferences(data.preferences);
    } catch (err: any) {
      setErrorMessage(err.response?.data?.error || 'Failed to load preferences');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPreferences();
  }, []);

  const handleSave = async () => {
    try {
      setSaving(true);
      setErrorMessage(null);
      const res = await preferencesApi.update(preferences);
      setPreferences(res.preferences);
      setSuccessMessage('Job search preferences updated successfully!');
      setTimeout(() => setSuccessMessage(null), 3500);
    } catch (err: any) {
      setErrorMessage(err.response?.data?.error || 'Failed to update preferences');
    } finally {
      setSaving(false);
    }
  };

  const addRolePill = (role: string) => {
    const current = preferences.desired_titles
      ? preferences.desired_titles.split(',').map((r) => r.trim())
      : [];
    if (!current.includes(role)) {
      setPreferences({
        ...preferences,
        desired_titles: current.length > 0 ? `${preferences.desired_titles}, ${role}` : role,
      });
    }
  };

  const addCityPill = (city: string) => {
    const current = preferences.desired_locations
      ? preferences.desired_locations.split(',').map((c) => c.trim())
      : [];
    if (!current.includes(city)) {
      setPreferences({
        ...preferences,
        desired_locations: current.length > 0 ? `${preferences.desired_locations}, ${city}` : city,
      });
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-slate-400 gap-3">
        <Loader2 className="w-8 h-8 animate-spin text-primary-500" />
        <p className="text-sm">Loading job preferences...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-5xl pb-12">
      {/* Title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight flex items-center gap-3">
            <Sliders className="w-7 h-7 text-primary-500" />
            Job Preferences & Filters
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Configure target titles, locations, fresh-graduate parameters, and company filters for the discovery and auto-application engines.
          </p>
        </div>

        <button
          onClick={handleSave}
          disabled={saving}
          className="btn-primary self-start sm:self-auto flex items-center gap-2 px-6 py-2.5 text-sm font-semibold cursor-pointer"
        >
          {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
          <span>Save Preferences</span>
        </button>
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

      {/* Fresh Graduate Advantage Spotlight Banner */}
      <div className="glass-panel p-6 rounded-2xl border-primary-500/40 bg-gradient-to-r from-primary-900/30 to-blue-900/20 shadow-xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-start gap-4">
          <div className="p-3 bg-primary-500/20 text-primary-400 rounded-xl shrink-0 mt-0.5">
            <GraduationCap className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="font-semibold text-white text-base">Fresh Graduate Friendly Mode</h3>
              <span className="px-2 py-0.5 text-[10px] uppercase font-bold tracking-wider rounded bg-primary-500/30 text-primary-300">
                Recommended
              </span>
            </div>
            <p className="text-xs text-slate-300 mt-1 max-w-2xl leading-relaxed">
              Prioritizes roles tailored for recent UG/PG college graduates (0–2 years experience), automatic filtering of unrealistic senior requirements, and high-match entry roles.
            </p>
          </div>
        </div>

        <label className="relative inline-flex items-center cursor-pointer shrink-0">
          <input
            type="checkbox"
            checked={preferences.fresh_graduate_friendly}
            onChange={(e) => setPreferences({ ...preferences, fresh_graduate_friendly: e.target.checked })}
            className="sr-only peer"
          />
          <div className="w-12 h-6 bg-slate-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
        </label>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Card 1: Desired Job Titles */}
        <div className="glass-panel p-6 rounded-2xl space-y-4">
          <div className="flex items-center gap-2 text-white font-semibold">
            <Briefcase className="w-4 h-4 text-primary-400" />
            <h3>Target Job Titles</h3>
          </div>
          <p className="text-xs text-slate-400">Comma-separated titles you wish to discover and apply for.</p>
          <input
            type="text"
            value={preferences.desired_titles}
            onChange={(e) => setPreferences({ ...preferences, desired_titles: e.target.value })}
            className="input-field w-full text-sm font-medium"
            placeholder="e.g. Software Engineer, React Developer"
          />
          <div>
            <span className="text-[11px] text-slate-400 uppercase tracking-wider block mb-2 font-semibold">Quick Add:</span>
            <div className="flex flex-wrap gap-1.5">
              {POPULAR_ROLES.map((role) => (
                <button
                  key={role}
                  type="button"
                  onClick={() => addRolePill(role)}
                  className="px-2.5 py-1 text-xs rounded-lg bg-surfaceHighlight/50 hover:bg-primary-500/20 text-slate-300 hover:text-primary-300 border border-slate-700/50 transition-colors cursor-pointer"
                >
                  + {role}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Card 2: Preferred Locations */}
        <div className="glass-panel p-6 rounded-2xl space-y-4">
          <div className="flex items-center gap-2 text-white font-semibold">
            <MapPin className="w-4 h-4 text-primary-400" />
            <h3>Preferred Locations</h3>
          </div>
          <p className="text-xs text-slate-400">Cities or regions to target for opportunities.</p>
          <input
            type="text"
            value={preferences.desired_locations}
            onChange={(e) => setPreferences({ ...preferences, desired_locations: e.target.value })}
            className="input-field w-full text-sm font-medium"
            placeholder="e.g. Remote, Bengaluru, Pune"
          />
          <div>
            <span className="text-[11px] text-slate-400 uppercase tracking-wider block mb-2 font-semibold">Quick Add:</span>
            <div className="flex flex-wrap gap-1.5">
              {POPULAR_CITIES.map((city) => (
                <button
                  key={city}
                  type="button"
                  onClick={() => addCityPill(city)}
                  className="px-2.5 py-1 text-xs rounded-lg bg-surfaceHighlight/50 hover:bg-primary-500/20 text-slate-300 hover:text-primary-300 border border-slate-700/50 transition-colors cursor-pointer"
                >
                  + {city}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Card 3: Workplace Mode */}
        <div className="glass-panel p-6 rounded-2xl space-y-4">
          <h3 className="text-white font-semibold flex items-center gap-2">
            <Building className="w-4 h-4 text-primary-400" /> Workplace Mode
          </h3>
          <p className="text-xs text-slate-400">Select your preferred working arrangement.</p>
          <div className="grid grid-cols-2 gap-2.5">
            {[
              { id: 'remote', label: 'Remote Only', desc: 'Work 100% from home' },
              { id: 'hybrid', label: 'Hybrid', desc: 'Mix of office and remote' },
              { id: 'onsite', label: 'Onsite / Office', desc: 'In-office presence' },
              { id: 'any', label: 'Any Workplace Mode', desc: 'No mode restrictions' },
            ].map((mode) => (
              <button
                key={mode.id}
                type="button"
                onClick={() => setPreferences({ ...preferences, remote_preference: mode.id as any })}
                className={`p-3 rounded-xl border text-left transition-all cursor-pointer ${
                  preferences.remote_preference === mode.id
                    ? 'border-primary-500 bg-primary-500/10 text-white'
                    : 'border-slate-700/50 hover:bg-surfaceHighlight/30 text-slate-300'
                }`}
              >
                <p className="text-sm font-semibold">{mode.label}</p>
                <p className="text-[11px] text-slate-400 mt-0.5">{mode.desc}</p>
              </button>
            ))}
          </div>
        </div>

        {/* Card 4: Experience Level & Employment Type */}
        <div className="glass-panel p-6 rounded-2xl space-y-4">
          <h3 className="text-white font-semibold flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-primary-400" /> Experience & Type
          </h3>
          <div className="space-y-3">
            <div>
              <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider block mb-1.5">
                Target Experience Bracket
              </label>
              <select
                value={preferences.experience_level}
                onChange={(e) => setPreferences({ ...preferences, experience_level: e.target.value as any })}
                className="input-field w-full text-sm"
              >
                <option value="entry">Entry Level (0 - 2 Years)</option>
                <option value="mid">Mid Level (2 - 5 Years)</option>
                <option value="any">Any Experience Level</option>
              </select>
            </div>

            <div>
              <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider block mb-1.5">
                Opportunity Types
              </label>
              <input
                type="text"
                value={preferences.employment_types}
                onChange={(e) => setPreferences({ ...preferences, employment_types: e.target.value })}
                className="input-field w-full text-sm"
                placeholder="full-time, internship"
              />
              <span className="text-[11px] text-slate-500 mt-1 block">Separate with commas (e.g. full-time, internship)</span>
            </div>
          </div>
        </div>

        {/* Card 5: Minimum Expected Annual Compensation */}
        <div className="glass-panel p-6 rounded-2xl space-y-4">
          <h3 className="text-white font-semibold flex items-center gap-2">
            <IndianRupee className="w-4 h-4 text-primary-400" /> Minimum Salary / Package (INR)
          </h3>
          <p className="text-xs text-slate-400">Filter out opportunities below your baseline threshold.</p>
          <div className="relative">
            <input
              type="number"
              step="50000"
              value={preferences.min_salary || ''}
              onChange={(e) => setPreferences({ ...preferences, min_salary: parseInt(e.target.value) || 0 })}
              className="input-field w-full text-sm pl-8 font-mono"
              placeholder="0 (No minimum)"
            />
            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 font-bold text-sm">₹</span>
          </div>

          <div className="flex gap-2">
            {[300000, 500000, 800000, 1200000].map((val) => (
              <button
                key={val}
                type="button"
                onClick={() => setPreferences({ ...preferences, min_salary: val })}
                className="px-2.5 py-1 text-xs rounded-lg bg-surfaceHighlight/50 hover:bg-slate-700 text-slate-300 border border-slate-700/60 transition-colors"
              >
                ₹{(val / 100000).toFixed(0)} LPA
              </button>
            ))}
          </div>
        </div>

        {/* Card 6: Required Skill Keywords */}
        <div className="glass-panel p-6 rounded-2xl space-y-4">
          <h3 className="text-white font-semibold flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-primary-400" /> Essential Skills Filter
          </h3>
          <p className="text-xs text-slate-400">Prioritize jobs containing these required technologies.</p>
          <input
            type="text"
            value={preferences.skills_filter}
            onChange={(e) => setPreferences({ ...preferences, skills_filter: e.target.value })}
            className="input-field w-full text-sm"
            placeholder="e.g. Python, React, SQL, TypeScript, Git"
          />
        </div>

        {/* Card 7: Target Companies (Whitelist) */}
        <div className="glass-panel p-6 rounded-2xl space-y-4">
          <h3 className="text-white font-semibold flex items-center gap-2 text-green-400">
            <Building className="w-4 h-4 text-green-400" /> Target Companies (Whitelist)
          </h3>
          <p className="text-xs text-slate-400">Companies you are particularly eager to apply to.</p>
          <input
            type="text"
            value={preferences.companies_whitelist}
            onChange={(e) => setPreferences({ ...preferences, companies_whitelist: e.target.value })}
            className="input-field w-full text-sm"
            placeholder="e.g. Google, Microsoft, Atlassian, Razorpay"
          />
        </div>

        {/* Card 8: Excluded Companies (Blacklist) */}
        <div className="glass-panel p-6 rounded-2xl space-y-4">
          <h3 className="text-white font-semibold flex items-center gap-2 text-red-400">
            <ShieldAlert className="w-4 h-4 text-red-400" /> Excluded Companies (Blacklist)
          </h3>
          <p className="text-xs text-slate-400">ApplyPilot will skip these companies automatically.</p>
          <input
            type="text"
            value={preferences.companies_blacklist}
            onChange={(e) => setPreferences({ ...preferences, companies_blacklist: e.target.value })}
            className="input-field w-full text-sm"
            placeholder="e.g. Revature, Staffing Agencies"
          />
        </div>
      </div>
    </div>
  );
}
