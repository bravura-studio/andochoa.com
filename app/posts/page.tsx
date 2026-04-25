import { PostsWorkspace } from "@/components/posts-workspace";
import { getAllPosts } from "@/lib/posts";
import { buildPageMetadata } from "@/lib/site";

export const metadata = buildPageMetadata({
  title: "Posts",
  description: "Published essays and drafts from Andre Ochoa's founder writing workspace.",
  path: "/posts",
});

export default function PostsPage() {
  const posts = getAllPosts();

  return <PostsWorkspace posts={posts} selectedSlug={posts[0]?.slug ?? null} />;
}
