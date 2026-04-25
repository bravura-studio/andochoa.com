"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const quickLinks = [
  {
    href: "/posts",
    label: "/posts",
    detail: "Open the writing workspace.",
  },
  {
    href: "/vault",
    label: "/vault",
    detail: "Inspect the knowledge directory.",
  },
  {
    href: "/about",
    label: "/about",
    detail: "Read the founder profile.",
  },
];

export default function NotFound() {
  const pathname = usePathname() || "/unknown";

  return (
    <section className="space-y-4">
      <div className="overflow-hidden rounded-[2rem] border border-dashed border-white/15 bg-white/[0.045] shadow-terminal backdrop-blur-xl">
        <div className="relative border-b border-dashed border-white/10 bg-black/45 px-4 py-3 text-xs text-white/42 sm:px-5">
          <div className="flex items-center gap-2">
            <span className="h-3 w-3 rounded-full bg-white/82" />
            <span className="h-3 w-3 rounded-full bg-white/34" />
            <span className="h-3 w-3 rounded-full bg-white/18" />
          </div>
          <div className="pointer-events-none absolute inset-x-0 top-1/2 flex -translate-y-1/2 items-center justify-center uppercase tracking-[0.3em]">
            <span>command not found</span>
          </div>
          <div className="flex justify-end uppercase tracking-[0.28em]">
            <span>404</span>
          </div>
        </div>

        <div className="grid gap-px bg-white/10 lg:grid-cols-[minmax(0,1.2fr)_320px]">
          <div className="bg-black/35 px-5 py-6 sm:px-6 sm:py-8">
            <p className="text-[11px] uppercase tracking-[0.35em] text-white/40">missing route</p>
            <div className="mt-6 rounded-[1.6rem] border border-dashed border-white/12 bg-white/[0.03] p-5 text-sm leading-8 text-white/72">
              <p className="text-white/88">$ cd {pathname}</p>
              <p className="text-white/56">bash: command not found: {pathname.replace(/^\//, "") || "/"}</p>
              <p className="mt-5 text-[11px] uppercase tracking-[0.34em] text-white/40">&gt; try one of these</p>
            </div>

            <div className="mt-6 grid gap-3 sm:grid-cols-3">
              {quickLinks.map((link) => (
                <Link
                  className="rounded-[1.4rem] border border-dashed border-white/14 bg-white/[0.045] p-4 transition hover:-translate-y-1 hover:border-white/24 hover:bg-white/[0.08]"
                  href={link.href}
                  key={link.href}
                >
                  <span className="text-[11px] uppercase tracking-[0.32em] text-white/40">{link.label}</span>
                  <p className="mt-4 text-sm leading-6 text-white/84">{link.detail}</p>
                </Link>
              ))}
            </div>

            <Link
              className="mt-6 inline-flex rounded-full border border-dashed border-white/16 bg-white px-5 py-3 text-sm font-medium text-black transition hover:bg-white/90"
              href="/"
            >
              [go home →]
            </Link>
          </div>

          <aside className="bg-black/45 px-4 py-5 sm:px-5">
            <div className="rounded-[1.5rem] border border-dashed border-white/12 bg-white/[0.04] p-4">
              <p className="text-[11px] uppercase tracking-[0.34em] text-white/38">status</p>
              <dl className="mt-4 space-y-4 text-sm">
                <div className="flex items-center justify-between gap-4 border-b border-dashed border-white/10 pb-3">
                  <dt className="text-white/42">Code</dt>
                  <dd className="text-white/84">404</dd>
                </div>
                <div className="flex items-center justify-between gap-4 border-b border-dashed border-white/10 pb-3">
                  <dt className="text-white/42">Shell</dt>
                  <dd className="text-white/84">Monochrome terminal</dd>
                </div>
                <div className="flex items-center justify-between gap-4">
                  <dt className="text-white/42">Recovery</dt>
                  <dd className="text-white/84">Indexed routes</dd>
                </div>
              </dl>
            </div>

            <div className="mt-4 rounded-[1.5rem] border border-dashed border-white/12 bg-white/[0.035] p-4 text-sm leading-7 text-white/54">
              <p className="text-[11px] uppercase tracking-[0.34em] text-white/38">operator note</p>
              <p className="mt-3">
                Missing pages should feel like part of the same workspace, not a visual exception.
              </p>
            </div>
          </aside>
        </div>
      </div>
    </section>
  );
}
