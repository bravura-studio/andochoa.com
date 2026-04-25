import Link from "next/link";

export default function PostsPage() {
  return (
    <section className="rounded-[2rem] border border-border/80 bg-card/80 p-6 shadow-terminal sm:p-8">
      <p className="text-xs uppercase tracking-[0.35em] text-primary">posts index</p>
      <h1 className="mt-4 text-3xl font-semibold">Published and in-progress essays</h1>
      <p className="mt-4 max-w-2xl leading-7 text-muted-foreground">
        This route is scaffolded and ready for MDX-backed content. The repository already contains a content pipeline in
        `content/`, and the next step is wiring published entries into this view.
      </p>
      <Link className="mt-8 inline-block text-sm text-accent hover:text-primary" href="/">
        &gt; return home
      </Link>
    </section>
  );
}
