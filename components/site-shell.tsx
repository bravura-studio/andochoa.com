"use client";

import { useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { Menu, X } from "lucide-react";
import type { ReactNode } from "react";
import { usePathname } from "next/navigation";

const navItems = [
  { href: "/", label: "home" },
  { href: "/posts", label: "posts" },
  { href: "/vault", label: "vault" },
  { href: "/about", label: "about" },
] as const;

export function SiteShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  function isActive(href: string) {
    return href === "/" ? pathname === "/" : pathname === href || pathname.startsWith(`${href}/`);
  }

  const activeItem = navItems.find((item) => isActive(item.href)) ?? navItems[0];

  function closeMobileNav() {
    setMobileNavOpen(false);
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="flex min-h-screen">
        <aside className="shell-card shell-glow fixed inset-y-0 left-0 z-30 hidden w-[220px] rounded-none border-y-0 border-l-0 lg:block">
          <div className="flex h-full flex-col px-5 py-8">
            <Link className="border-b border-dashed border-border/8 pb-8" href="/">
              <div className="flex items-center gap-4">
                <div className="relative h-11 w-11 overflow-hidden rounded-full border border-dashed border-border/15 bg-surface-elevated/80">
                  <Image
                    alt="ANDOCHOA wordmark"
                    className="object-cover grayscale"
                    fill
                    priority
                    sizes="44px"
                    src="/logo.jpg"
                  />
                </div>
                <div className="min-w-0">
                  <p className="text-sm font-bold uppercase tracking-[0.4em] text-foreground">ANDOCHOA</p>
                  <p className="mt-2 text-xs text-text-dim/45">Personal archive for BUILD.FUN.FREE.</p>
                </div>
              </div>
            </Link>

            <nav aria-label="Primary" className="mt-8 flex flex-col gap-1.5 text-[13px] text-text-dim/45">
              {navItems.map((item) => {
                const active = isActive(item.href);

                return (
                  <Link
                    className={`group rounded-md px-3 py-2.5 transition ${
                      active ? "bg-foreground/5 text-foreground" : "hover:bg-foreground/5 hover:text-foreground"
                    }`}
                    href={item.href}
                    key={item.href}
                  >
                    <span className={`mr-2 transition ${active ? "opacity-100" : "opacity-0 group-hover:opacity-100"}`}>&gt;</span>
                    {item.label}
                  </Link>
                );
              })}
            </nav>

            <p className="mt-auto text-[11px] leading-7 text-text-muted/25">Keep building. -Ochoa</p>
          </div>
        </aside>

        <div className="min-h-screen w-full lg:pl-[220px]">
          <header className="sticky top-0 z-20 border-b border-dashed border-border/8 bg-background/90 backdrop-blur">
            <div className="flex items-center justify-between px-4 py-4 sm:px-6 lg:hidden">
              <Link className="text-sm font-bold uppercase tracking-[0.4em] text-foreground" href="/" onClick={closeMobileNav}>
                ANDOCHOA
              </Link>
              <button
                aria-expanded={mobileNavOpen}
                aria-label={mobileNavOpen ? "Close menu" : "Open menu"}
                className="inline-flex h-11 w-11 items-center justify-center rounded-md border border-dashed border-border/10 bg-surface/80 text-foreground transition hover:bg-foreground/5"
                onClick={() => setMobileNavOpen((current) => !current)}
                type="button"
              >
                {mobileNavOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
              </button>
            </div>

            {mobileNavOpen ? (
              <nav aria-label="Mobile primary" className="border-t border-dashed border-border/8 px-4 py-4 sm:px-6 lg:hidden">
                <div className="shell-panel flex flex-col gap-1 p-2">
                  {navItems.map((item) => {
                    const active = isActive(item.href);

                    return (
                      <Link
                        className={`rounded-md px-3 py-3 text-sm transition ${
                          active ? "bg-foreground/5 text-foreground" : "text-text-dim/45 hover:bg-foreground/5 hover:text-foreground"
                        }`}
                        href={item.href}
                        key={item.href}
                        onClick={closeMobileNav}
                      >
                        <span className={`mr-2 ${active ? "opacity-100" : "opacity-0"}`}>&gt;</span>
                        {item.label}
                      </Link>
                    );
                  })}
                </div>
              </nav>
            ) : null}
          </header>

          <main className="px-4 py-6 sm:px-6 sm:py-8 lg:px-10">
            <div className="mx-auto flex min-h-[calc(100vh-3rem)] max-w-[1280px] flex-col">
              <div className="mb-6 hidden items-end justify-between gap-6 lg:flex">
                <div>
                  <p className="shell-label">Active view</p>
                  <h1 className="mt-3 text-2xl font-semibold tracking-[-0.04em] text-foreground">{activeItem.label}</h1>
                </div>
                <p className="max-w-md text-right text-sm leading-7 text-text-dim/45">
                  Monochrome shell. Dashed borders. Type-first layout.
                </p>
              </div>
              <div className="flex-1">{children}</div>
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}
