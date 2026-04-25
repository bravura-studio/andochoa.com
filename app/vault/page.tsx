import Link from "next/link";
import { SiteShell } from "@/components/site-shell";

export default function VaultPage() {
  return (
    <SiteShell eyebrow="directory /vault">
      <section className="rounded-[2rem] border border-border/80 bg-card/80 p-6 shadow-terminal sm:p-8">
        <p className="text-xs uppercase tracking-[0.35em] text-primary">vault index</p>
        <h1 className="mt-4 text-3xl font-semibold">Internal systems and source material</h1>
        <p className="mt-4 max-w-2xl leading-7 text-muted-foreground">
          Reserved for process notes, prompts, and system documentation that support the public writing loop.
        </p>
        <Link className="mt-8 inline-block text-sm text-accent hover:text-primary" href="/">
          &gt; return home
        </Link>
      </section>
    </SiteShell>
  );
}
