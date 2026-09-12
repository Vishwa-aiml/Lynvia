export interface Designer {
  id: string;
  name: string;
  specialty: string;
  location: string;
  image: string;
  portrait: string;
  tags: string[];
  rating: number;
  projects: number;
  quote: string;
}

export const designers: Designer[] = [
  {
    id: "aria-santos",
    name: "Aria Santos",
    specialty: "Brand Identity",
    location: "Lisbon, PT",
    image: "https://images.unsplash.com/photo-1636633762833-5d1658f1e29b?q=80&w=1200&auto=format&fit=crop",
    portrait: "https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?q=80&w=800&auto=format&fit=crop",
    tags: ["Branding", "Logo", "Identity"],
    rating: 4.9,
    projects: 84,
    quote: "Design is not just what it looks like—design is how it works.",
  },
  {
    id: "kai-nakamura",
    name: "Kai Nakamura",
    specialty: "Motion & Digital",
    location: "Tokyo, JP",
    image: "https://images.unsplash.com/photo-1611532736597-de2d4265fba3?q=80&w=1200&auto=format&fit=crop",
    portrait: "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?q=80&w=800&auto=format&fit=crop",
    tags: ["Motion", "UI/UX", "Digital Art"],
    rating: 4.8,
    projects: 112,
    quote: "Every pixel has a purpose. Every frame tells a story.",
  },
  {
    id: "nova-osei",
    name: "Nova Osei",
    specialty: "Editorial & Type",
    location: "Accra, GH",
    image: "https://images.unsplash.com/photo-1586281380349-632531db7ed4?q=80&w=1200&auto=format&fit=crop",
    portrait: "https://images.unsplash.com/photo-1531123897727-8f129e1688ce?q=80&w=800&auto=format&fit=crop",
    tags: ["Editorial", "Typography", "Print"],
    rating: 4.9,
    projects: 67,
    quote: "Typography is the voice of design. I make it speak volumes.",
  },
  {
    id: "soren-berg",
    name: "Søren Berg",
    specialty: "Packaging Design",
    location: "Copenhagen, DK",
    image: "https://images.unsplash.com/photo-1626785774573-4b799315345d?q=80&w=1200&auto=format&fit=crop",
    portrait: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?q=80&w=800&auto=format&fit=crop",
    tags: ["Packaging", "3D", "Luxury"],
    rating: 4.7,
    projects: 53,
    quote: "The best design is invisible. It just feels right.",
  },
  {
    id: "elena-moore",
    name: "Elena Moore",
    specialty: "Web & Interaction",
    location: "New York, US",
    image: "https://images.unsplash.com/photo-1600132806370-bf17e65e942f?q=80&w=1200&auto=format&fit=crop",
    portrait: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?q=80&w=800&auto=format&fit=crop",
    tags: ["Web Design", "Interaction", "Figma"],
    rating: 4.9,
    projects: 98,
    quote: "Interfaces should feel like second nature, not second-guessing.",
  },
  {
    id: "marc-fontaine",
    name: "Marc Fontaine",
    specialty: "Photography & Art Dir.",
    location: "Paris, FR",
    image: "https://images.unsplash.com/photo-1561070791-2526d30994b5?q=80&w=1200&auto=format&fit=crop",
    portrait: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?q=80&w=800&auto=format&fit=crop",
    tags: ["Photography", "Art Direction", "Fashion"],
    rating: 4.8,
    projects: 76,
    quote: "A single image should hold an entire world within it.",
  },
];
