import { cn } from "@/lib/utils";

const postTypeStyles: Record<string, { badge: string; text: string }> = {
  reflection: {
    badge: "border-[rgba(59,130,246,0.3)] bg-[rgba(59,130,246,0.15)] text-[rgba(59,130,246,0.8)]",
    text: "text-[rgba(59,130,246,0.8)]",
  },
  struggle: {
    badge: "border-[rgba(244,63,94,0.3)] bg-[rgba(244,63,94,0.15)] text-[rgba(244,63,94,0.8)]",
    text: "text-[rgba(244,63,94,0.8)]",
  },
  win: {
    badge: "border-[rgba(34,197,94,0.3)] bg-[rgba(34,197,94,0.15)] text-[rgba(34,197,94,0.8)]",
    text: "text-[rgba(34,197,94,0.8)]",
  },
  observation: {
    badge: "border-[rgba(234,179,8,0.3)] bg-[rgba(234,179,8,0.15)] text-[rgba(234,179,8,0.8)]",
    text: "text-[rgba(234,179,8,0.8)]",
  },
  brainstorm: {
    badge: "border-[rgba(168,85,247,0.3)] bg-[rgba(168,85,247,0.15)] text-[rgba(168,85,247,0.8)]",
    text: "text-[rgba(168,85,247,0.8)]",
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
