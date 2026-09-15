import apiClient from '../client';
import type { Project } from '../../types/marketplace';

export const projectService = {
  createProject: async (data: any) => {
    return apiClient.post<Project>('/projects', data);
  },

  getClientProjects: async () => {
    return apiClient.get<Project[]>('/projects/client');
  },

  getDesignerProjects: async () => {
    return apiClient.get<Project[]>('/projects/designer');
  },

  getProject: async (projectId: string) => {
    return apiClient.get<Project>(`/projects/${projectId}`);
  },

  publishProject: async (projectId: string) => {
    return apiClient.post<{ status: string }>(`/projects/${projectId}/publish`);
  },

  cancelProject: async (projectId: string) => {
    return apiClient.post<{ status: string }>(`/projects/${projectId}/cancel`);
  },

  // Used by clients to get proposals for their project
  getProposals: async (projectId: string) => {
    return apiClient.get(`/projects/${projectId}/proposals`);
  },

  // Used by clients to select a designer proposal
  selectProposal: async (projectId: string, proposalId: string) => {
    return apiClient.post(`/projects/${projectId}/proposals/${proposalId}/select`);
  },

  // Used by designers to submit a proposal
  submitProposal: async (projectId: string, data: any) => {
    return apiClient.post(`/projects/${projectId}/proposals`, data);
  },

  // Used by designers to accept a project after being selected
  acceptProject: async (projectId: string) => {
    return apiClient.post(`/projects/${projectId}/accept`);
  }
};
