export interface DesignerProfile {
  user_id: string;
  bio: string | null;
  specialties: string[];
  portfolio_links: string[];
  hourly_rate: number | null;
  created_at: string;
  updated_at: string;
}

export interface Project {
  id: string;
  clientId: string;
  designerId: string | null;
  selectedProposalId: string | null;
  title: string;
  category: string;
  description: string | null;
  requirements: string | null;
  deliverables: string[] | null;
  referenceFiles: string[] | null;
  budget: number | null;
  deadline: string | null;
  status: string; // DRAFT, OPEN_FOR_PROPOSALS, etc.
  currentPhase: string | null;
  createdAt: string;
  updatedAt: string;
}
