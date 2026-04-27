"use client";

import { useEffect, useState } from "react";
import { ArrowUp } from "lucide-react";

function getScrollContainer(): HTMLElement | null {
  return document.querySelector("[data-scroll-container]") as HTMLElement | null;
}

export function BackToTop({ triggerSectionId }: { triggerSectionId: string }) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const trigger = document.getElementById(triggerSectionId);
    const scrollContainer = getScrollContainer();
    if (!trigger || !scrollContainer) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        setVisible(!entry.isIntersecting);
      },
      { root: scrollContainer, threshold: 0.1 },
    );

    observer.observe(trigger);
    return () => observer.disconnect();
  }, [triggerSectionId]);

  if (!visible) return null;

  return (
    <button
      aria-label="Back to top"
      className="fixed bottom-20 right-5 z-50 flex h-9 w-9 items-center justify-center rounded-full border border-dashed border-white/20 bg-background/80 text-white/50 backdrop-blur-md transition hover:bg-white/[0.06] hover:text-white/80 lg:bottom-10"
      onClick={() => {
        const container = getScrollContainer();
        if (container) container.scrollTo({ top: 0, behavior: "smooth" });
      }}
      type="button"
    >
      <ArrowUp className="h-4 w-4" />
    </button>
  );
}
