"use client";

import Image from "next/image";
import Link from "next/link";
import { Command } from "lucide-react";
import type { ReactNode } from "react";
import { usePathname } from "next/navigation";

const navItems = [
  { href: "/posts", label: "posts" },
  { href: "/vault", label: "vault" },
  { href: "/about", label: "about" },
];

const eyebrowByPath: Record<string, string> = {
  "/": "andochoa.com boot sequence",
  "/posts": "directory /posts",
  "/vault": "directory /vault",
  "/about": "directory /about",
};

export function SiteShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const eyebrow = eyebrowByPath[pathname] ?? "andochoa.com boot sequence";

  return (
    <div className="relative min-h-screen overflow-hidden">
      <div className="mx-auto flex min-h-screen max-w-7xl px-4 py-5 sm:px-6 lg:px-8">
        <div className="grid w-full gap-4 lg:grid-cols-[260px_minmax(0,1fr)]">
          <aside className="animate-fade-up rounded-[2rem] border border-dashed border-white/15 bg-white/5 p-5 shadow-terminal backdrop-blur-xl">
            <div className="flex h-full flex-col">
              <Link className="flex items-center gap-4 border-b border-dashed border-white/12 pb-5" href="/">
                <div className="relative h-12 w-12 overflow-hidden rounded-2xl border border-dashed border-white/20 bg-black/50">
                  <Image
                    alt="ANDOCHOA wordmark"
                    className="object-cover grayscale"
                    fill
                    priority
                    sizes="48px"
                    src="/logo.jpg"
                  />
                </div>
                <div className="min-w-0">
                  <p className="text-[10px] uppercase tracking-[0.38em] text-white/45">{eyebrow}</p>
                  <p className="mt-2 text-sm leading-6 text-white/88">founder notes, systems, and experiments</p>
                </div>
              </Link>

              <nav aria-label="Primary" className="mt-6 flex flex-col gap-2 text-sm text-white/62">
                <Link
                  className={`rounded-2xl border border-dashed px-4 py-3 transition ${
                    pathname === "/"
                      ? "border-white/20 bg-white/10 text-white"
                      : "border-white/10 bg-white/[0.03] hover:border-white/18 hover:bg-white/[0.06] hover:text-white/90"
                  }`}
                  href="/"
                >
                  [home]
                </Link>
                {navItems.map((item) => (
                  <Link
                    className={`rounded-2xl border border-dashed px-4 py-3 transition ${
                      pathname === item.href
                        ? "border-white/20 bg-white/10 text-white"
                        : "border-white/10 bg-white/[0.03] hover:border-white/18 hover:bg-white/[0.06] hover:text-white/90"
                    }`}
                    href={item.href}
                    key={item.href}
                  >
                    [{item.label}]
                  </Link>
                ))}
              </nav>

              <div className="mt-6 rounded-[1.5rem] border border-dashed border-white/10 bg-black/30 p-4 text-xs leading-6 text-white/52">
                <div className="flex items-center gap-2">
                  <span className="h-2.5 w-2.5 rounded-full bg-white/80" />
                  <span className="h-2.5 w-2.5 rounded-full bg-white/35" />
                  <span className="h-2.5 w-2.5 rounded-full bg-white/18" />
                </div>
                <p className="mt-4">Minimal shell, sparse spacing, monochrome surfaces.</p>
              </div>
            </div>
          </aside>

          <div className="flex min-h-[calc(100vh-2.5rem)] flex-col rounded-[2rem] border border-dashed border-white/15 bg-white/[0.045] shadow-terminal backdrop-blur-2xl">
            <header className="animate-fade-up border-b border-dashed border-white/12 px-4 py-4 sm:px-6">
              <div className="rounded-[1.6rem] border border-dashed border-white/12 bg-black/45">
                <div className="flex items-center justify-between rounded-t-[1.5rem] border-b border-dashed border-white/10 px-4 py-3 text-xs text-white/42">
                  <div className="flex items-center gap-2">
                    <span className="h-3 w-3 rounded-full bg-white/80" />
                    <span className="h-3 w-3 rounded-full bg-white/35" />
                    <span className="h-3 w-3 rounded-full bg-white/18" />
                  </div>
                  <div className="flex items-center gap-2 uppercase tracking-[0.28em]">
                    <Command className="h-3.5 w-3.5" />
                    <span>terminal</span>
                  </div>
                  <span>{pathname === "/" ? "~" : pathname}</span>
                </div>
                <div className="flex items-center gap-3 px-4 py-4 text-sm text-white/78">
                  <span className="text-white/38">andre</span>
                  <span className="text-white/22">~/build.fun.free</span>
                  <span className="text-white/88">$_</span>
                  <span className="h-4 w-px bg-white/20" />
                  <span className="text-white/52">clean, sparse, developer-elegant</span>
                </div>
              </div>
            </header>

            <main className="flex-1 px-4 py-6 sm:px-6 sm:py-8">{children}</main>

            <footer className="border-t border-dashed border-white/12 px-4 py-4 text-sm text-white/42 sm:px-6">
              Keep building. -Ochoa
            </footer>
          </div>
        </div>
      </div>
    </div>
  );
}
