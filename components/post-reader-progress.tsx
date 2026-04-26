"use client";

import { useEffect, useRef, useState } from "react";

type PostReaderProgressProps = {
  postSlug: string;
};

export function PostReaderProgress({ postSlug }: PostReaderProgressProps) {
  const progressBarRef = useRef<HTMLDivElement | null>(null);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const progressBar = progressBarRef.current;
    const container = progressBar?.closest<HTMLElement>("[data-post-reader-container]");
    const article = container?.querySelector<HTMLElement>("[data-post-reader-article]");

    if (!progressBar || !container || !article) {
      setProgress(0);
      return;
    }

    const getScrollRoot = () => {
      let parent = container.parentElement;

      while (parent) {
        const { overflowY } = window.getComputedStyle(parent);
        const isScrollable = /(auto|scroll)/u.test(overflowY) && parent.scrollHeight > parent.clientHeight + 1;

        if (isScrollable) {
          return parent;
        }

        parent = parent.parentElement;
      }

      return document.scrollingElement;
    };

    const scrollRoot = getScrollRoot();
    const isDocumentScrollRoot = scrollRoot === document.scrollingElement;

    const clampProgress = (value: number) => Math.max(0, Math.min(1, value));

    const updateProgress = () => {
      const articleRect = article.getBoundingClientRect();
      const articleHeight = articleRect.height;

      if (scrollRoot instanceof HTMLElement && !isDocumentScrollRoot) {
        const scrollRootRect = scrollRoot.getBoundingClientRect();
        const articleTop = articleRect.top - scrollRootRect.top + scrollRoot.scrollTop;
        const scrollRange = articleHeight - scrollRoot.clientHeight;

        if (scrollRange <= 0) {
          setProgress(0);
          return;
        }

        setProgress(clampProgress((scrollRoot.scrollTop - articleTop) / scrollRange));
        return;
      }

      const articleTop = window.scrollY + articleRect.top;
      const scrollRange = articleHeight - window.innerHeight;

      if (scrollRange <= 0) {
        setProgress(0);
        return;
      }

      setProgress(clampProgress((window.scrollY - articleTop) / scrollRange));
    };

    updateProgress();
    if (scrollRoot instanceof HTMLElement && !isDocumentScrollRoot) {
      scrollRoot.addEventListener("scroll", updateProgress, { passive: true });
    } else {
      window.addEventListener("scroll", updateProgress, { passive: true });
    }
    window.addEventListener("resize", updateProgress);

    return () => {
      if (scrollRoot instanceof HTMLElement && !isDocumentScrollRoot) {
        scrollRoot.removeEventListener("scroll", updateProgress);
      } else {
        window.removeEventListener("scroll", updateProgress);
      }
      window.removeEventListener("resize", updateProgress);
    };
  }, [postSlug]);

  return (
    <div className="fixed left-0 right-0 top-0 z-50 h-[3px] overflow-hidden bg-white/[0.10]" ref={progressBarRef}>
      <div className="h-full bg-white/[0.55] transition-[width] duration-150" style={{ width: `${progress * 100}%` }} />
    </div>
  );
}
