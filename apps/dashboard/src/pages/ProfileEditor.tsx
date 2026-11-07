import { useState, useEffect } from 'react';
import {
  User,
  GraduationCap,
  Wrench,
  Briefcase,
  Plus,
  Trash2,
  Save,
  CheckCircle2,
  AlertCircle,
  Loader2,
} from 'lucide-react';
import {
  profileApi,
  type UserProfileData,
  type EducationData,
  type SkillData,
  type ExperienceData,
} from '../services/api';
import { useAuth } from '../context/AuthContext';

export default function ProfileEditor() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<'personal' | 'education' | 'skills' | 'experience'>('personal');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Profile data
  const [profile, setProfile] = useState<UserProfileData>({
    id: 0,
    user_id: 0,
    full_name: '',
    phone: '',
    address: '',
    city: '',
    state: '',
    country: 'India',
    postal_code: '',
    linkedin_url: '',
    github_url: '',
    portfolio_url: '',
    bio: '',
    graduation_year: null,
    highest_degree: '',
  });

  const [educationList, setEducationList] = useState<EducationData[]>([]);
  const [skillsList, setSkillsList] = useState<SkillData[]>([]);
  const [experienceList, setExperienceList] = useState<ExperienceData[]>([]);

  // New item modal/form states
  const [newEdu, setNewEdu] = useState({
    institution: '',
    degree: '',
    field_of_study: '',
    start_date: '',
    end_date: '',
    gpa: '',
    is_current: false,
  });

  const [newSkill, setNewSkill] = useState({
    skill_name: '',
    category: 'Technical',
    proficiency_level: 'Intermediate',
    years_of_experience: 1,
  });

  const [newExp, setNewExp] = useState({
    company: '',
    job_title: '',
    location: '',
    start_date: '',
    end_date: '',
    is_current: false,
    description: '',
  });

  const [showAddEdu, setShowAddEdu] = useState(false);
  const [showAddSkill, setShowAddSkill] = useState(false);
  const [showAddExp, setShowAddExp] = useState(false);

  const loadProfile = async () => {
    try {
      setLoading(true);
      const data = await profileApi.get();
      setProfile(data.profile);
      setEducationList(data.education);
      setSkillsList(data.skills);
      setExperienceList(data.experience);
    } catch (err: any) {
      setErrorMessage(err.response?.data?.error || 'Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProfile();
  }, []);

  const handleSavePersonal = async () => {
    try {
      setSaving(true);
      setErrorMessage(null);
      await profileApi.update(profile);
      setSuccessMessage('Personal profile updated successfully!');
      setTimeout(() => setSuccessMessage(null), 3500);
    } catch (err: any) {
      setErrorMessage(err.response?.data?.error || 'Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  // Education Handlers
  const handleAddEducation = async () => {
    if (!newEdu.institution || !newEdu.degree) {
      setErrorMessage('Please fill in both institution and degree');
      return;
    }
    try {
      setSaving(true);
      const res = await profileApi.addEducation(newEdu);
      setEducationList([res.education, ...educationList]);
      setNewEdu({ institution: '', degree: '', field_of_study: '', start_date: '', end_date: '', gpa: '', is_current: false });
      setShowAddEdu(false);
      setSuccessMessage('Education added successfully');
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: any) {
      setErrorMessage(err.response?.data?.error || 'Failed to add education');
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteEducation = async (id: number) => {
    try {
      await profileApi.deleteEducation(id);
      setEducationList(educationList.filter((e) => e.id !== id));
    } catch (err: any) {
      setErrorMessage(err.response?.data?.error || 'Failed to delete education');
    }
  };

  // Skill Handlers
  const handleAddSkill = async () => {
    if (!newSkill.skill_name) {
      setErrorMessage('Skill name is required');
      return;
    }
    try {
      setSaving(true);
      const res = await profileApi.addSkill(newSkill);
      setSkillsList([...skillsList, res.skill]);
      setNewSkill({ skill_name: '', category: 'Technical', proficiency_level: 'Intermediate', years_of_experience: 1 });
      setShowAddSkill(false);
      setSuccessMessage('Skill added successfully');
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: any) {
      setErrorMessage(err.response?.data?.error || 'Failed to add skill');
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteSkill = async (id: number) => {
    try {
      await profileApi.deleteSkill(id);
      setSkillsList(skillsList.filter((s) => s.id !== id));
    } catch (err: any) {
      setErrorMessage(err.response?.data?.error || 'Failed to delete skill');
    }
  };

  // Experience Handlers
  const handleAddExperience = async () => {
    if (!newExp.company || !newExp.job_title) {
      setErrorMessage('Please provide both company name and job title');
      return;
    }
    try {
      setSaving(true);
      const res = await profileApi.addExperience(newExp);
      setExperienceList([res.experience, ...experienceList]);
      setNewExp({ company: '', job_title: '', location: '', start_date: '', end_date: '', is_current: false, description: '' });
      setShowAddExp(false);
      setSuccessMessage('Experience added successfully');
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: any) {
      setErrorMessage(err.response?.data?.error || 'Failed to add experience');
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteExperience = async (id: number) => {
    try {
      await profileApi.deleteExperience(id);
      setExperienceList(experienceList.filter((e) => e.id !== id));
    } catch (err: any) {
      setErrorMessage(err.response?.data?.error || 'Failed to delete experience');
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-slate-400 gap-3">
        <Loader2 className="w-8 h-8 animate-spin text-primary-500" />
        <p className="text-sm">Loading career profile...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-5xl pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Career Profile</h1>
          <p className="text-slate-400 text-sm mt-1">
            Complete your information. ApplyPilot AI maps these verified data points to application forms automatically.
          </p>
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

      {/* Navigation Tabs */}
      <div className="flex border-b border-slate-700/60 space-x-1 sm:space-x-4">
        {[
          { id: 'personal', label: 'Personal Details', icon: User, count: profile.full_name ? '✓' : '' },
          { id: 'education', label: 'Education', icon: GraduationCap, count: educationList.length },
          { id: 'skills', label: 'Skills', icon: Wrench, count: skillsList.length },
          { id: 'experience', label: 'Experience', icon: Briefcase, count: experienceList.length },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => {
              setActiveTab(tab.id as any);
              setErrorMessage(null);
            }}
            className={`flex items-center gap-2 px-4 py-3 border-b-2 font-medium text-sm transition-colors cursor-pointer ${
              activeTab === tab.id
                ? 'border-primary-500 text-primary-400 bg-primary-500/5'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <tab.icon className="w-4 h-4" />
            <span>{tab.label}</span>
            {tab.count !== '' && (
              <span className="ml-1 px-1.5 py-0.5 text-xs rounded-full bg-slate-800 text-slate-300">
                {tab.count}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Tab 1: Personal Details */}
      {activeTab === 'personal' && (
        <div className="glass-panel p-6 sm:p-8 rounded-2xl space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Full Legal Name</label>
              <input
                type="text"
                value={profile.full_name}
                onChange={(e) => setProfile({ ...profile, full_name: e.target.value })}
                className="input-field w-full text-sm"
                placeholder="e.g. Arjun Sharma"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Email Address</label>
              <input
                type="email"
                value={user?.email || ''}
                disabled
                className="input-field w-full text-sm opacity-60 cursor-not-allowed"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Phone Number</label>
              <input
                type="tel"
                value={profile.phone}
                onChange={(e) => setProfile({ ...profile, phone: e.target.value })}
                className="input-field w-full text-sm"
                placeholder="+91 9876543210"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Highest Degree</label>
              <input
                type="text"
                value={profile.highest_degree}
                onChange={(e) => setProfile({ ...profile, highest_degree: e.target.value })}
                className="input-field w-full text-sm"
                placeholder="e.g. B.Tech in Computer Science"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Graduation Year</label>
              <input
                type="number"
                value={profile.graduation_year || ''}
                onChange={(e) => setProfile({ ...profile, graduation_year: e.target.value ? parseInt(e.target.value) : null })}
                className="input-field w-full text-sm"
                placeholder="2026"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Current City</label>
              <input
                type="text"
                value={profile.city}
                onChange={(e) => setProfile({ ...profile, city: e.target.value })}
                className="input-field w-full text-sm"
                placeholder="Bengaluru"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">State / Province</label>
              <input
                type="text"
                value={profile.state}
                onChange={(e) => setProfile({ ...profile, state: e.target.value })}
                className="input-field w-full text-sm"
                placeholder="Karnataka"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Country</label>
              <input
                type="text"
                value={profile.country}
                onChange={(e) => setProfile({ ...profile, country: e.target.value })}
                className="input-field w-full text-sm"
                placeholder="India"
              />
            </div>

            <div className="space-y-1.5 sm:col-span-2">
              <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">LinkedIn Profile URL</label>
              <input
                type="url"
                value={profile.linkedin_url}
                onChange={(e) => setProfile({ ...profile, linkedin_url: e.target.value })}
                className="input-field w-full text-sm"
                placeholder="https://linkedin.com/in/username"
              />
            </div>

            <div className="space-y-1.5 sm:col-span-2">
              <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">GitHub Profile URL</label>
              <input
                type="url"
                value={profile.github_url}
                onChange={(e) => setProfile({ ...profile, github_url: e.target.value })}
                className="input-field w-full text-sm"
                placeholder="https://github.com/username"
              />
            </div>

            <div className="space-y-1.5 sm:col-span-2">
              <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Portfolio / Website URL</label>
              <input
                type="url"
                value={profile.portfolio_url}
                onChange={(e) => setProfile({ ...profile, portfolio_url: e.target.value })}
                className="input-field w-full text-sm"
                placeholder="https://yourportfolio.dev"
              />
            </div>

            <div className="space-y-1.5 sm:col-span-2">
              <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Professional Bio / Summary</label>
              <textarea
                rows={3}
                value={profile.bio}
                onChange={(e) => setProfile({ ...profile, bio: e.target.value })}
                className="input-field w-full text-sm"
                placeholder="Brief summary of your academic background, passions, and core skills..."
              />
            </div>
          </div>

          <div className="flex justify-end pt-4 border-t border-slate-700/60">
            <button
              onClick={handleSavePersonal}
              disabled={saving}
              className="btn-primary flex items-center gap-2 px-6 py-2.5 text-sm"
            >
              {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
              <span>Save Personal Information</span>
            </button>
          </div>
        </div>
      )}

      {/* Tab 2: Education */}
      {activeTab === 'education' && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <p className="text-sm text-slate-400">Add all undergraduate, postgraduate, and diploma degrees.</p>
            <button
              onClick={() => setShowAddEdu(true)}
              className="btn-primary text-xs flex items-center gap-1.5 py-1.5 px-3"
            >
              <Plus className="w-3.5 h-3.5" /> Add Degree
            </button>
          </div>

          {showAddEdu && (
            <div className="glass-panel p-6 rounded-2xl border-primary-500/30 space-y-4">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">Add Educational Qualification</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <input
                  type="text"
                  placeholder="Institution / University *"
                  value={newEdu.institution}
                  onChange={(e) => setNewEdu({ ...newEdu, institution: e.target.value })}
                  className="input-field text-sm"
                />
                <input
                  type="text"
                  placeholder="Degree (e.g. B.Tech, B.S., M.S.) *"
                  value={newEdu.degree}
                  onChange={(e) => setNewEdu({ ...newEdu, degree: e.target.value })}
                  className="input-field text-sm"
                />
                <input
                  type="text"
                  placeholder="Field of Study (e.g. Computer Science)"
                  value={newEdu.field_of_study}
                  onChange={(e) => setNewEdu({ ...newEdu, field_of_study: e.target.value })}
                  className="input-field text-sm"
                />
                <input
                  type="text"
                  placeholder="GPA / Percentage (e.g. 8.5/10, 3.8/4.0)"
                  value={newEdu.gpa}
                  onChange={(e) => setNewEdu({ ...newEdu, gpa: e.target.value })}
                  className="input-field text-sm"
                />
                <input
                  type="text"
                  placeholder="Start Year (e.g. 2022)"
                  value={newEdu.start_date}
                  onChange={(e) => setNewEdu({ ...newEdu, start_date: e.target.value })}
                  className="input-field text-sm"
                />
                <input
                  type="text"
                  placeholder="End Year / Expected (e.g. 2026)"
                  value={newEdu.end_date}
                  onChange={(e) => setNewEdu({ ...newEdu, end_date: e.target.value })}
                  className="input-field text-sm"
                />
              </div>
              <div className="flex justify-end gap-3 pt-2">
                <button
                  onClick={() => setShowAddEdu(false)}
                  className="px-4 py-2 text-sm text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button onClick={handleAddEducation} className="btn-primary text-sm px-4 py-2">
                  Add Qualification
                </button>
              </div>
            </div>
          )}

          {educationList.length === 0 && !showAddEdu ? (
            <div className="glass-panel p-12 text-center rounded-2xl text-slate-400">
              <GraduationCap className="w-12 h-12 mx-auto mb-3 opacity-30 text-primary-400" />
              <p className="font-medium text-white">No education added yet</p>
              <p className="text-xs text-slate-500 mt-1">Add your degree to help ApplyPilot match academic criteria.</p>
            </div>
          ) : (
            <div className="grid gap-3">
              {educationList.map((edu) => (
                <div key={edu.id} className="glass-panel p-5 rounded-xl flex items-start justify-between">
                  <div>
                    <h4 className="font-semibold text-white text-base">{edu.degree} {edu.field_of_study && `in ${edu.field_of_study}`}</h4>
                    <p className="text-sm text-slate-300 mt-0.5">{edu.institution}</p>
                    <div className="flex gap-4 mt-2 text-xs text-slate-400">
                      <span>{edu.start_date} – {edu.is_current ? 'Present' : edu.end_date || 'N/A'}</span>
                      {edu.gpa && <span>GPA: {edu.gpa}</span>}
                    </div>
                  </div>
                  <button
                    onClick={() => handleDeleteEducation(edu.id)}
                    className="p-2 text-slate-500 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Tab 3: Skills */}
      {activeTab === 'skills' && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <p className="text-sm text-slate-400">Add technical languages, frameworks, developer tools, and concepts.</p>
            <button
              onClick={() => setShowAddSkill(true)}
              className="btn-primary text-xs flex items-center gap-1.5 py-1.5 px-3"
            >
              <Plus className="w-3.5 h-3.5" /> Add Skill
            </button>
          </div>

          {showAddSkill && (
            <div className="glass-panel p-6 rounded-2xl border-primary-500/30 space-y-4">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">Add Technical Skill</h3>
              <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
                <input
                  type="text"
                  placeholder="Skill name (e.g. Python, React) *"
                  value={newSkill.skill_name}
                  onChange={(e) => setNewSkill({ ...newSkill, skill_name: e.target.value })}
                  className="input-field text-sm"
                />
                <select
                  value={newSkill.category}
                  onChange={(e) => setNewSkill({ ...newSkill, category: e.target.value })}
                  className="input-field text-sm"
                >
                  <option value="Languages">Languages</option>
                  <option value="Frameworks">Frameworks & Libraries</option>
                  <option value="Databases">Databases</option>
                  <option value="Tools & Cloud">Tools & Cloud</option>
                  <option value="Soft Skills">Soft Skills</option>
                </select>
                <select
                  value={newSkill.proficiency_level}
                  onChange={(e) => setNewSkill({ ...newSkill, proficiency_level: e.target.value })}
                  className="input-field text-sm"
                >
                  <option value="Beginner">Beginner</option>
                  <option value="Intermediate">Intermediate</option>
                  <option value="Advanced">Advanced</option>
                  <option value="Expert">Expert</option>
                </select>
                <input
                  type="number"
                  step="0.5"
                  placeholder="Years Exp (e.g. 1.5)"
                  value={newSkill.years_of_experience}
                  onChange={(e) => setNewSkill({ ...newSkill, years_of_experience: parseFloat(e.target.value) || 0 })}
                  className="input-field text-sm"
                />
              </div>
              <div className="flex justify-end gap-3 pt-2">
                <button
                  onClick={() => setShowAddSkill(false)}
                  className="px-4 py-2 text-sm text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button onClick={handleAddSkill} className="btn-primary text-sm px-4 py-2">
                  Save Skill
                </button>
              </div>
            </div>
          )}

          {skillsList.length === 0 && !showAddSkill ? (
            <div className="glass-panel p-12 text-center rounded-2xl text-slate-400">
              <Wrench className="w-12 h-12 mx-auto mb-3 opacity-30 text-primary-400" />
              <p className="font-medium text-white">No skills added yet</p>
              <p className="text-xs text-slate-500 mt-1">Add your skills so the eligibility engine can evaluate job requirements.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
              {skillsList.map((skill) => (
                <div key={skill.id} className="glass-panel p-4 rounded-xl flex items-center justify-between">
                  <div>
                    <h4 className="font-medium text-white text-sm">{skill.skill_name}</h4>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-xs text-primary-400 bg-primary-500/10 px-2 py-0.5 rounded-md border border-primary-500/20">
                        {skill.proficiency_level}
                      </span>
                      <span className="text-xs text-slate-400">{skill.category}</span>
                    </div>
                  </div>
                  <button
                    onClick={() => handleDeleteSkill(skill.id)}
                    className="p-1.5 text-slate-500 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Tab 4: Experience */}
      {activeTab === 'experience' && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <p className="text-sm text-slate-400">Add internships, part-time jobs, freelance, or full-time roles.</p>
            <button
              onClick={() => setShowAddExp(true)}
              className="btn-primary text-xs flex items-center gap-1.5 py-1.5 px-3"
            >
              <Plus className="w-3.5 h-3.5" /> Add Experience
            </button>
          </div>

          {showAddExp && (
            <div className="glass-panel p-6 rounded-2xl border-primary-500/30 space-y-4">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">Add Experience</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <input
                  type="text"
                  placeholder="Company Name *"
                  value={newExp.company}
                  onChange={(e) => setNewExp({ ...newExp, company: e.target.value })}
                  className="input-field text-sm"
                />
                <input
                  type="text"
                  placeholder="Job Title / Role *"
                  value={newExp.job_title}
                  onChange={(e) => setNewExp({ ...newExp, job_title: e.target.value })}
                  className="input-field text-sm"
                />
                <input
                  type="text"
                  placeholder="Location (e.g. Remote, Bengaluru)"
                  value={newExp.location}
                  onChange={(e) => setNewExp({ ...newExp, location: e.target.value })}
                  className="input-field text-sm"
                />
                <div className="grid grid-cols-2 gap-2">
                  <input
                    type="text"
                    placeholder="Start Date (e.g. May 2025)"
                    value={newExp.start_date}
                    onChange={(e) => setNewExp({ ...newExp, start_date: e.target.value })}
                    className="input-field text-sm"
                  />
                  <input
                    type="text"
                    placeholder="End Date (e.g. Aug 2025)"
                    value={newExp.end_date}
                    onChange={(e) => setNewExp({ ...newExp, end_date: e.target.value })}
                    className="input-field text-sm"
                  />
                </div>
                <div className="sm:col-span-2">
                  <textarea
                    rows={3}
                    placeholder="Key responsibilities and achievements..."
                    value={newExp.description}
                    onChange={(e) => setNewExp({ ...newExp, description: e.target.value })}
                    className="input-field w-full text-sm"
                  />
                </div>
              </div>
              <div className="flex justify-end gap-3 pt-2">
                <button
                  onClick={() => setShowAddExp(false)}
                  className="px-4 py-2 text-sm text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button onClick={handleAddExperience} className="btn-primary text-sm px-4 py-2">
                  Save Experience
                </button>
              </div>
            </div>
          )}

          {experienceList.length === 0 && !showAddExp ? (
            <div className="glass-panel p-12 text-center rounded-2xl text-slate-400">
              <Briefcase className="w-12 h-12 mx-auto mb-3 opacity-30 text-primary-400" />
              <p className="font-medium text-white">No work experience listed</p>
              <p className="text-xs text-slate-500 mt-1">If you are a fresh graduate with no prior experience, you can leave this blank.</p>
            </div>
          ) : (
            <div className="grid gap-3">
              {experienceList.map((exp) => (
                <div key={exp.id} className="glass-panel p-5 rounded-xl flex items-start justify-between">
                  <div>
                    <h4 className="font-semibold text-white text-base">{exp.job_title}</h4>
                    <p className="text-sm text-primary-400 mt-0.5">{exp.company} {exp.location && `• ${exp.location}`}</p>
                    <p className="text-xs text-slate-400 mt-1">{exp.start_date} – {exp.is_current ? 'Present' : exp.end_date || 'N/A'}</p>
                    {exp.description && (
                      <p className="text-xs text-slate-300 mt-2 leading-relaxed">{exp.description}</p>
                    )}
                  </div>
                  <button
                    onClick={() => handleDeleteExperience(exp.id)}
                    className="p-2 text-slate-500 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
