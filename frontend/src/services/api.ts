import axios from 'axios';
import {
  PaperDetail,
  PaperSummary,
  ReferenceDetail,
  CitationOccurrence,
  PaperIssue,
  PaperStatistics,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // Upload a PDF paper
  uploadPaper: async (file: File): Promise<PaperDetail> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await client.post<PaperDetail>('/papers/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Start analysis pipeline
  analyzePaper: async (paperId: string): Promise<any> => {
    const response = await client.post(`/papers/${paperId}/analyze`);
    return response.data;
  },

  // List all uploaded papers
  listPapers: async (): Promise<PaperSummary[]> => {
    const response = await client.get<PaperSummary[]>('/papers');
    return response.data;
  },

  // Get paper detail
  getPaper: async (paperId: string): Promise<PaperDetail> => {
    const response = await client.get<PaperDetail>(`/papers/${paperId}`);
    return response.data;
  },

  // Get paper references with filtering & sorting
  getPaperReferences: async (
    paperId: string,
    params?: { status?: string; search?: string; sort_by?: string }
  ): Promise<ReferenceDetail[]> => {
    const response = await client.get<ReferenceDetail[]>(`/papers/${paperId}/references`, {
      params,
    });
    return response.data;
  },

  // Get single reference detail
  getReferenceDetail: async (paperId: string, referenceId: string): Promise<ReferenceDetail> => {
    const response = await client.get<ReferenceDetail>(`/papers/${paperId}/references/${referenceId}`);
    return response.data;
  },

  // Re-verify a single reference
  reverifyReference: async (referenceId: string): Promise<ReferenceDetail> => {
    const response = await client.post<ReferenceDetail>(`/references/${referenceId}/verify`);
    return response.data;
  },

  // Get in-text citations & claim validations
  getPaperCitations: async (paperId: string): Promise<CitationOccurrence[]> => {
    const response = await client.get<CitationOccurrence[]>(`/papers/${paperId}/citations`);
    return response.data;
  },

  // Get detected integrity & metadata issues
  getPaperIssues: async (paperId: string, severity?: string): Promise<PaperIssue[]> => {
    const response = await client.get<PaperIssue[]>(`/papers/${paperId}/issues`, {
      params: { severity },
    });
    return response.data;
  },

  // Get aggregated paper statistics
  getPaperStatistics: async (paperId: string): Promise<PaperStatistics> => {
    const response = await client.get<PaperStatistics>(`/papers/${paperId}/statistics`);
    return response.data;
  },

  // Download PDF Report
  getReportDownloadUrl: (paperId: string): string => {
    return `${API_BASE_URL}/papers/${paperId}/report`;
  },

  // Load rich demo dataset
  loadDemoPaper: async (): Promise<PaperDetail> => {
    const response = await client.post<PaperDetail>('/demo/load');
    return response.data;
  },

  // Delete paper
  deletePaper: async (paperId: string): Promise<void> => {
    await client.delete(`/papers/${paperId}`);
  },
};
