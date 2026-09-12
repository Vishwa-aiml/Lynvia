export interface Project {
  id: string;
  title: string;
  category: string;
  designer: string;
  image: string;
  size: "large" | "medium" | "small";
  year: string;
}

export const featuredProjects: Project[] = [
  {
    id: "brand-identity-sketch",
    title: "Brand Identity Sketch",
    category: "Logo Design",
    designer: "Aria Santos",
    image: "https://images.unsplash.com/photo-1572044162444-ad60f128bdea?q=80&w=1400&auto=format&fit=crop",
    size: "large",
    year: "2026",
  },
  {
    id: "logo-system",
    title: "Logo System",
    category: "Brand Identity",
    designer: "Kai Nakamura",
    image: "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?q=80&w=1000&auto=format&fit=crop",
    size: "medium",
    year: "2026",
  },
  {
    id: "graphic-design-workspace",
    title: "Creative Workspace",
    category: "Graphic Design",
    designer: "Nova Osei",
    image: "https://images.unsplash.com/photo-1542621334-a254cf47733d?q=80&w=1000&auto=format&fit=crop",
    size: "medium",
    year: "2025",
  },
  {
    id: "type-and-colour",
    title: "Type & Colour",
    category: "Typography",
    designer: "Søren Berg",
    image: "https://images.unsplash.com/photo-1561070791-2526d30994b5?q=80&w=1400&auto=format&fit=crop",
    size: "large",
    year: "2026",
  },
];
