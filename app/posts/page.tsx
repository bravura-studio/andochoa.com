import Link from "next/link";
import { getAllPosts } from "@/lib/posts";

function formatDate(date: string) {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "2-digit",
    year: "numeric",
  }).format(new Date(date));
}

export default function PostsPage() {
  const posts = getAllPosts();
  const published = posts.filter((post) => post.status === "published");
  const drafts = posts.filter((post) => post.status === "draft");

  return (
    <section className="rounded-[2rem] border border-dashed border-white/15 bg-white/[0.05] p-6 shadow-terminal backdrop-blur-xl sm:p-8">
      <p className="text-xs uppercase tracking-[0.35em] text-white/42">posts index</p>
      <h1 className="mt-4 text-3xl font-semibold">Published and in-progress essays</h1>
      <p className="mt-4 max-w-2xl leading-7 text-white/60">
        The site reads directly from local markdown. Published entries surface first, with drafts visible as in-flight
        work inside the same system.
      </p>

      <div className="mt-10 space-y-8">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-white/42">&gt; published</p>
          {published.length > 0 ? (
            <div className="mt-4 space-y-3">
              {published.map((post) => (
                <article
                  className="rounded-[1.4rem] border border-dashed border-white/12 bg-black/30 px-4 py-4"
                  key={post.slug}
                >
                  <p className="text-xs uppercase tracking-[0.24em] text-white/38">{formatDate(post.date)}</p>
                  <h2 className="mt-2 text-lg font-medium">{post.title}</h2>
                  <p className="mt-2 text-sm leading-6 text-white/56">{post.excerpt}</p>
                </article>
              ))}
            </div>
          ) : (
            <div className="mt-4 rounded-[1.4rem] border border-dashed border-white/12 bg-black/30 px-4 py-4 text-sm leading-7 text-white/56">
              No published posts yet.
            </div>
          )}
        </div>

        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-white/42">&gt; drafts</p>
          <div className="mt-4 space-y-3">
            {drafts.map((post) => (
              <article
                className="rounded-[1.4rem] border border-dashed border-white/12 bg-black/30 px-4 py-4"
                key={post.slug}
              >
                <div className="flex items-center justify-between gap-3">
                  <p className="text-xs uppercase tracking-[0.24em] text-white/38">{formatDate(post.date)}</p>
                  <span className="rounded-full border border-dashed border-white/14 px-3 py-1 text-[11px] uppercase tracking-[0.22em] text-white/48">
                    draft
                  </span>
                </div>
                <h2 className="mt-2 text-lg font-medium">{post.title}</h2>
                <p className="mt-2 text-sm leading-6 text-white/56">{post.excerpt}</p>
              </article>
            ))}
          </div>
        </div>
      </div>

      <Link className="mt-8 inline-block text-sm text-white/72 transition hover:text-white" href="/">
        &gt; return home
      </Link>
    </section>
  );
}
