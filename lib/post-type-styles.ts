import { cn } from "@/lib/utils";

const postTypeStyles: Record<string, { badge: string; text: string }> = {
  reflection: {
    badge: "border-white/12 bg-white/[0.05] text-white/74",
    text: "text-white/74",
  },
  struggle: {
    badge: "border-white/10 bg-white/[0.04] text-white/68",
    text: "text-white/68",
  },
  win: {
    badge: "border-white/12 bg-white/[0.05] text-white/76",
    text: "text-white/76",
  },
  observation: {
    badge: "border-white/10 bg-white/[0.04] text-white/64",
    text: "text-white/64",
  },
  brainstorm: {
    badge: "border-white/11 bg-white/[0.045] text-white/70",
    text: "text-white/70",
  },
};

const fallbackStyles = {
  badge: "border-white/8 bg-white/[0.04] text-white/45",
  text: "text-white/45",
};

export function getPostTypeStyles(type: string) {
  const normalizedType = type.trim().toLowerCase();

  return postTypeStyles[normalizedType] ?? fallbackStyles;
}

export function getPostTypeBadgeClassName(type: string) {
  return cn("rounded-md border px-2.5 py-1 text-[9px] uppercase tracking-[0.18em]", getPostTypeStyles(type).badge);
}
