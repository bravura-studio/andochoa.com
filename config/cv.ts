export type CVLink = {
  label: string;
  href: string;
};

export type CVExperience = {
  company: string;
  role: string;
  period: string;
  summary: string;
  highlights: string[];
};

export type CVProject = {
  name: string;
  role: string;
  status: string;
  summary: string;
};

export type CVEducation = {
  school: string;
  degree: string;
  period: string;
};

export type CVData = {
  name: string;
  title: string;
  location: string;
  summary: string;
  links: CVLink[];
  principles: string[];
  strengths: string[];
  featuredProjects: CVProject[];
  experience: CVExperience[];
  education: CVEducation[];
};

export const cv: CVData = {
  name: "Andres Ochoa",
  title: "Builder, product operator, and founder documenting the road to BUILD.FUN.FREE",
  location: "Portugal",
  summary:
    "I build products, write in public, and use code as leverage to turn lived founder problems into software. My background spans finance, consulting, and product leadership, but the through-line is simpler: spot friction, make the system clearer, and ship something useful before certainty shows up.",
  links: [
    { label: "Website", href: "https://andochoa.com" },
    { label: "GitHub", href: "https://github.com/bravura-studio" },
  ],
  principles: [
    "Build from conviction, not committee theater.",
    "Make the work legible while it is still messy.",
    "Use AI to compress execution time, not replace judgment.",
  ],
  strengths: [
    "Product strategy and narrative framing",
    "Zero-to-one prototyping with modern AI tooling",
    "Founder-led writing and content systems",
    "Operating across business, product, and technical constraints",
  ],
  featuredProjects: [
    {
      name: "Scripta",
      role: "Founder",
      status: "Active",
      summary: "Personal publishing engine for essays, journals, and structured founder notes.",
    },
    {
      name: "Tmaker",
      role: "Founder",
      status: "Paused",
      summary: "Maker-focused product experiment shaped around momentum, systems, and execution clarity.",
    },
    {
      name: "Tycoon",
      role: "Founder",
      status: "Planned",
      summary: "Real-estate workflow concept grounded in urgency, demand validation, and operator leverage.",
    },
    {
      name: "Striva",
      role: "Founder",
      status: "Planned",
      summary: "Small-business operations bet focused on reducing admin overhead through software.",
    },
  ],
  experience: [
    {
      company: "BUILD.FUN.FREE",
      role: "Founder",
      period: "2024 - Present",
      summary: "Building a small portfolio of AI-native products while writing openly about the process.",
      highlights: [
        "Shaping product bets, experiments, and messaging across multiple projects.",
        "Using AI-assisted workflows to compress idea-to-prototype cycle time.",
        "Turning raw founder notes into reusable writing and decision assets.",
      ],
    },
    {
      company: "Technology Companies",
      role: "Product Manager",
      period: "Before BUILD.FUN.FREE",
      summary: "Led product work across software teams with a bias for clarity, prioritization, and shipping.",
      highlights: [
        "Worked across roadmap definition, stakeholder alignment, and product delivery.",
        "Learned where corporate process helps and where it quietly kills momentum.",
      ],
    },
    {
      company: "Finance and Consulting",
      role: "Analyst / Operator",
      period: "Earlier career",
      summary: "Started in structured business environments that sharpened analytical thinking and business judgment.",
      highlights: [
        "Built a foundation in economics, finance, and disciplined problem-solving.",
        "Carried that rigor into product and founder work instead of leaving it behind.",
      ],
    },
  ],
  education: [
    {
      school: "Economics and Finance Background",
      degree: "Formal training that preceded the move into product and software",
      period: "Earlier studies",
    },
  ],
};
