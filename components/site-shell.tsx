import Image from "next/image";
import Link from "next/link";
import { TerminalSquare } from "lucide-react";
import type { ReactNode } from "react";

const navItems = [
  { href: "/posts", label: "posts" },
  { href: "/vault", label: "vault" },
  { href: "/about", label: "about" },
];

export function SiteShell({
  children,
  eyebrow = "andochoa.com boot sequence",
}: {
  children: ReactNode;
  eyebrow?: string;
}) {
  return (
    <div className="relative min-h-screen overflow-hidden">
      <div className="mx-auto flex min-h-screen max-w-6xl flex-col px-4 py-6 sm:px-6 lg:px-8">
        <header className="animate-fade-up rounded-3xl border border-border/80 bg-card/85 p-4 shadow-terminal backdrop-blur">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <Link className="flex items-center gap-3" href="/">
              <div className="relative h-12 w-12 overflow-hidden rounded-2xl border border-primary/40 bg-black/40">
                <Image
                  alt="ANDOCHOA wordmark"
                  className="object-cover"
                  fill
                  priority
                  sizes="48px"
                  src="/logo.jpg"
                />
              </div>
              <div className="space-y-1">
                <p className="text-[10px] uppercase tracking-[0.45em] text-primary/75">
                  {eyebrow}
                </p>
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <TerminalSquare className="h-4 w-4 text-accent" />
                  <span>
                    founder notes, systems, and experiments
                    <span className="ml-1 inline-block h-4 w-2 animate-blink bg-primary align-middle" />
                  </span>
                </div>
              </div>
            </Link>

            <nav aria-label="Primary" className="flex flex-wrap gap-2 text-sm text-muted-foreground">
              {navItems.map((item) => (
                <Link
                  className="rounded-full border border-border/80 bg-background/70 px-4 py-2 transition hover:border-primary/60 hover:text-primary"
                  href={item.href}
                  key={item.href}
                >
                  <span className="mr-2 text-primary">&gt;</span>
                  [{item.label}]
                </Link>
              ))}
            </nav>
          </div>
        </header>

        <main className="flex-1 py-8">{children}</main>

        <footer className="border-t border-border/70 py-4 text-sm text-muted-foreground">
          <span className="text-primary">&gt;</span> Keep building. -Ochoa
        </footer>
      </div>
    </div>
  );
}
