"use client";

import { useEffect, useState } from "react";
import { CalendarDays, Download } from "lucide-react";
import Link from "next/link";

const outlineSections = [
  { id: "bio", label: "Bio" },
  { id: "mantra", label: "Mantra" },
  { id: "experience", label: "Experience" },
  { id: "education", label: "Education" },
  { id: "skills", label: "Skills" },
  { id: "contact", label: "Contact" },
];

type AboutSidebarProps = {
  onSectionClick?: () => void;
};

export function AboutSidebar({ onSectionClick }: AboutSidebarProps = {}) {
  const [activeId, setActiveId] = useState<string>("bio");

  useEffect(() => {
    const scrollContainer = document.querySelector("[data-scroll-container]") as HTMLElement | null;

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            setActiveId(entry.target.id);
          }
        }
      },
      {
        root: scrollContainer,
        rootMargin: "-10% 0px -60% 0px",
        threshold: 0,
      },
    );

    for (const section of outlineSections) {
      const el = document.getElementById(section.id);
      if (el) observer.observe(el);
    }

    return () => observer.disconnect();
  }, []);

  function handleAnchorClick(e: React.MouseEvent<HTMLAnchorElement>, id: string) {
    e.preventDefault();
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: "smooth", block: "start" });
      window.history.pushState(null, "", `#${id}`);
      setActiveId(id);
    }
    onSectionClick?.();
  }

  return (
    <div className="space-y-5">
      <div className="space-y-1">
        {outlineSections.map((section) => {
          const isActive = activeId === section.id;
          return (
            <a
              className={`flex items-center gap-0 rounded-md border-l-2 px-3 py-2 text-[12px] transition ${
                isActive
                  ? "border-white/80 bg-white/[0.06] text-white"
                  : "border-transparent text-white/42 hover:bg-white/[0.04] hover:text-white/72"
              }`}
              href={`#${section.id}`}
              key={section.id}
              onClick={(e) => handleAnchorClick(e, section.id)}
            >
              {section.label}
            </a>
          );
        })}
      </div>

      <div className="space-y-2 border-t border-white/7 pt-4">
        <a
          className="flex items-center justify-center gap-2 rounded-md border border-dashed border-white/12 bg-white/[0.03] px-3 py-3 text-[11px] uppercase tracking-[0.18em] text-white/70 transition hover:bg-white/[0.06]"
          download
          href="/ochoa-cv.pdf"
        >
          <Download className="h-4 w-4" />
          Download CV
        </a>
        <Link
          className="flex items-center justify-center gap-2 rounded-md border border-dashed border-white/12 bg-white/[0.03] px-3 py-3 text-[11px] uppercase tracking-[0.18em] text-white/70 transition hover:bg-white/[0.06]"
          href="https://cal.com/andochoa/chitchat"
          rel="noreferrer"
          target="_blank"
        >
          <CalendarDays className="h-4 w-4" />
          Book a call
        </Link>
      </div>
    </div>
  );
}
