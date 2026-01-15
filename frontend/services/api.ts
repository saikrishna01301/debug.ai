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
}

export const apiService = new ApiService();
