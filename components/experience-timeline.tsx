"use client";

import { useState } from "react";
import type { CvEntry } from "@/config/cv";

export function ExperienceTimeline({ entries }: { entries: CvEntry[] }) {
  const [expanded, setExpanded] = useState<string | null>(null);

  return (
    <div className="relative pl-4">
      {/* Vertical dashed line */}
      <div
        className="absolute bottom-2 left-0 top-2 w-px"
        style={{
          backgroundImage: "repeating-linear-gradient(to bottom, rgba(255,255,255,0.14) 0px, rgba(255,255,255,0.14) 4px, transparent 4px, transparent 8px)",
        }}
      />

      <div className="space-y-3">
        {entries.map((role) => {
          const key = `${role.company}-${role.role}`;
          const isOpen = expanded === key;

          return (
            <article className="relative" key={key}>
              {/* Timeline dot */}
              <span className="absolute -left-[17px] top-[14px] h-2 w-2 rounded-full border border-dashed border-white/24 bg-background" />

              <button
                className="w-full text-left"
                onClick={() => setExpanded(isOpen ? null : key)}
                type="button"
              >
                <div className="shell-card p-4 transition hover:bg-white/[0.03]">
                  <div className="flex flex-col gap-1 sm:flex-row sm:items-start sm:justify-between">
                    <div>
                      <h2 className="text-[14px] text-white">{role.role}</h2>
                      <p className="mt-0.5 text-[11px] text-white/38">{role.company}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <p className="text-[10px] uppercase tracking-[0.2em] text-white/28">{role.period}</p>
                      <span className="text-[10px] text-white/20">{isOpen ? "−" : "+"}</span>
                    </div>
                  </div>
                  <p className="mt-3 text-[13px] leading-7 text-white/54">{role.summary}</p>

                  {isOpen && role.highlights.length > 0 && (
                    <ul className="mt-3 space-y-1.5 border-t border-white/7 pt-3">
                      {role.highlights.map((h) => (
                        <li className="flex gap-2 text-[12px] leading-6 text-white/40" key={h}>
                          <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-white/20" />
                          {h}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              </button>
            </article>
          );
        })}
      </div>
    </div>
  );
}
