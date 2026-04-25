import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { PostsWorkspace } from "@/components/posts-workspace";
import { getAllPosts, getPostBySlug } from "@/lib/posts";
import { siteConfig } from "@/lib/site";

type PostPageProps = {
  params: Promise<{ slug: string[] }>;
};

export async function generateMetadata({ params }: PostPageProps): Promise<Metadata> {
  const { slug } = await params;
  const resolvedSlug = slug.join("/");
  const post = getPostBySlug(resolvedSlug);

  if (!post) {
    return {
      title: "Post not found",
      description: siteConfig.description,
    };
  }

  const path = `/posts/${resolvedSlug}`;

  return {
    title: post.title,
    description: post.description,
    alternates: {
      canonical: path,
    },
    openGraph: {
      title: `${post.title} | ${siteConfig.name}`,
      description: post.description,
      url: path,
      siteName: siteConfig.name,
      images: [siteConfig.ogImagePath],
      type: "article",
      publishedTime: post.date,
    },
    twitter: {
      card: "summary_large_image",
      title: `${post.title} | ${siteConfig.name}`,
      description: post.description,
      images: [siteConfig.ogImagePath],
    },
  };
}

export default async function PostPage({ params }: PostPageProps) {
  const { slug } = await params;
  const resolvedSlug = slug.join("/");
  const post = getPostBySlug(resolvedSlug);

  if (!post) {
    notFound();
  }

  return <PostsWorkspace posts={getAllPosts()} selectedSlug={resolvedSlug} showMobileReader />;
}
