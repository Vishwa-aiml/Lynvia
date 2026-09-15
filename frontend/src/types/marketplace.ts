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
  title: string;
  description: string;
  category: string;
  status: string; // DRAFT, OPEN_FOR_PROPOSALS, etc.
  client_id: string;
  assigned_designer_id: string | null;
  budget: number;
  expected_delivery_days: number;
  created_at: string;
  updated_at: string;
}
