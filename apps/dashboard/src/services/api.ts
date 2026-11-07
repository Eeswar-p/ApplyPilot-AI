import axios, { AxiosError } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: attach JWT Bearer token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('applypilot_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: handle 401 Unauthorized
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('applypilot_token');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// Type definitions
export interface User {
  id: number;
  email: string;
  is_active: boolean;
  created_at?: string;
}

export interface UserProfileData {
  id: number;
  user_id: number;
  full_name: string;
  phone: string;
  address: string;
  city: string;
  state: string;
  country: string;
  postal_code: string;
  linkedin_url: string;
  github_url: string;
  portfolio_url: string;
  bio: string;
  graduation_year: number | null;
  highest_degree: string;
}

export interface EducationData {
  id: number;
  user_id: number;
  institution: string;
  degree: string;
  field_of_study: string;
  start_date: string;
  end_date: string;
  gpa: string;
  is_current: boolean;
}

export interface SkillData {
  id: number;
  user_id: number;
  skill_name: string;
  category: string;
  proficiency_level: string;
  years_of_experience: number;
}

export interface ExperienceData {
  id: number;
  user_id: number;
  company: string;
  job_title: string;
  location: string;
  start_date: string;
  end_date: string;
  is_current: boolean;
  description: string;
}

export interface CompleteProfileResponse {
  profile: UserProfileData;
  education: EducationData[];
  skills: SkillData[];
  experience: ExperienceData[];
}

export interface ResumeData {
  id: number;
  user_id: number;
  filename: string;
  file_size: number;
  file_type: string;
  is_primary: boolean;
  parsed_text?: string;
  created_at: string;
}

export interface JobPreferenceData {
  id: number;
  user_id: number;
  desired_titles: string;
  desired_locations: string;
  remote_preference: 'remote' | 'hybrid' | 'onsite' | 'any';
  min_salary: number;
  employment_types: string;
  experience_level: 'entry' | 'mid' | 'senior' | 'any';
  fresh_graduate_friendly: boolean;
  skills_filter: string;
  companies_whitelist: string;
  companies_blacklist: string;
}

export interface JobItemData {
  id: number;
  title: string;
  company: string;
  location: string;
  employment_type: string;
  experience_required: string;
  description: string;
  requirements: string;
  salary_range: string;
  source: string;
  external_job_url: string;
  application_method: string;
  discovered_at: string;
  application_id?: number | null;
  application_status?: string;
  match_score?: number;
  relevance_category?: string;
}

export interface EligibilityEvaluationData {
  job_id: number;
  job_title: string;
  company: string;
  match_score: number;
  relevance_category: string;
  status: string;
  matched_skills: string[];
  missing_skills: string[];
  relevance_reason: string;
  score_breakdown: {
    skills: number;
    education: number;
    experience: number;
    location: number;
  };
}

// Authentication API
export const authApi = {
  register: async (payload: { email: string; password: string; full_name?: string }) => {
    const res = await apiClient.post('/auth/register', payload);
    return res.data;
  },
  login: async (payload: { email: string; password: string }) => {
    const res = await apiClient.post('/auth/login', payload);
    return res.data;
  },
  logout: async () => {
    const res = await apiClient.post('/auth/logout');
    return res.data;
  },
  me: async () => {
    const res = await apiClient.get('/auth/me');
    return res.data;
  },
};

// Profile API
export const profileApi = {
  get: async (): Promise<CompleteProfileResponse> => {
    const res = await apiClient.get('/profile');
    return res.data;
  },
  update: async (data: Partial<UserProfileData>) => {
    const res = await apiClient.put('/profile', data);
    return res.data;
  },
  addEducation: async (data: Omit<EducationData, 'id' | 'user_id'>) => {
    const res = await apiClient.post('/profile/education', data);
    return res.data;
  },
  updateEducation: async (id: number, data: Partial<EducationData>) => {
    const res = await apiClient.put(`/profile/education/${id}`, data);
    return res.data;
  },
  deleteEducation: async (id: number) => {
    const res = await apiClient.delete(`/profile/education/${id}`);
    return res.data;
  },
  addSkill: async (data: Omit<SkillData, 'id' | 'user_id'>) => {
    const res = await apiClient.post('/profile/skills', data);
    return res.data;
  },
  updateSkill: async (id: number, data: Partial<SkillData>) => {
    const res = await apiClient.put(`/profile/skills/${id}`, data);
    return res.data;
  },
  deleteSkill: async (id: number) => {
    const res = await apiClient.delete(`/profile/skills/${id}`);
    return res.data;
  },
  addExperience: async (data: Omit<ExperienceData, 'id' | 'user_id'>) => {
    const res = await apiClient.post('/profile/experience', data);
    return res.data;
  },
  updateExperience: async (id: number, data: Partial<ExperienceData>) => {
    const res = await apiClient.put(`/profile/experience/${id}`, data);
    return res.data;
  },
  deleteExperience: async (id: number) => {
    const res = await apiClient.delete(`/profile/experience/${id}`);
    return res.data;
  },
};

// Resumes API
export const resumesApi = {
  list: async (): Promise<{ resumes: ResumeData[]; count: number }> => {
    const res = await apiClient.get('/resumes');
    return res.data;
  },
  getById: async (id: number): Promise<{ resume: ResumeData }> => {
    const res = await apiClient.get(`/resumes/${id}`);
    return res.data;
  },
  upload: async (file: File): Promise<{ message: string; resume: ResumeData; meta: any }> => {
    const formData = new FormData();
    formData.append('resume', file);
    const res = await apiClient.post('/resumes/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return res.data;
  },
  setPrimary: async (id: number) => {
    const res = await apiClient.put(`/resumes/${id}/primary`);
    return res.data;
  },
  delete: async (id: number) => {
    const res = await apiClient.delete(`/resumes/${id}`);
    return res.data;
  },
};

// Job Preferences API
export const preferencesApi = {
  get: async (): Promise<{ preferences: JobPreferenceData }> => {
    const res = await apiClient.get('/preferences');
    return res.data;
  },
  update: async (data: Partial<JobPreferenceData>): Promise<{ message: string; preferences: JobPreferenceData }> => {
    const res = await apiClient.put('/preferences', data);
    return res.data;
  },
};

// Jobs API
export const jobsApi = {
  list: async (params?: {
    search?: string;
    source?: string;
    employment_type?: string;
    page?: number;
    per_page?: number;
  }): Promise<{ jobs: JobItemData[]; total: number; page: number; per_page: number; pages: number }> => {
    const res = await apiClient.get('/jobs', { params });
    return res.data;
  },
  getById: async (id: number): Promise<{ job: JobItemData & { application?: any } }> => {
    const res = await apiClient.get(`/jobs/${id}`);
    return res.data;
  },
  discover: async (): Promise<{ message: string; stats: any }> => {
    const res = await apiClient.post('/jobs/discover');
    return res.data;
  },
};

// Eligibility Evaluation API
export const eligibilityApi = {
  evaluate: async (jobId?: number): Promise<{ message: string; summary?: any; evaluation?: EligibilityEvaluationData }> => {
    const res = await apiClient.post('/eligibility/evaluate', jobId ? { job_id: jobId } : {});
    return res.data;
  },
  getBreakdown: async (jobId: number): Promise<{ evaluation: EligibilityEvaluationData }> => {
    const res = await apiClient.get(`/eligibility/${jobId}`);
    return res.data;
  },
};

export const healthApi = {
  check: async () => {
    const res = await apiClient.get('/health');
    return res.data;
  },
};

export default apiClient;
