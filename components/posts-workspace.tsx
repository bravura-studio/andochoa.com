import type { Post } from "@/lib/posts";
import { PostReader } from "@/components/post-reader";
import { PostsNavigator } from "@/components/posts-navigator";

type PostsWorkspaceProps = {
  posts: Post[];
  selectedSlug?: string | null;
  showMobileReader?: boolean;
};

export function PostsWorkspace({
  posts,
  selectedSlug = null,
  showMobileReader = false,
}: PostsWorkspaceProps) {
  const fallbackPost = posts[0] ?? null;
  const selectedPost = posts.find((post) => post.slug === selectedSlug) ?? fallbackPost;

  return (
    <section className="space-y-4">
      <div className="rounded-[2rem] border border-dashed border-white/15 bg-white/[0.05] p-6 shadow-terminal backdrop-blur-xl sm:p-8">
        <p className="text-xs uppercase tracking-[0.35em] text-white/42">posts workspace</p>
        <h1 className="mt-4 text-3xl font-semibold sm:text-4xl">Founder writing, arranged like an editor.</h1>
        <p className="mt-4 max-w-3xl leading-7 text-white/60">
          Browse the archive in the navigator, keep one post open in the reader, and use direct URLs when you want to
          point to a specific essay.
        </p>
      </div>

      <div className="grid gap-4 lg:grid-cols-[340px_minmax(0,1fr)]">
        <div className={showMobileReader ? "hidden lg:block" : undefined}>
          <PostsNavigator posts={posts} selectedSlug={selectedPost?.slug ?? null} />
        </div>

        <div className={showMobileReader ? undefined : "hidden lg:block"}>
          {selectedPost ? (
            <PostReader post={selectedPost} />
          ) : (
            <section className="rounded-[2rem] border border-dashed border-white/15 bg-white/[0.045] p-8 shadow-terminal backdrop-blur-xl">
              <p className="text-sm text-white/56">No post selected yet.</p>
            </section>
          )}
        </div>

        {showMobileReader && selectedPost ? (
          <div className="lg:hidden">
            <PostReader post={selectedPost} showMobileBackLink />
          </div>
        ) : null}
      </div>
    </section>
  );
}
