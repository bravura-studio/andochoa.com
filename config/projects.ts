export type ProjectStatus = "active" | "paused" | "planned";

export type Project = {
  name: string;
  description: string;
  status: ProjectStatus;
  url: string;
  logo: string;
};

export const projects: Project[] = [
  {
    name: "Tmaker",
    description: "A focused workspace for makers to capture ideas, ship faster, and keep momentum visible.",
    status: "paused",
    url: "https://tmaker.io",
    logo: "TM",
  },
  {
    name: "Scripta",
    description: "The publishing layer for founder essays, notes, and operating-system thinking behind BUILD.FUN.FREE.",
    status: "active",
    url: "https://andochoa.com",
    logo: "SC",
  },
  {
    name: "Tycoon",
    description: "A real-estate workflow bet aimed at making deal flow and evaluation easier for investors.",
    status: "planned",
    url: "https://tycoon.pt",
    logo: "TY",
  },
  {
    name: "Striva",
    description: "An operations product for small businesses that want less admin drag and more execution speed.",
    status: "planned",
    url: "https://striva.pt",
    logo: "ST",
  },
];
