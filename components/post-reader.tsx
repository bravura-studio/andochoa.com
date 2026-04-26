import Image from "next/image";
import Link from "next/link";
import type { HTMLAttributes, LiHTMLAttributes, ReactNode } from "react";
import { PostReaderProgress } from "@/components/post-reader-progress";
import { formatIsoDate } from "@/lib/date";
import { getPostTypeBadgeClassName } from "@/lib/post-type-styles";
import type { Post } from "@/lib/posts";

function renderInlineMarkdown(text: string) {
  const segments = text.split(/(\[[^\]]+\]\([^)]+\)|\*\*[^*]+\*\*|`[^`]+`|\*[^*]+\*)/g).filter(Boolean);

  return segments.map((segment, index) => {
    if (/^\[[^\]]+\]\([^)]+\)$/.test(segment)) {
      const match = segment.match(/^\[([^\]]+)\]\(([^)]+)\)$/);

      if (match) {
        const [, label, href] = match;

        return (
          <a
            className="text-white underline decoration-white/30 underline-offset-4 transition hover:decoration-white/65"
            href={href}
            key={`${segment}-${index}`}
            rel={href.startsWith("http") ? "noreferrer" : undefined}
            target={href.startsWith("http") ? "_blank" : undefined}
          >
            {label}
          </a>
        );
      }
    }

    if (/^\*\*[^*]+\*\*$/.test(segment)) {
      return (
        <strong className="font-semibold text-white" key={`${segment}-${index}`}>
          {segment.slice(2, -2)}
        </strong>
      );
    }

    if (/^\*[^*]+\*$/.test(segment)) {
      return (
        <em className="italic text-white/82" key={`${segment}-${index}`}>
          {segment.slice(1, -1)}
        </em>
      );
    }

    if (/^`[^`]+`$/.test(segment)) {
      return (
        <code className="rounded bg-white/[0.08] px-1.5 py-1 text-[0.92em] text-white" key={`${segment}-${index}`}>
          {segment.slice(1, -1)}
        </code>
      );
    }

    return segment;
  });
}

function Paragraph({ children, ...props }: HTMLAttributes<HTMLParagraphElement>) {
  return (
    <p className="mt-5 text-[14px] leading-[1.8] text-white/75 first:mt-0" {...props}>
      {children}
    </p>
  );
}

function HeadingOne({ children, ...props }: HTMLAttributes<HTMLHeadingElement>) {
  return (
    <h1 className="mt-10 text-[28px] font-bold leading-tight text-white first:mt-0" {...props}>
      {children}
    </h1>
  );
}

function HeadingTwo({ children, ...props }: HTMLAttributes<HTMLHeadingElement>) {
  return (
    <h2 className="mt-10 text-2xl font-semibold leading-tight text-white" {...props}>
      {children}
    </h2>
  );
}

function HeadingThree({ children, ...props }: HTMLAttributes<HTMLHeadingElement>) {
  return (
    <h3 className="mt-8 text-xl font-semibold leading-tight text-white" {...props}>
      {children}
    </h3>
  );
}

function ListItem({ children, ...props }: LiHTMLAttributes<HTMLLIElement>) {
  return (
    <li className="pl-1 text-[14px] leading-[1.8] text-white/75" {...props}>
      {children}
    </li>
  );
}

function renderMarkdown(content: string) {
  const lines = content.replace(/\r\n/g, "\n").split("\n");
  const blocks: ReactNode[] = [];
  let index = 0;

  while (index < lines.length) {
    const currentLine = lines[index];
    const trimmedLine = currentLine.trim();

    if (!trimmedLine) {
      index += 1;
      continue;
    }

    if (trimmedLine === "---") {
      blocks.push(<hr className="mt-8 border-t border-dashed border-white/12" key={`hr-${blocks.length}`} />);
      index += 1;
      continue;
    }

    if (trimmedLine.startsWith("```")) {
      const language = trimmedLine.slice(3).trim();
      const codeLines: string[] = [];
      index += 1;

      while (index < lines.length && !lines[index].trim().startsWith("```")) {
        codeLines.push(lines[index]);
        index += 1;
      }

      index += 1;
      blocks.push(
        <pre
          className="mt-6 overflow-x-auto rounded-2xl border border-dashed border-white/14 bg-black/70 px-4 py-4 text-sm leading-7 text-white/82"
          key={`code-${blocks.length}`}
        >
          {language ? <div className="mb-3 text-[11px] uppercase tracking-[0.24em] text-white/38">{language}</div> : null}
          <code>{codeLines.join("\n")}</code>
        </pre>,
      );
      continue;
    }

    if (trimmedLine.startsWith("### ")) {
      blocks.push(<HeadingThree key={`h3-${blocks.length}`}>{renderInlineMarkdown(trimmedLine.slice(4))}</HeadingThree>);
      index += 1;
      continue;
    }

    if (trimmedLine.startsWith("## ")) {
      blocks.push(<HeadingTwo key={`h2-${blocks.length}`}>{renderInlineMarkdown(trimmedLine.slice(3))}</HeadingTwo>);
      index += 1;
      continue;
    }

    if (trimmedLine.startsWith("# ")) {
      blocks.push(<HeadingOne key={`h1-${blocks.length}`}>{renderInlineMarkdown(trimmedLine.slice(2))}</HeadingOne>);
      index += 1;
      continue;
    }

    if (trimmedLine.startsWith(">")) {
      const quoteLines: string[] = [];

      while (index < lines.length && lines[index].trim().startsWith(">")) {
        quoteLines.push(lines[index].trim().replace(/^>\s?/, ""));
        index += 1;
      }

      blocks.push(
        <blockquote
          className="mt-6 border-l border-dashed border-white/20 pl-4 text-[14px] leading-[1.8] text-white/60"
          key={`quote-${blocks.length}`}
        >
          {quoteLines.map((line, quoteIndex) => (
            <p key={`quote-line-${quoteIndex}`}>{renderInlineMarkdown(line)}</p>
          ))}
        </blockquote>,
      );
      continue;
    }

    if (/^\d+\.\s/.test(trimmedLine)) {
      const listItems: string[] = [];

      while (index < lines.length && /^\d+\.\s/.test(lines[index].trim())) {
        listItems.push(lines[index].trim().replace(/^\d+\.\s/, ""));
        index += 1;
      }

      blocks.push(
        <ol className="mt-5 list-decimal space-y-3 pl-6" key={`ol-${blocks.length}`}>
          {listItems.map((item, listIndex) => (
            <ListItem key={`ol-item-${listIndex}`}>{renderInlineMarkdown(item)}</ListItem>
          ))}
        </ol>,
      );
      continue;
    }

    if (/^[-*]\s/.test(trimmedLine)) {
      const listItems: string[] = [];

      while (index < lines.length && /^[-*]\s/.test(lines[index].trim())) {
        listItems.push(lines[index].trim().replace(/^[-*]\s/, ""));
        index += 1;
      }

      blocks.push(
        <ul className="mt-5 list-disc space-y-3 pl-6" key={`ul-${blocks.length}`}>
          {listItems.map((item, listIndex) => (
            <ListItem key={`ul-item-${listIndex}`}>{renderInlineMarkdown(item)}</ListItem>
          ))}
        </ul>,
      );
      continue;
    }

    const paragraphLines: string[] = [];

    while (index < lines.length && lines[index].trim()) {
      const paragraphLine = lines[index].trim();

      if (
        paragraphLine === "---" ||
        paragraphLine.startsWith("#") ||
        paragraphLine.startsWith(">") ||
        paragraphLine.startsWith("```") ||
        /^\d+\.\s/.test(paragraphLine) ||
        /^[-*]\s/.test(paragraphLine)
      ) {
        break;
      }

      paragraphLines.push(paragraphLine);
      index += 1;
    }

    blocks.push(
      <Paragraph key={`p-${blocks.length}`}>{renderInlineMarkdown(paragraphLines.join(" "))}</Paragraph>,
    );
  }

  return blocks;
}

type PostReaderProps = {
  post: Post;
  previousPost: Post | null;
  nextPost: Post | null;
};

function stripPostSignoff(content: string) {
  return content.replace(/\n+Keep building\. -Ochoa\s*$/u, "");
}

export function PostReader({ post, previousPost, nextPost }: PostReaderProps) {
  return (
    <div className="mx-auto max-w-[65ch]" data-post-reader-container>
      <PostReaderProgress postSlug={post.slug} />

      <article data-post-reader-article>
        <header className="border-b border-dashed border-white/10 pb-6">
          <div className="flex items-center gap-3">
            <div className="relative h-10 w-10 overflow-hidden rounded-full border border-dashed border-white/14 bg-black/45">
              <Image alt="Andre Ochoa" className="object-cover" fill sizes="40px" src="/profile.jpg" />
            </div>
            <div>
              <p className="text-[12px] text-white">Andre Ochoa</p>
              <p className="mt-1 text-[10px] uppercase tracking-[0.22em] text-white/32">{formatIsoDate(post.date)}</p>
            </div>
          </div>

          <h1 className="mt-6 max-w-4xl text-[28px] font-semibold leading-tight tracking-[-0.04em] text-white sm:text-[34px]">
            {post.title}
          </h1>
          <p className="mt-3 max-w-[60ch] text-[13px] leading-7 text-white/46">{post.description}</p>

          <div className="mt-4 flex flex-wrap items-center gap-2 text-[10px] uppercase tracking-[0.2em] text-white/34">
            <span className={getPostTypeBadgeClassName(post.type)}>{post.type}</span>
          </div>
        </header>

        <div className="pt-8">{renderMarkdown(stripPostSignoff(post.content))}</div>

        <footer className="mt-10 border-t border-dashed border-white/10 pt-6">
          <p className="text-[12px] uppercase tracking-[0.2em] text-white/68">Keep building. -Ochoa</p>

          {(previousPost ?? nextPost) ? (
            <div className="mt-6 flex items-stretch justify-between gap-3 border-t border-dashed border-white/8 pt-5">
              {previousPost ? (
                <Link
                  className="group flex min-w-0 flex-1 flex-col gap-1 rounded-md border border-white/8 px-4 py-3 transition hover:border-white/18 hover:bg-white/[0.03]"
                  href={`/posts/${previousPost.slug}`}
                >
                  <span className="text-[10px] uppercase tracking-[0.2em] text-white/28">← older</span>
                  <span className="truncate text-[12px] text-white/62 transition group-hover:text-white">
                    {previousPost.title}
                  </span>
                </Link>
              ) : (
                <span className="flex-1" />
              )}

              {nextPost ? (
                <Link
                  className="group flex min-w-0 flex-1 flex-col items-end gap-1 rounded-md border border-white/8 px-4 py-3 text-right transition hover:border-white/18 hover:bg-white/[0.03]"
                  href={`/posts/${nextPost.slug}`}
                >
                  <span className="text-[10px] uppercase tracking-[0.2em] text-white/28">newer →</span>
                  <span className="truncate text-[12px] text-white/62 transition group-hover:text-white">
                    {nextPost.title}
                  </span>
                </Link>
              ) : null}
            </div>
          ) : null}
        </footer>
      </article>
    </div>
  );
}
