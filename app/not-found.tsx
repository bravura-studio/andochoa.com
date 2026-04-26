"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { SiteShell } from "@/components/site-shell";

const quickLinks = ["/", "/posts", "/vault", "/about"];

export default function NotFound() {
  const pathname = usePathname() || "/unknown";
  const label = pathname.replace(/^\/+/, "") || "index";

  return (
    <SiteShell
      activityKey="home"
      breadcrumbs={[
        { label: "andochoa.com", href: "/" },
        { label: "file not found", tone: "alert" },
      ]}
      sidebar={
        <div className="space-y-1 text-[12px] text-white/40">
          <div className="rounded-md bg-white/[0.04] px-3 py-2">andochoa.com</div>
          <div className="px-3 py-1.5 text-[#ff8a8a]/80">└─ {label}</div>
        </div>
      }
      sidebarTitle="explorer"
      statusMeta="404 · missing route"
      tabs={[{ active: true, label: label, tone: "alert" }]}
    >
      <div className="flex min-h-[calc(100vh-16rem)] items-center justify-center">
        <div className="w-full max-w-[560px] overflow-hidden rounded-lg border border-dashed border-white/12 bg-[#080808]">
          <div className="flex items-center gap-2 border-b border-white/7 bg-white/[0.02] px-4 py-3">
            <span className="h-2.5 w-2.5 rounded-full bg-[#ff5f57]" />
            <span className="h-2.5 w-2.5 rounded-full bg-[#febc2e]" />
            <span className="h-2.5 w-2.5 rounded-full bg-[#28c840]" />
            <span className="ml-auto text-[10px] uppercase tracking-[0.22em] text-white/26">error</span>
          </div>

          <div className="space-y-4 px-5 py-6 text-[13px] leading-8 text-white/68">
            <p className="text-white">$ cd /{label}</p>
            <p className="text-white/42">bash: no such file or directory: /{label}</p>
            <p className="text-[11px] uppercase tracking-[0.24em] text-white/30">&gt; available paths</p>
            <div className="space-y-1">
              {quickLinks.map((href) => (
                <p key={href}>
                  <Link className="border-b border-dashed border-white/18 text-white/76 hover:border-white/50" href={href}>
                    {href}
                  </Link>
                </p>
              ))}
            </div>
          </div>
        </div>
      </div>
    </SiteShell>
  );
}
