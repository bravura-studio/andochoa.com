import Image from "next/image";
import Link from "next/link";
import { Github, Linkedin, Twitter } from "lucide-react";
import { TypingStatus } from "@/components/typing-status";
import { projects } from "@/config/projects";
import { getRecentPublishedPosts } from "@/lib/posts";
import { buildPageMetadata } from "@/lib/site";

const socialLinks = [
  { href: "https://x.com/andochoa", icon: Twitter, label: "X" },
  { href: "https://linkedin.com/in/andreochoa", icon: Linkedin, label: "LinkedIn" },
  { href: "https://github.com/AndOchoa", icon: Github, label: "GitHub" },
];

const statusStyles = {
  active: "border-white/15 text-white/72",
  paused: "border-white/12 border-solid text-white/42",
  planned: "border-white/12 border-dashed text-white/42",
} as const;

export const metadata = buildPageMetadata({
  description: "A centered monochrome hub for founder notes, projects, and recent writing from Andre Ochoa.",
});

function formatDate(date: string) {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "2-digit",
    year: "numeric",
  }).format(new Date(date));
}

export default function Home() {
  const recentPosts = getRecentPublishedPosts(4);

  return (
    <section className="mx-auto flex w-full max-w-[600px] flex-col items-center px-1 pb-10 pt-6 text-center sm:pt-10">
      <div className="relative h-20 w-20 overflow-hidden rounded-full border-2 border-dashed border-white/[0.15] bg-[#111]">
        <Image alt="Andre Ochoa profile photo" className="object-cover grayscale" fill priority sizes="80px" src="/profile.jpg" />
      </div>

      <h1 className="mt-5 text-[32px] font-bold leading-none text-[#e8e8e8]" style={{ letterSpacing: "-0.5px" }}>
        andre ochoa
      </h1>

      <div className="mt-4">
        <TypingStatus />
      </div>

      <div className="mt-5 rounded-xl border border-dashed border-white/[0.12] bg-white/[0.02] px-4 py-3">
        <p className="text-[13px] uppercase text-white/80" style={{ letterSpacing: "6px" }}>
          BUILD · FUN · FREE
        </p>
      </div>

      <div className="mt-5 flex flex-wrap items-center justify-center gap-2">
        {socialLinks.map(({ href, icon: Icon, label }) => (
          <Link
            className="inline-flex items-center gap-2 rounded-full border border-dashed border-white/[0.12] bg-white/[0.03] px-3 py-2 text-[12px] text-white/72 transition hover:border-white/[0.18] hover:bg-white/[0.06]"
            href={href}
            key={href}
            rel="noreferrer"
            target="_blank"
          >
            <Icon className="h-3.5 w-3.5 text-white/55" />
            <span>{label}</span>
          </Link>
        ))}
      </div>

      <div className="mt-8 grid w-full gap-4 text-left sm:grid-cols-2">
        <section className="rounded-xl border border-dashed border-white/[0.12] bg-white/[0.03] p-4 backdrop-blur-[12px]">
          <div className="flex items-center justify-between gap-3">
            <p className="text-[12px] uppercase tracking-[0.24em] text-white/58">&gt; recent posts</p>
            <Link className="text-[11px] uppercase tracking-[0.18em] text-white/40 transition hover:text-white/72" href="/posts">
              all
            </Link>
          </div>

          <div className="mt-4 space-y-3">
            {recentPosts.length > 0 ? (
              recentPosts.map((post) => (
                <Link
                  className="block rounded-lg border border-dashed border-white/[0.08] bg-black/20 px-3 py-3 transition hover:border-white/[0.14] hover:bg-white/[0.04]"
                  href={`/posts/${post.slug}`}
                  key={post.slug}
                >
                  <p className="text-[11px] uppercase tracking-[0.18em] text-white/38">{formatDate(post.date)}</p>
                  <p className="mt-2 text-sm leading-6 text-[#e8e8e8]">{post.title}</p>
                </Link>
              ))
            ) : (
              <div className="rounded-lg border border-dashed border-white/[0.08] bg-black/20 px-3 py-3 text-sm leading-6 text-white/50">
                No published posts yet.
              </div>
            )}
          </div>
        </section>

        <section className="rounded-xl border border-dashed border-white/[0.12] bg-white/[0.03] p-4 backdrop-blur-[12px]">
          <p className="text-[12px] uppercase tracking-[0.24em] text-white/58">&gt; projects</p>

          <div className="mt-4 space-y-3">
            {projects.map((project) => (
              <Link
                className="flex items-center justify-between gap-3 rounded-lg border border-dashed border-white/[0.08] bg-black/20 px-3 py-3 transition hover:border-white/[0.14] hover:bg-white/[0.04]"
                href={project.href}
                key={project.slug}
              >
                <span className="text-sm leading-6 text-[#e8e8e8]">{project.name}</span>
                <span
                  className={`shrink-0 rounded-full border px-2.5 py-1 text-[11px] uppercase tracking-[0.18em] ${statusStyles[project.status]}`}
                >
                  {project.status}
                </span>
              </Link>
            ))}
          </div>
        </section>
      </div>

      <p className="mt-8 text-[12px] text-white/38">Keep building. -Ochoa</p>
    </section>
  );
}
