import Image from "next/image";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import type { HTMLAttributes, LiHTMLAttributes, ReactNode } from "react";
import type { Post } from "@/lib/posts";

function formatDate(date: string) {
  return new Intl.DateTimeFormat("en-US", {
    month: "long",
    day: "2-digit",
    year: "numeric",
  }).format(new Date(date));
}

function renderInlineMarkdown(text: string) {
  const segments = text.split(/(\[[^\]]+\]\([^)]+\)|\*\*[^*]+\*\*|`[^`]+`)/g).filter(Boolean);

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

    if (/^`[^`]+`$/.test(segment)) {
      return (
        <code className="rounded bg-white/[0.08] px-1.5 py-1 font-mono text-[0.92em] text-white" key={`${segment}-${index}`}>
          {segment.slice(1, -1)}
        </code>
      );
    }

    return segment;
  });
}

function Paragraph({ children, ...props }: HTMLAttributes<HTMLParagraphElement>) {
  return (
    <p className="mt-5 text-[15px] leading-8 text-white/72 first:mt-0 sm:text-base" {...props}>
      {children}
    </p>
  );
}

function HeadingOne({ children, ...props }: HTMLAttributes<HTMLHeadingElement>) {
  return (
    <h1 className="mt-10 font-mono text-3xl font-semibold leading-tight text-white first:mt-0 sm:text-4xl" {...props}>
      {children}
    </h1>
  );
}

function HeadingTwo({ children, ...props }: HTMLAttributes<HTMLHeadingElement>) {
  return (
    <h2 className="mt-10 font-mono text-2xl font-semibold leading-tight text-white" {...props}>
      {children}
    </h2>
  );
}

function HeadingThree({ children, ...props }: HTMLAttributes<HTMLHeadingElement>) {
  return (
    <h3 className="mt-8 font-mono text-xl font-semibold leading-tight text-white" {...props}>
      {children}
    </h3>
  );
}

function ListItem({ children, ...props }: LiHTMLAttributes<HTMLLIElement>) {
  return (
    <li className="pl-1 text-[15px] leading-8 text-white/72 sm:text-base" {...props}>
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
          className="mt-6 overflow-x-auto rounded-[1.4rem] border border-dashed border-white/14 bg-black/70 px-4 py-4 text-sm leading-7 text-white/82"
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
          className="mt-6 border-l border-dashed border-white/20 pl-4 text-[15px] leading-8 text-white/58 sm:text-base"
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
  showMobileBackLink?: boolean;
};

export function PostReader({ post, showMobileBackLink = false }: PostReaderProps) {
  return (
    <section className="overflow-hidden rounded-[2rem] border border-dashed border-white/15 bg-white/[0.045] shadow-terminal backdrop-blur-xl">
      <div className="border-b border-dashed border-white/10 px-4 py-4 sm:px-6">
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="h-2.5 w-2.5 rounded-full bg-white/80" />
            <span className="h-2.5 w-2.5 rounded-full bg-white/35" />
            <span className="h-2.5 w-2.5 rounded-full bg-white/18" />
          </div>
          <span className="rounded-full border border-dashed border-white/12 px-3 py-1 text-[11px] uppercase tracking-[0.28em] text-white/44">
            reader
          </span>
        </div>

        {showMobileBackLink ? (
          <Link
            className="mt-4 inline-flex items-center gap-2 text-sm text-white/68 transition hover:text-white lg:hidden"
            href="/posts"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to posts
          </Link>
        ) : null}
      </div>

      <article className="px-4 py-6 sm:px-6 sm:py-8">
        <header className="border-b border-dashed border-white/10 pb-6">
          <div className="flex items-center gap-4">
            <div className="relative h-14 w-14 overflow-hidden rounded-full border border-dashed border-white/18 bg-black/45">
              <Image
                alt="Andre Ochoa"
                className="object-cover grayscale"
                fill
                sizes="56px"
                src="/profile.jpg"
              />
            </div>
            <div>
              <p className="text-sm text-white">Andre Ochoa</p>
              <p className="mt-1 text-xs uppercase tracking-[0.24em] text-white/40">{formatDate(post.date)}</p>
            </div>
          </div>

          <h1 className="mt-6 max-w-4xl font-mono text-3xl font-semibold leading-tight text-white sm:text-4xl">
            {post.title}
          </h1>

          <div className="mt-4 flex flex-wrap items-center gap-2 text-[11px] uppercase tracking-[0.24em] text-white/46">
            <span className="rounded-full border border-dashed border-white/12 px-3 py-1">{post.type}</span>
            <span className="rounded-full border border-dashed border-white/12 px-3 py-1">{post.wordCount} words</span>
            <span className="rounded-full border border-dashed border-white/12 px-3 py-1">
              {post.readingTimeMinutes} min read
            </span>
          </div>
        </header>

        <div className="mx-auto mt-8 max-w-[65ch]">
          {renderMarkdown(post.content)}
        </div>

        <footer className="mx-auto mt-10 max-w-[65ch] border-t border-dashed border-white/10 pt-5">
          <p className="text-sm uppercase tracking-[0.28em] text-white/46">Keep building. -Ochoa</p>
        </footer>
      </article>
    </section>
  );
}
