export type ProjectStatus = "active" | "paused" | "planned";

export type PortfolioProject = {
  slug: string;
  name: string;
  description: string;
  status: ProjectStatus;
  url: string | null;
};

export const projects: PortfolioProject[] = [
  {
    slug: "tmaker",
    name: "Tmaker",
    description: "mini-tool factory",
    status: "paused",
    url: "https://tmaker.io",
  },
  {
    slug: "scripta",
    name: "Scripta",
    description: "content engine",
    status: "active",
    url: "https://andochoa.com",
  },
  {
    slug: "tycoon",
    name: "Tycoon",
    description: "real estate deal sourcing",
    status: "planned",
    url: null,
  },
  {
    slug: "striva",
    name: "Striva",
    description: "agentic finance for SMBs",
    status: "planned",
    url: null,
  },
];
