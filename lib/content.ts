import { readFile, readdir } from "node:fs/promises";
import path from "node:path";
import { compileMDX } from "next-mdx-remote/rsc";
import matter from "gray-matter";

const PUBLISHED_CONTENT_DIR = path.join(process.cwd(), "content", "published");
const VALID_POST_TYPES = ["struggle", "win", "observation", "brainstorm", "reflection"] as const;
const VALID_POST_STATUSES = ["draft", "published", "archived"] as const;
const MARKDOWN_EXTENSIONS = new Set([".md", ".mdx"]);

export type PostType = (typeof VALID_POST_TYPES)[number];
export type PostStatus = (typeof VALID_POST_STATUSES)[number];

export type PostFrontmatter = {
  title: string;
  date: string;
  type: PostType;
  description: string;
  status: PostStatus;
  word_count: number;
};

export type PostSummary = PostFrontmatter & {
  slug: string;
  pathname: string;
};

export type Post = PostSummary & {
  content: React.ReactNode;
  rawContent: string;
};

function isPostType(value: unknown): value is PostType {
  return typeof value === "string" && VALID_POST_TYPES.includes(value as PostType);
}

function isPostStatus(value: unknown): value is PostStatus {
  return typeof value === "string" && VALID_POST_STATUSES.includes(value as PostStatus);
}

function toSlug(filePath: string) {
  return path.basename(filePath, path.extname(filePath)).replace(/^\d{4}-\d{2}-\d{2}-/, "");
}

function validateFrontmatter(data: Record<string, unknown>, filePath: string): PostFrontmatter {
  if (typeof data.title !== "string" || !data.title.trim()) {
    throw new Error(`Missing valid title in ${filePath}`);
  }

  if (typeof data.date !== "string" || Number.isNaN(Date.parse(data.date))) {
    throw new Error(`Missing valid date in ${filePath}`);
  }

  if (!isPostType(data.type)) {
    throw new Error(`Invalid post type in ${filePath}`);
  }

  if (typeof data.description !== "string" || !data.description.trim()) {
    throw new Error(`Missing valid description in ${filePath}`);
  }

  if (!isPostStatus(data.status)) {
    throw new Error(`Invalid post status in ${filePath}`);
  }

  if (typeof data.word_count !== "number") {
    throw new Error(`Missing valid word_count in ${filePath}`);
  }

  return {
    title: data.title,
    date: data.date,
    type: data.type,
    description: data.description,
    status: data.status,
    word_count: data.word_count,
  };
}

async function collectMarkdownFiles(directory: string): Promise<string[]> {
  const entries = await readdir(directory, { withFileTypes: true });
  const files = await Promise.all(
    entries.map(async (entry) => {
      const entryPath = path.join(directory, entry.name);

      if (entry.isDirectory()) {
        return collectMarkdownFiles(entryPath);
      }

      if (!entry.isFile()) {
        return [];
      }

      const extension = path.extname(entry.name);
      if (!MARKDOWN_EXTENSIONS.has(extension) || entry.name === "README.md") {
        return [];
      }

      return [entryPath];
    }),
  );

  return files.flat();
}

async function readPostSummary(filePath: string): Promise<PostSummary> {
  const source = await readFile(filePath, "utf8");
  const { data } = matter(source);
  const frontmatter = validateFrontmatter(data, filePath);
  const slug = toSlug(filePath);

  return {
    ...frontmatter,
    slug,
    pathname: `/posts/${slug}`,
  };
}

export async function getAllPosts() {
  const files = await collectMarkdownFiles(PUBLISHED_CONTENT_DIR);
  const posts = await Promise.all(files.map(readPostSummary));

  return posts.sort((left, right) => Date.parse(right.date) - Date.parse(left.date));
}

export async function getPostBySlug(slug: string): Promise<Post | null> {
  const files = await collectMarkdownFiles(PUBLISHED_CONTENT_DIR);
  const filePath = files.find((candidate) => toSlug(candidate) === slug);

  if (!filePath) {
    return null;
  }

  const source = await readFile(filePath, "utf8");
  const { content: rawContent, data } = matter(source);
  const frontmatter = validateFrontmatter(data, filePath);
  const { content } = await compileMDX<PostFrontmatter>({
    source: rawContent,
    options: {
      parseFrontmatter: false,
    },
  });

  return {
    ...frontmatter,
    slug,
    pathname: `/posts/${slug}`,
    content,
    rawContent,
  };
}
