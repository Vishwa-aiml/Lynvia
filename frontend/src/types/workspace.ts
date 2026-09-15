export interface Milestone {
  id: string;
  projectId: string;
  title: string;
  description: string | null;
  order: number;
  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED';
  dueDate: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface Task {
  id: string;
  milestoneId: string;
  title: string;
  description: string | null;
  status: 'TODO' | 'IN_PROGRESS' | 'IN_REVIEW' | 'DONE';
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';
  assignedUserId: string | null;
  dueDate: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface FileMetadata {
  id: string;
  projectId: string;
  filename: string;
  storageKey: string | null;
  fileUrl: string;
  mimeType: string | null;
  fileSize: number | null;
  uploaderId: string | null;
  createdAt: string;
}

export interface ProjectEvent {
  id: string;
  projectId: string;
  eventType: string;
  content: string | null;
  authorId: string | null;
  createdAt: string;
}

export interface Revision {
  id: string;
  deliveryId: string;
  revisionNumber: number;
  requestReason: string;
  clientComment: string;
  designerResponse: string | null;
  status: 'REQUESTED' | 'IN_PROGRESS' | 'RESOLVED';
  createdAt: string;
  updatedAt: string;
}

export interface Delivery {
  id: string;
  projectId: string;
  designerId: string;
  version: number;
  status: 'SUBMITTED' | 'IN_REVISION' | 'ACCEPTED' | 'REJECTED';
  message: string | null;
  submittedAt: string;
  files: FileMetadata[];
  revisions: Revision[];
}

export interface ProjectWorkspace {
  projectId: string;
  milestones: Milestone[];
  tasks: Task[];
  files: FileMetadata[];
  events: ProjectEvent[];
  deliveries: Delivery[];
}
