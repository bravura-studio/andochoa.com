import Link from "next/link";

export default function AboutPage() {
  return (
    <section className="rounded-[2rem] border border-border/80 bg-card/80 p-6 shadow-terminal sm:p-8">
      <p className="text-xs uppercase tracking-[0.35em] text-primary">about the founder</p>
      <h1 className="mt-4 text-3xl font-semibold">A site for shipping the thinking behind BUILD.FUN.FREE</h1>
      <p className="mt-4 max-w-2xl leading-7 text-muted-foreground">
        The goal of andochoa.com is to make the strategy, experiments, and lessons legible while products are still
        being built. This page is a stub for the founder narrative and can expand as the broader content system comes
        online.
      </p>
      <Link className="mt-8 inline-block text-sm text-accent hover:text-primary" href="/">
        &gt; return home
      </Link>
    </section>
  );
}
