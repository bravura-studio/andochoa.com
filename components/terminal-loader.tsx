"use client";

import { useEffect, useState } from "react";

const FRAMES = ["|", "/", "—", "\\"];

export function TerminalLoader() {
  const [frameIndex, setFrameIndex] = useState(0);

  useEffect(() => {
    const interval = window.setInterval(() => {
      setFrameIndex((current) => (current + 1) % FRAMES.length);
    }, 120);

    return () => window.clearInterval(interval);
  }, []);

  return (
    <section className="space-y-4">
      <div className="overflow-hidden rounded-[2rem] border border-dashed border-white/15 bg-white/[0.045] shadow-terminal backdrop-blur-xl">
        <div className="flex items-center justify-between border-b border-dashed border-white/10 bg-black/45 px-4 py-3 text-xs uppercase tracking-[0.3em] text-white/40">
          <div className="flex items-center gap-2">
            <span className="h-3 w-3 rounded-full bg-white/82" />
            <span className="h-3 w-3 rounded-full bg-white/34" />
            <span className="h-3 w-3 rounded-full bg-white/18" />
          </div>
          <span>loading</span>
          <span>{FRAMES[frameIndex]}</span>
        </div>

        <div className="space-y-4 bg-black/35 px-5 py-8 sm:px-6">
          <p className="text-[11px] uppercase tracking-[0.34em] text-white/38">terminal spinner</p>
          <div className="rounded-[1.5rem] border border-dashed border-white/12 bg-white/[0.03] p-5">
            <p className="text-sm text-white/84">
              <span className="text-white/44">andre@andochoa</span>
              <span className="mx-2 text-white/24">~/workspace</span>
              <span className="text-white">{FRAMES[frameIndex]}</span>
            </p>
            <p className="mt-4 text-sm leading-7 text-white/58">
              Rendering the next surface. Preserving the shell while content loads.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
