import Image from "next/image";
import Link from "next/link";
import { ArrowRight, ArrowUpRight, Github, Linkedin, Twitter } from "lucide-react";
import { TypingStatus } from "@/components/typing-status";
import { projects } from "@/config/projects";
import { getRecentPublishedPosts } from "@/lib/posts";

const socialLinks = [
  { href: "https://x.com/andochoa", icon: Twitter, label: "x /andochoa" },
  { href: "https://linkedin.com/in/andreochoa", icon: Linkedin, label: "linkedin /andreochoa" },
  { href: "https://github.com/AndOchoa", icon: Github, label: "github /AndOchoa" },
];

const statusLabel = {
  live: "live",
  building: "building",
  testing: "testing",
} as const;

function formatDate(date: string) {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "2-digit",
    year: "numeric",
  }).format(new Date(date));
}

export default function Home() {
  const recentPosts = getRecentPublishedPosts(3);

  return (
    <>
      <section className="grid gap-6 lg:grid-cols-[1.15fr_0.85fr]">
        <div className="animate-fade-up rounded-[2rem] border border-dashed border-white/15 bg-white/[0.05] p-6 shadow-terminal backdrop-blur-xl [animation-delay:0.08s] sm:p-8">
          <p className="text-xs uppercase tracking-[0.4em] text-white/42">andochoa.com / founder terminal</p>
          <div className="mt-8 flex flex-col gap-6 sm:flex-row sm:items-center">
            <div className="relative h-28 w-28 overflow-hidden rounded-full border border-dashed border-white/18 bg-black/50 sm:h-32 sm:w-32">
              <Image
                alt="Founder profile"
                className="object-cover grayscale contrast-110"
                fill
                priority
                sizes="128px"
                src="/profile.jpg"
              />
            </div>
            <div className="min-w-0">
              <h1 className="text-4xl font-semibold tracking-[-0.04em] sm:text-6xl">andre ochoa</h1>
              <div className="mt-4">
                <TypingStatus />
              </div>
              <p className="mt-5 max-w-2xl text-sm leading-7 text-white/58 sm:text-base">
                Building products in public, documenting the operating system behind them, and turning live work into
                essays, prompts, and experiments.
              </p>
            </div>
          </div>

          <div className="mt-8 rounded-[1.75rem] border border-dashed border-white/16 bg-black/35 px-5 py-5 backdrop-blur-xl">
            <p className="text-[11px] uppercase tracking-[0.4em] text-white/38">north star</p>
            <div className="mt-4 flex flex-wrap gap-3 text-2xl font-semibold tracking-[-0.06em] sm:text-4xl">
              <span className="rounded-full border border-dashed border-white/14 bg-white/[0.04] px-4 py-2">BUILD.</span>
              <span className="rounded-full border border-dashed border-white/14 bg-white/[0.04] px-4 py-2">FUN.</span>
              <span className="rounded-full border border-dashed border-white/14 bg-white/[0.04] px-4 py-2">FREE.</span>
            </div>
          </div>

          <div className="mt-8 flex flex-wrap gap-3">
            {socialLinks.map(({ href, icon: Icon, label }) => (
              <Link
                className="inline-flex items-center gap-2 rounded-full border border-dashed border-white/16 bg-white/[0.04] px-4 py-3 text-sm text-white/78 transition hover:border-white/24 hover:bg-white/[0.08]"
                href={href}
                key={href}
                rel="noreferrer"
                target="_blank"
              >
                <Icon className="h-4 w-4 text-white/56" />
                <span>{label}</span>
              </Link>
            ))}
          </div>
        </div>

        <div className="animate-fade-up rounded-[2rem] border border-dashed border-white/15 bg-white/[0.04] p-6 backdrop-blur-xl [animation-delay:0.16s]">
          <div className="rounded-[1.5rem] border border-dashed border-white/12 bg-black/35 p-5">
            <p className="text-[11px] uppercase tracking-[0.38em] text-white/38">workspace note</p>
            <h2 className="mt-4 text-2xl font-semibold tracking-[-0.04em]">A sparse hub for shipping the thinking.</h2>
            <p className="mt-4 text-sm leading-7 text-white/58">
              No neon hacker posture. Just a clean desktop shell for founder notes, portfolio context, and current
              writing momentum.
            </p>

            <div className="mt-8 grid gap-3 sm:grid-cols-2">
              <Link
                className="rounded-[1.4rem] border border-dashed border-white/16 bg-white px-4 py-4 text-sm font-medium text-black transition hover:bg-white/90"
                href="/posts"
              >
                enter posts
              </Link>
              <Link
                className="rounded-[1.4rem] border border-dashed border-white/16 bg-white/[0.04] px-4 py-4 text-sm font-medium text-white/82 transition hover:border-white/24 hover:bg-white/[0.08]"
                href="/about"
              >
                read mission
              </Link>
            </div>

            <div className="mt-8 rounded-[1.4rem] border border-dashed border-white/12 bg-white/[0.03] p-4 text-sm text-white/56">
              Founder profile loaded from `public/profile.jpg`. Content system wired to local markdown under
              `content/`.
            </div>
          </div>
        </div>
      </section>

      <section className="mt-8 grid gap-6 lg:grid-cols-[0.95fr_1.05fr]">
        <div className="animate-fade-up rounded-[1.9rem] border border-dashed border-white/14 bg-white/[0.045] p-6 shadow-terminal [animation-delay:0.22s]">
          <div className="flex items-center justify-between gap-3">
            <p className="text-xs uppercase tracking-[0.36em] text-white/42">&gt; recent posts</p>
            <Link className="inline-flex items-center gap-2 text-sm text-white/72 transition hover:text-white" href="/posts">
              [all posts <ArrowRight className="h-4 w-4" />]
            </Link>
          </div>

          {recentPosts.length > 0 ? (
            <div className="mt-6 space-y-3">
              {recentPosts.map((post) => (
                <article
                  className="rounded-[1.35rem] border border-dashed border-white/12 bg-black/30 px-4 py-4"
                  key={post.slug}
                >
                  <p className="text-xs uppercase tracking-[0.24em] text-white/38">{formatDate(post.date)}</p>
                  <h2 className="mt-3 text-lg font-medium text-white">{post.title}</h2>
                  <p className="mt-2 text-sm leading-6 text-white/56">{post.excerpt}</p>
                </article>
              ))}
            </div>
          ) : (
            <div className="mt-6 rounded-[1.35rem] border border-dashed border-white/12 bg-black/30 px-4 py-5 text-sm leading-7 text-white/56">
              No published posts yet. The writing pipeline is live, and drafts are accumulating before the first public
              releases.
            </div>
          )}
        </div>

        <div className="animate-fade-up rounded-[1.9rem] border border-dashed border-white/14 bg-white/[0.045] p-6 shadow-terminal [animation-delay:0.28s]">
          <p className="text-xs uppercase tracking-[0.36em] text-white/42">&gt; projects</p>
          <div className="mt-6 grid gap-3 md:grid-cols-2">
            {projects.map((project) => (
              <Link
                className="rounded-[1.4rem] border border-dashed border-white/12 bg-black/30 p-4 transition hover:-translate-y-1 hover:border-white/22 hover:bg-white/[0.06]"
                href={project.href}
                key={project.slug}
              >
                <div className="flex items-center justify-between gap-3">
                  <div className="flex h-11 w-11 items-center justify-center rounded-2xl border border-dashed border-white/14 bg-white/[0.04] text-sm text-white/84">
                    {project.mark}
                  </div>
                  <span className="rounded-full border border-dashed border-white/14 px-3 py-1 text-[11px] uppercase tracking-[0.24em] text-white/48">
                    {statusLabel[project.status]}
                  </span>
                </div>
                <h2 className="mt-6 text-xl font-medium text-white">{project.name}</h2>
                <p className="mt-3 text-sm leading-6 text-white/56">{project.description}</p>
                <span className="mt-5 inline-flex items-center gap-2 text-sm text-white/78">
                  open <ArrowUpRight className="h-4 w-4" />
                </span>
              </Link>
            ))}
          </div>
        </div>
      </section>
    </>
  );
}
