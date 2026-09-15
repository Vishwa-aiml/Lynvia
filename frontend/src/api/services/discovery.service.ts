import apiClient from '../client';
import type { Project, DesignerProfile } from '../../types/marketplace';

export const discoveryService = {
  getProjects: async (category?: string) => {
    const params = category ? { category } : {};
    return apiClient.get<Project[]>('/discovery/projects', { params });
  },

  getDesigners: async (category?: string) => {
    const params = category ? { category } : {};
    return apiClient.get<DesignerProfile[]>('/discovery/designers', { params });
  },

  getDesignerProfile: async (designerId: string) => {
    return apiClient.get<DesignerProfile>(`/discovery/designers/${designerId}`);
  }
};
