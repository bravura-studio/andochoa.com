"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const quickLinks = ["/posts", "/vault", "/about"];

export default function NotFound() {
  const pathname = usePathname() || "/unknown";
  const attemptedPath = pathname === "/" ? "" : pathname.replace(/^\/+/, "");

  return (
    <section className="flex min-h-[70vh] items-center justify-center px-4 py-10">
      <div className="w-full max-w-[500px] overflow-hidden rounded-[16px] border border-dashed border-white/14 bg-white/[0.045] backdrop-blur-xl">
        <div className="relative border-b border-dashed border-white/10 bg-black/45 px-4 py-3 text-xs text-white/42">
          <div className="flex items-center gap-2">
            <span className="h-3 w-3 rounded-full bg-[#ff5f57]" />
            <span className="h-3 w-3 rounded-full bg-[#febc2e]" />
            <span className="h-3 w-3 rounded-full bg-[#28c840]" />
          </div>
          <div className="pointer-events-none absolute inset-x-0 top-1/2 flex -translate-y-1/2 items-center justify-center uppercase tracking-[0.28em]">
            <span>andochoa.com</span>
          </div>
        </div>

        <div className="bg-[#0d0d0d] px-5 py-6 text-sm leading-8 text-white/74 sm:px-6">
          <p className="text-white/90">$ cd /{attemptedPath}</p>
          <p className="text-white/54">bash: command not found: /{attemptedPath}</p>

          <p className="mt-4 text-white/42">&gt; try one of these:</p>
          <div className="mt-2 space-y-1">
            {quickLinks.map((href) => (
              <p key={href}>
                <Link className="border-b border-dashed border-white/45 text-white transition hover:border-white hover:text-white" href={href}>
                  {href}
                </Link>
              </p>
            ))}
          </div>

          <p className="mt-5 text-white/42">&gt; go home</p>
          <p>
            <Link className="border-b border-dashed border-white/45 text-white transition hover:border-white hover:text-white" href="/">
              /
            </Link>
          </p>
        </div>
      </div>
    </section>
  );
}
