import apiClient from '../client';
import type { ProjectWorkspace, Delivery, Revision, FileMetadata } from '../../types/workspace';

export const workspaceService = {
  getWorkspace: (projectId: string) =>
    apiClient.get<ProjectWorkspace>('/workspace/', { params: { project_id: projectId } }),

  submitDelivery: (projectId: string, data: { message?: string, fileIds: string[] }) =>
    apiClient.post<Delivery>(`/workspace/deliveries`, data, { params: { project_id: projectId } }),

  acceptDelivery: (projectId: string, deliveryId: string) =>
    apiClient.post<Delivery>(`/workspace/deliveries/${deliveryId}/accept`, null, { params: { project_id: projectId } }),

  requestRevision: (projectId: string, deliveryId: string, data: { requestReason: string, clientComment: string }) =>
    apiClient.post<Revision>(`/workspace/deliveries/${deliveryId}/revise`, data, { params: { project_id: projectId } }),

  addFile: (projectId: string, data: { filename: string, storageKey: string | null, fileUrl: string, mimeType: string | null, fileSize: number | null }) =>
    apiClient.post<FileMetadata>(`/workspace/files`, data, { params: { project_id: projectId } }),
};
