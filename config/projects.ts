export type ProjectStatus = "active" | "paused" | "planned";

export type PortfolioProject = {
  slug: string;
  name: string;
  description: string;
  status: ProjectStatus;
  href: string;
  mark: string;
};

export const projects: PortfolioProject[] = [
  {
    slug: "voice-notes",
    name: "Voice Notes",
    description: "Voice-first capture system for turning founder thoughts into publishable raw material.",
    status: "active",
    href: "/vault",
    mark: "VN",
  },
  {
    slug: "tycoon",
    name: "Tycoon.pt",
    description: "Real estate wholesale workflow focused on investor-ready opportunities with clear ROI signals.",
    status: "paused",
    href: "/vault",
    mark: "TY",
  },
  {
    slug: "striva",
    name: "Striva.pt",
    description: "Operations software for removing administrative drag from small and medium businesses.",
    status: "planned",
    href: "/vault",
    mark: "ST",
  },
  {
    slug: "scripta",
    name: "Scripta",
    description: "The public writing engine for BUILD.FUN.FREE: essays, field notes, and experiments in motion.",
    status: "active",
    href: "/",
    mark: "SC",
  },
];
