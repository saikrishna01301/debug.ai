import axios, { AxiosInstance, AxiosError } from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Analysis API Types
export interface Solution {
  title: string;
  explanation: string;
  code: string;
  confidence: number;
  source_urls?: string[];
}

export interface AnalysisResult {
  error_type: string;
  error_message: string;
  language: string;
  file_path: string;
  line_number: number;
  root_cause: string;
  reasoning: string;
  solutions: Solution[];
  sources_used: number;
  analysis_id: number;
}

// Feedback API Types
export interface FeedbackRequest {
  analysis_id: number;
  solution_index: number;
  worked: boolean;
  notes?: string;
}

export interface FeedbackResponse {
  id: number;
  analysis_id: number;
  solution_index: number;
  worked: boolean;
  notes?: string;
  created_at: string;
}

// Analytics API Types
export interface AnalyticsOverview {
  total_analyses: number;
  total_errors_parsed: number;
  avg_analysis_time_ms: number;
  errors_by_language: { language: string; count: number }[];
  feedback: {
    total: number;
    successful: number;
    success_rate: number;
  };
}

export interface LanguageBreakdown {
  language: string;
  total_errors: number;
  avg_confidence: number;
}

export interface FeedbackStats {
  total_feedback: number;
  total_successful: number;
  overall_success_rate: number;
  solution_breakdown: {
    solution_index: number;
    total_feedback: number;
    successful: number;
    success_rate: number;
  }[];
}

// Error response type
export interface ApiError {
  message: string;
  status?: number;
  data?: any;
}

class ApiService {
  private client: AxiosInstance;

  constructor(baseUrl: string = API_BASE_URL) {
    this.client = axios.create({
      baseURL: baseUrl,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000, // 30 seconds timeout
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        const apiError: ApiError = {
          message: error.message,
          status: error.response?.status,
          data: error.response?.data,
        };

        if (error.response) {
          // Server responded with error status
          apiError.message = `Request failed: ${error.response.status} ${error.response.statusText}`;
        } else if (error.request) {
          // Request made but no response received
          apiError.message = 'No response from server. Please check if the backend is running.';
        }

        return Promise.reject(apiError);
      }
    );
  }

  /**
   * Analyze error log and get solutions
   */
  async analyze(query: string, limit: number = 5): Promise<AnalysisResult> {
    try {
      const response = await this.client.post<AnalysisResult>('/api/analyze', {
        query,
        limit,
      });
      return response.data;
    } catch (error) {
      console.error('Analyze API error:', error);
      throw error;
    }
  }

  /**
   * Health check
   */
  async health(): Promise<{ message: string }> {
    try {
      const response = await this.client.get<{ message: string }>('/');
      return response.data;
    } catch (error) {
      console.error('Health check error:', error);
      throw error;
    }
  }

  /**
   * Submit feedback for a solution
   */
  async submitFeedback(feedback: FeedbackRequest): Promise<FeedbackResponse> {
    try {
      const response = await this.client.post<FeedbackResponse>('/api/feedback', feedback);
      return response.data;
    } catch (error) {
      console.error('Feedback API error:', error);
      throw error;
    }
  }

  /**
   * Get analytics overview
   */
  async getAnalyticsOverview(): Promise<AnalyticsOverview> {
    try {
      const response = await this.client.get<AnalyticsOverview>('/api/analytics/overview');
      return response.data;
    } catch (error) {
      console.error('Analytics overview error:', error);
      throw error;
    }
  }

  /**
   * Get language breakdown
   */
  async getLanguageBreakdown(): Promise<LanguageBreakdown[]> {
    try {
      const response = await this.client.get<LanguageBreakdown[]>('/api/analytics/language-breakdown');
      return response.data;
    } catch (error) {
      console.error('Language breakdown error:', error);
      throw error;
    }
  }

  /**
   * Get feedback stats
   */
  async getFeedbackStats(): Promise<FeedbackStats> {
    try {
      const response = await this.client.get<FeedbackStats>('/api/analytics/feedback-stats');
      return response.data;
    } catch (error) {
      console.error('Feedback stats error:', error);
      throw error;
    }
  }
}

export const apiService = new ApiService();
