import Image from "next/image";
import Link from "next/link";
import { ArrowRight, FolderKanban, NotebookPen, Orbit } from "lucide-react";
import { SiteShell } from "@/components/site-shell";

const cards = [
  {
    href: "/posts",
    icon: NotebookPen,
    label: "posts",
    title: "Long-form writing in progress",
    body: "Essays and published notes shaped from the Scripta pipeline.",
  },
  {
    href: "/vault",
    icon: FolderKanban,
    label: "vault",
    title: "Systems, prompts, and source material",
    body: "A map of the operating system behind BUILD.FUN.FREE.",
  },
  {
    href: "/about",
    icon: Orbit,
    label: "about",
    title: "Founder context",
    body: "What this site is for, why it exists, and how the experiments connect.",
  },
];

export default function Home() {
  return (
    <SiteShell eyebrow="terminal theme initialized">
      <section className="grid gap-6 lg:grid-cols-[1.35fr_0.9fr]">
        <div className="animate-fade-up rounded-[2rem] border border-border/80 bg-card/80 p-6 shadow-terminal backdrop-blur [animation-delay:0.08s] sm:p-8">
          <p className="text-xs uppercase tracking-[0.4em] text-accent">andochoa@build.fun.free</p>
          <h1 className="mt-4 max-w-3xl text-4xl font-semibold leading-tight sm:text-5xl">
            Building a founder operating system in public.
          </h1>
          <p className="mt-6 max-w-2xl text-base leading-7 text-muted-foreground sm:text-lg">
            Scripta is the front-end for essays, field notes, and experiments from the BUILD.FUN.FREE portfolio.
            The interface is intentionally terminal-like: direct, dark, and built for shipping.
          </p>

          <div className="mt-8 flex flex-wrap gap-3">
            <Link
              className="rounded-full border border-primary/50 bg-primary px-5 py-3 text-sm font-medium text-primary-foreground transition hover:brightness-110"
              href="/posts"
            >
              Enter posts
            </Link>
            <Link
              className="rounded-full border border-border/80 bg-background/70 px-5 py-3 text-sm font-medium text-foreground transition hover:border-accent hover:text-accent"
              href="/about"
            >
              Read mission
            </Link>
          </div>
        </div>

        <div className="animate-fade-up rounded-[2rem] border border-border/80 bg-black/40 p-6 [animation-delay:0.16s]">
          <div className="rounded-[1.5rem] border border-border/80 bg-card/60 p-3">
            <div className="relative aspect-square overflow-hidden rounded-[1.25rem] border border-dashed border-accent/45 bg-background/60">
              <Image
                alt="Founder profile placeholder"
                className="object-cover opacity-85"
                fill
                priority
                sizes="(min-width: 1024px) 28rem, 100vw"
                src="/logo.jpg"
              />
              <div className="absolute inset-x-4 bottom-4 rounded-2xl border border-border/80 bg-background/80 px-4 py-3 text-sm text-muted-foreground backdrop-blur">
                `public/profile.jpg` is still missing in the repo, so the shell is falling back to `logo.jpg` for now.
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="mt-8 grid gap-4 md:grid-cols-3">
        {cards.map(({ href, icon: Icon, label, title, body }, index) => (
          <Link
            className="animate-fade-up rounded-[1.75rem] border border-border/80 bg-card/70 p-5 transition hover:-translate-y-1 hover:border-primary/60 hover:shadow-terminal"
            href={href}
            key={href}
            style={{ animationDelay: `${0.2 + index * 0.08}s` }}
          >
            <div className="flex items-center justify-between text-sm text-muted-foreground">
              <span>[{label}]</span>
              <Icon className="h-4 w-4 text-primary" />
            </div>
            <h2 className="mt-8 text-xl font-medium">{title}</h2>
            <p className="mt-3 text-sm leading-6 text-muted-foreground">{body}</p>
            <span className="mt-6 inline-flex items-center gap-2 text-sm text-accent">
              open directory <ArrowRight className="h-4 w-4" />
            </span>
          </Link>
        ))}
      </section>
    </SiteShell>
  );
}
