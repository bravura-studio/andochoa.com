import Image from "next/image";
import Link from "next/link";
import { Github, Linkedin, Twitter } from "lucide-react";
import { SiteShell } from "@/components/site-shell";
import { TypingStatus } from "@/components/typing-status";
import { projects } from "@/config/projects";
import { getRecentPublishedPosts } from "@/lib/posts";
import { buildPageMetadata } from "@/lib/site";

const socialLinks = [
  { href: "https://x.com/andochoa", icon: Twitter, label: "X" },
  { href: "https://linkedin.com/in/andreochoa", icon: Linkedin, label: "LinkedIn" },
  { href: "https://github.com/AndOchoa", icon: Github, label: "GitHub" },
];

export const metadata = buildPageMetadata({
  description: "A Cursor-like welcome workspace for founder notes, projects, and recent writing from Andre Ochoa.",
});

function formatDate(date: string) {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "2-digit",
    year: "numeric",
  }).format(new Date(date));
}

export default function Home() {
  const recentPosts = getRecentPublishedPosts(2);

  return (
    <SiteShell
      activityKey="home"
      breadcrumbs={[{ label: "andochoa.com", href: "/" }, { label: "welcome" }]}
      sidebar={
        <div className="space-y-5">
          <div className="space-y-1 text-[12px] text-white/40">
            <div className="rounded-md bg-white/[0.06] px-3 py-2 text-white">▸ andochoa.com</div>
            <div className="px-3 py-1.5">└─ welcome</div>
            <Link className="block px-3 py-1.5 hover:text-white/72" href="/posts">
              ├─ posts/
            </Link>
            <Link className="block px-3 py-1.5 hover:text-white/72" href="/vault">
              ├─ vault/
            </Link>
            <Link className="block px-3 py-1.5 hover:text-white/72" href="/about">
              └─ about.md
            </Link>
          </div>

          <div className="shell-card p-4 text-center">
            <div className="relative mx-auto h-12 w-12 overflow-hidden rounded-full border border-dashed border-white/14 bg-black/40">
              <Image alt="Andre Ochoa profile photo" className="object-cover grayscale" fill sizes="48px" src="/profile.jpg" />
            </div>
            <p className="mt-3 text-[12px] text-white">Andre Ochoa</p>
            <p className="mt-1 text-[10px] uppercase tracking-[0.2em] text-white/28">Porto, Portugal</p>
            <div className="mt-3 flex justify-center gap-2">
              {socialLinks.map(({ href, label }) => (
                <Link
                  className="rounded-md border border-white/8 px-2 py-1 text-[10px] text-white/44 transition hover:bg-white/[0.04] hover:text-white/72"
                  href={href}
                  key={href}
                  rel="noreferrer"
                  target="_blank"
                >
                  {label}
                </Link>
              ))}
            </div>
          </div>
        </div>
      }
      sidebarTitle="explorer"
      statusMeta={`welcome · ${recentPosts.length} posts · ${projects.length} projects`}
      tabs={[{ active: true, label: "welcome" }]}
    >
      <section className="flex min-h-[calc(100vh-14rem)] items-center justify-center">
        <div className="w-full max-w-[560px] text-center">
          <div className="relative mx-auto h-[72px] w-[72px] overflow-hidden rounded-full border-2 border-dashed border-white/14 bg-[#111]">
            <Image alt="Andre Ochoa profile photo" className="object-cover grayscale" fill priority sizes="72px" src="/profile.jpg" />
          </div>

          <h1 className="mt-5 text-[28px] font-bold tracking-[-0.05em] text-white sm:text-[32px]">andre ochoa</h1>

          <div className="mt-4">
            <TypingStatus />
          </div>

          <div className="mt-5 inline-flex rounded-md border border-dashed border-white/12 bg-white/[0.02] px-4 py-3">
            <p className="text-[12px] uppercase tracking-[0.45em] text-white/78">BUILD·FUN·FREE</p>
          </div>

          <div className="mt-6 grid gap-4 text-left sm:grid-cols-2">
            <section className="shell-card p-4">
              <div className="flex items-center justify-between gap-3">
                <p className="text-[10px] uppercase tracking-[0.28em] text-white/30">&gt; recent posts</p>
                <Link className="text-[10px] uppercase tracking-[0.2em] text-white/28 hover:text-white/66" href="/posts">
                  all
                </Link>
              </div>

              <div className="mt-4 space-y-3">
                {recentPosts.map((post) => (
                  <Link
                    className="block rounded-md border border-dashed border-white/10 bg-black/25 px-3 py-3 transition hover:bg-white/[0.04]"
                    href={`/posts/${post.slug}`}
                    key={post.slug}
                  >
                    <p className="text-[10px] uppercase tracking-[0.2em] text-white/28">{formatDate(post.date)}</p>
                    <p className="mt-2 text-[13px] text-white">{post.title}</p>
                  </Link>
                ))}
              </div>
            </section>

            <section className="shell-card p-4">
              <p className="text-[10px] uppercase tracking-[0.28em] text-white/30">&gt; projects</p>

              <div className="mt-4 space-y-3">
                {projects.map((project) => {
                  const body = (
                    <>
                      <div>
                        <p className="text-[13px] text-white">{project.name}</p>
                        <p className="mt-1 text-[11px] leading-5 text-white/40">{project.description}</p>
                      </div>
                      <span className="rounded-md border border-white/8 px-2.5 py-1 text-[10px] uppercase tracking-[0.2em] text-white/40">
                        {project.status}
                      </span>
                    </>
                  );

                  return project.url ? (
                    <Link
                      className="flex items-start justify-between gap-3 rounded-md border border-dashed border-white/10 bg-black/25 px-3 py-3 transition hover:bg-white/[0.04]"
                      href={project.url}
                      key={project.slug}
                      rel="noreferrer"
                      target="_blank"
                    >
                      {body}
                    </Link>
                  ) : (
                    <div className="flex items-start justify-between gap-3 rounded-md border border-dashed border-white/10 bg-black/25 px-3 py-3" key={project.slug}>
                      {body}
                    </div>
                  );
                })}
              </div>
            </section>
          </div>
        </div>
      </section>
    </SiteShell>
  );
}
