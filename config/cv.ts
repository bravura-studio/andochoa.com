export type CvEntry = {
  company: string;
  role: string;
  period: string;
  summary: string;
  highlights: string[];
};

export type CvSection = {
  title: string;
  items: string[];
};

export const cvProfile = {
  name: "Andre Ochoa",
  title: "Founder, product builder, and operator",
  location: "Portugal",
  summary:
    "Builder with an economics and finance background who crossed into product, code, and entrepreneurship. I like turning rough ideas into useful products, documenting the process in public, and building systems that create more autonomy over time.",
  bio: ["Builder. Product leader turned indie founder. Shipping products with AI agent teams from Porto, Portugal."],
};

export const cvExperience: CvEntry[] = [
  {
    company: "BUILD.FUN.FREE",
    role: "Founder",
    period: "Current",
    summary: "Building products in public and using writing as both distribution and reflection.",
    highlights: [
      "Shaping a portfolio around product strategy, AI leverage, and founder-led execution.",
      "Turning live work into essays, prompts, and operating principles that compound.",
    ],
  },
  {
    company: "Jscrambler",
    role: "Developer security products",
    period: "Previous",
    summary: "Worked on developer-facing security products with a strong bias toward clarity and practical outcomes.",
    highlights: [
      "Balanced customer context, roadmap tradeoffs, and execution detail across cross-functional teams.",
      "Learned how to translate technical constraints into product decisions that users could actually feel.",
    ],
  },
  {
    company: "knok",
    role: "Digital health product work",
    period: "Previous",
    summary: "Helped shape digital healthcare experiences in a fast-moving environment.",
    highlights: [
      "Worked across operations, product delivery, and user needs where reliability mattered.",
      "Built comfort navigating ambiguity, stakeholder friction, and iterative product discovery.",
    ],
  },
  {
    company: "Critical TechWorks",
    role: "Learned product inside large systems",
    period: "Previous",
    summary: "Developed product instincts inside a large-scale technology organization.",
    highlights: [
      "Operated close to engineering and learned how structure helps, and where it starts to slow good work down.",
      "Strengthened the habit of turning messy inputs into concrete next steps.",
    ],
  },
  {
    company: "Sonae MC",
    role: "Started in finance, learned the business",
    period: "Earlier",
    summary: "Started from the numbers side and learned how businesses really move underneath the narrative.",
    highlights: [
      "Built fluency in planning, operations, and commercial reality before moving deeper into product.",
      "Carried that operator lens forward into every later role.",
    ],
  },
];

export const cvEducation: CvSection = {
  title: "Foundation",
  items: ["Catolica Portuguesa University — Economics and finance foundation"],
};

export const cvSkills: CvSection = {
  title: "Operating modes",
  items: [
    "Founder-led product strategy",
    "Product discovery and validation",
    "0-to-1 execution",
    "AI-assisted building workflows",
    "Writing in public",
    "Cross-functional communication",
    "Operational thinking",
  ],
};

export const cvLinks = [
  { label: "X", href: "https://x.com/andochoa", value: "x.com/andochoa" },
  { label: "LinkedIn", href: "https://linkedin.com/in/andreochoa", value: "linkedin.com/in/andreochoa" },
  { label: "GitHub", href: "https://github.com/AndOchoa", value: "github.com/AndOchoa" },
  { label: "Cal.com", href: "https://cal.com/andochoa/chitchat", value: "cal.com/andochoa/chitchat" },
];
