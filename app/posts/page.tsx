import Link from "next/link";
import { getAllPosts } from "@/lib/content";

export default async function PostsPage() {
  const posts = await getAllPosts();

  return (
    <section className="rounded-[2rem] border border-border/80 bg-card/80 p-6 shadow-terminal sm:p-8">
      <p className="text-xs uppercase tracking-[0.35em] text-primary">posts index</p>
      <h1 className="mt-4 text-3xl font-semibold">Published essays and field notes</h1>
      <p className="mt-4 max-w-2xl leading-7 text-muted-foreground">
        MDX posts are now loaded from `content/published/` and sorted by publish date.
      </p>

      <div className="mt-8 space-y-4">
        {posts.map((post) => (
          <article className="rounded-[1.5rem] border border-border/70 bg-background/60 p-5" key={post.slug}>
            <div className="flex flex-wrap items-center gap-3 text-xs uppercase tracking-[0.24em] text-muted-foreground">
              <span>{post.date}</span>
              <span>{post.type}</span>
              <span>{post.word_count} words</span>
            </div>
            <h2 className="mt-4 text-2xl font-semibold">
              <Link className="transition hover:text-primary" href={post.pathname}>
                {post.title}
              </Link>
            </h2>
            <p className="mt-3 max-w-2xl leading-7 text-muted-foreground">{post.description}</p>
          </article>
        ))}
      </div>

      <Link className="mt-8 inline-block text-sm text-accent hover:text-primary" href="/">
        &gt; return home
      </Link>
    </section>
  );
}
