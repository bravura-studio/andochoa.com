import { notFound } from "next/navigation";
import { PostsWorkspace } from "@/components/posts-workspace";
import { getAllPosts, getPostBySlug } from "@/lib/posts";

type PostPageProps = {
  params: Promise<{ slug: string[] }>;
};

export default async function PostPage({ params }: PostPageProps) {
  const { slug } = await params;
  const resolvedSlug = slug.join("/");
  const post = getPostBySlug(resolvedSlug);

  if (!post) {
    notFound();
  }

  return <PostsWorkspace posts={getAllPosts()} selectedSlug={resolvedSlug} showMobileReader />;
}
