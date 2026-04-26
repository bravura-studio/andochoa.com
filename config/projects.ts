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
    description: "Talent marketplace project currently paused while the broader portfolio gets reshaped.",
    status: "paused",
    url: "https://tmaker.com",
  },
  {
    slug: "scripta",
    name: "Scripta",
    description: "Personal brand content engine for BUILD.FUN.FREE running at andochoa.com.",
    status: "active",
    url: "https://andochoa.com",
  },
  {
    slug: "tycoon",
    name: "Tycoon",
    description: "Real estate workflow still in planning mode.",
    status: "planned",
    url: null,
  },
  {
    slug: "striva",
    name: "Striva",
    description: "Operations software idea queued behind the current publishing engine.",
    status: "planned",
    url: null,
  },
];
