import { notFound } from "next/navigation";
import { getPostBySlug } from "@/lib/content";

type PostPageProps = {
  params: Promise<{
    slug: string;
  }>;
};

export default async function PostPage({ params }: PostPageProps) {
  const { slug } = await params;
  const post = await getPostBySlug(slug);

  if (!post) {
    notFound();
  }

  return (
    <article className="prose prose-invert max-w-none rounded-[2rem] border border-border/80 bg-card/80 p-6 shadow-terminal sm:p-8">
      <div className="not-prose flex flex-wrap gap-3 text-xs uppercase tracking-[0.24em] text-muted-foreground">
        <span>{post.date}</span>
        <span>{post.type}</span>
        <span>{post.status}</span>
        <span>{post.word_count} words</span>
      </div>
      <h1 className="not-prose mt-4 text-4xl font-semibold">{post.title}</h1>
      <p className="not-prose mt-4 max-w-2xl text-base leading-7 text-muted-foreground">{post.description}</p>
      <div className="mt-10">{post.content}</div>
    </article>
  );
}
