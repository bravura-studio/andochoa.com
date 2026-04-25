import Link from "next/link";

export default function VaultPage() {
  return (
    <section className="rounded-[2rem] border border-dashed border-white/15 bg-white/[0.05] p-6 shadow-terminal backdrop-blur-xl sm:p-8">
      <p className="text-xs uppercase tracking-[0.35em] text-white/42">vault index</p>
      <h1 className="mt-4 text-3xl font-semibold">Internal systems and source material</h1>
      <p className="mt-4 max-w-2xl leading-7 text-white/60">
        Reserved for process notes, prompts, and system documentation that support the public writing loop.
      </p>
      <Link className="mt-8 inline-block text-sm text-white/72 transition hover:text-white" href="/">
        &gt; return home
      </Link>
    </section>
  );
}
