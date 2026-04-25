import type { Metadata } from "next";
import { buildPostWorkspaceMetadata, renderPostWorkspacePage } from "@/app/posts/post-workspace-page";

type PostPageProps = {
  params: Promise<{
    slug: string;
  }>;
};

export async function generateMetadata({ params }: PostPageProps): Promise<Metadata> {
  const { slug } = await params;

  return buildPostWorkspaceMetadata(slug);
}

export default async function PostPage({ params }: PostPageProps) {
  const { slug } = await params;

  return renderPostWorkspacePage(slug);
}
