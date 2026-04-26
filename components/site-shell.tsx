"use client";

import { useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { Menu, X } from "lucide-react";
import type { ReactNode } from "react";

const activityItems = [
  { href: "/", label: "Home", icon: "⌂", key: "home" },
  { href: "/posts", label: "Posts", icon: "✎", key: "posts" },
  { href: "/vault", label: "Vault", icon: "◆", key: "vault" },
  { href: "/about", label: "About", icon: "○", key: "about" },
] as const;

type SiteTab = {
  label: string;
  href?: string;
  active?: boolean;
  tone?: "default" | "alert";
};

type Breadcrumb = {
  label: string;
  href?: string;
  tone?: "default" | "alert";
};

type SiteShellProps = {
  activityKey: (typeof activityItems)[number]["key"];
  sidebarTitle: string;
  sidebar: ReactNode;
  tabs: SiteTab[];
  breadcrumbs: Breadcrumb[];
  statusMeta: string;
  children: ReactNode;
  mobileSidebarOpen?: boolean;
  onMobileSidebarOpenChange?: (open: boolean) => void;
};

export function SiteShell({
  activityKey,
  sidebarTitle,
  sidebar,
  tabs,
  breadcrumbs,
  statusMeta,
  children,
  mobileSidebarOpen: controlledOpen,
  onMobileSidebarOpenChange,
}: SiteShellProps) {
  const [internalOpen, setInternalOpen] = useState(false);
  const mobileSidebarOpen = controlledOpen ?? internalOpen;
  const setMobileSidebarOpen = (open: boolean) => {
    setInternalOpen(open);
    onMobileSidebarOpenChange?.(open);
  };

  return (
    <div className="min-h-screen bg-background px-3 py-3 pb-[calc(52px+1.5rem)] text-foreground sm:px-5 sm:py-5 lg:pb-5">
      <div className="shell-frame mx-auto flex min-h-[calc(100dvh-76px)] max-w-[1440px] flex-col sm:min-h-[calc(100dvh-2.5rem)]">
        <div className="shell-chrome flex h-10 items-center gap-2 border-b px-3">
          <span className="h-2.5 w-2.5 rounded-full bg-[#ff5f57]" />
          <span className="h-2.5 w-2.5 rounded-full bg-[#febc2e]" />
          <span className="h-2.5 w-2.5 rounded-full bg-[#28c840]" />
          <Link aria-label="ANDOCHOA home" className="ml-2 hidden items-center sm:flex" href="/">
            <Image alt="ANDOCHOA wordmark" className="h-4 w-auto object-contain opacity-80" height={16} priority src="/logo.jpg" width={90} />
          </Link>
          <div className="flex-1 text-center text-[11px] text-white/30">andochoa.com</div>
          <button
            aria-expanded={mobileSidebarOpen}
            aria-label={mobileSidebarOpen ? "Close sidebar" : "Open sidebar"}
            className="inline-flex h-8 w-8 items-center justify-center rounded-md border border-white/8 text-white/50 transition hover:bg-white/[0.04] hover:text-white lg:hidden"
            onClick={() => setMobileSidebarOpen(!mobileSidebarOpen)}
            type="button"
          >
            {mobileSidebarOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
          </button>
        </div>

        <div className="flex min-h-0 flex-1">
          <nav aria-label="Activity" className="shell-chrome hidden w-[42px] shrink-0 flex-col items-center gap-1 border-r py-3 lg:flex">
            {activityItems.map((item) => (
              <Link
                aria-current={item.key === activityKey ? "page" : undefined}
                className={`flex h-8 w-8 items-center justify-center rounded-md text-sm transition ${
                  item.key === activityKey ? "bg-white/[0.06] text-white" : "text-white/28 hover:bg-white/[0.04] hover:text-white/65"
                }`}
                href={item.href}
                key={item.href}
                title={item.label}
              >
                {item.icon}
              </Link>
            ))}
          </nav>

          <aside className="shell-chrome hidden w-[220px] shrink-0 border-r lg:flex lg:flex-col">
            <div className="border-b px-4 py-3 text-[10px] uppercase tracking-[0.28em] text-white/28">{sidebarTitle}</div>
            <div className="min-h-0 flex-1 overflow-y-auto px-2 py-2">{sidebar}</div>
          </aside>

          <div className="flex min-h-0 min-w-0 flex-1 flex-col">
            <div className="shell-chrome hidden min-h-[34px] items-stretch overflow-x-auto border-b lg:flex">
              {tabs.map((tab, index) => {
                const className = tab.active
                  ? tab.tone === "alert"
                    ? "bg-background text-[#ff8a8a]"
                    : "bg-background text-white"
                  : tab.tone === "alert"
                    ? "text-[#ff8a8a]/65 hover:bg-white/[0.04]"
                    : "text-white/42 hover:bg-white/[0.04]";

                return tab.href ? (
                  <Link
                    className={`group relative flex shrink-0 items-center gap-2 border-r px-4 text-[11px] ${className}`}
                    href={tab.href}
                    key={`${tab.label}-${index}`}
                  >
                    <span>{tab.label}</span>
                    <span className="opacity-0 transition group-hover:opacity-100">×</span>
                  </Link>
                ) : (
                  <div className={`relative flex shrink-0 items-center gap-2 border-r px-4 text-[11px] ${className}`} key={`${tab.label}-${index}`}>
                    <span>{tab.label}</span>
                    <span className="text-white/20">×</span>
                  </div>
                );
              })}
            </div>

            <div className="hidden border-b border-white/7 px-4 py-1.5 text-[11px] text-white/28 lg:block">
              <div className="flex flex-wrap items-center gap-2">
                {breadcrumbs.map((crumb, index) => (
                  <div className="contents" key={`${crumb.label}-${index}`}>
                    {crumb.href ? (
                      <Link className={crumb.tone === "alert" ? "text-[#ff8a8a]/80" : "text-white/42 hover:text-white/68"} href={crumb.href}>
                        {crumb.label}
                      </Link>
                    ) : (
                      <span className={crumb.tone === "alert" ? "text-[#ff8a8a]/80" : "text-white/42"}>{crumb.label}</span>
                    )}
                    {index < breadcrumbs.length - 1 ? <span className="text-white/18">›</span> : null}
                  </div>
                ))}
              </div>
            </div>

            <div className="min-h-0 flex-1 overflow-y-auto bg-background px-4 py-4 sm:px-6 sm:py-6">{children}</div>

            <div className="shell-chrome flex h-6 items-center justify-between border-t px-3 text-[10px] text-white/28">
              <span>Keep building. -Ochoa</span>
              <span>{statusMeta}</span>
            </div>
          </div>
        </div>

        <nav aria-label="Mobile activity" className="shell-chrome fixed bottom-0 left-3 right-3 z-40 grid h-[52px] grid-cols-4 border-t lg:hidden sm:left-5 sm:right-5">
          {activityItems.map((item) => (
            <Link
              aria-current={item.key === activityKey ? "page" : undefined}
              className={`flex flex-col items-center justify-center gap-1 text-[10px] transition ${
                item.key === activityKey ? "bg-white/[0.06] text-white" : "text-white/32"
              }`}
              href={item.href}
              key={item.href}
            >
              <span className="text-sm">{item.icon}</span>
              <span>{item.label}</span>
            </Link>
          ))}
        </nav>
      </div>

      {mobileSidebarOpen ? (
        <div className="fixed inset-0 z-50 bg-black/70 lg:hidden" onClick={() => setMobileSidebarOpen(false)}>
          <div
            className="shell-chrome h-full w-[280px] border-r px-3 py-3"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="mb-3 flex items-center justify-between border-b border-white/7 pb-3">
              <span className="text-[10px] uppercase tracking-[0.28em] text-white/28">{sidebarTitle}</span>
              <button
                aria-label="Close sidebar"
                className="inline-flex h-8 w-8 items-center justify-center rounded-md border border-white/8 text-white/50"
                onClick={() => setMobileSidebarOpen(false)}
                type="button"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <div className="h-[calc(100%-3rem)] overflow-y-auto">{sidebar}</div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
