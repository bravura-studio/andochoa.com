"use client";

import { motion } from "framer-motion";
import { useEffect, useState } from "react";

const words = ["builder", "maker", "father", "dreamer"];
const typingSpeedMs = 90;
const deletingSpeedMs = 45;
const pauseAfterTypingMs = 1100;
const pauseAfterDeletingMs = 220;

export function TypingStatus() {
  const [index, setIndex] = useState(0);
  const [displayedWord, setDisplayedWord] = useState("");
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    const currentWord = words[index];

    if (!isDeleting && displayedWord === currentWord) {
      const timeout = window.setTimeout(() => {
        setIsDeleting(true);
      }, pauseAfterTypingMs);

      return () => window.clearTimeout(timeout);
    }

    if (isDeleting && displayedWord.length === 0) {
      const timeout = window.setTimeout(() => {
        setIsDeleting(false);
        setIndex((current) => (current + 1) % words.length);
      }, pauseAfterDeletingMs);

      return () => window.clearTimeout(timeout);
    }

    const timeout = window.setTimeout(() => {
      setDisplayedWord((current) =>
        isDeleting ? current.slice(0, -1) : currentWord.slice(0, current.length + 1),
      );
    }, isDeleting ? deletingSpeedMs : typingSpeedMs);

    return () => window.clearTimeout(timeout);
  }, [displayedWord, index, isDeleting]);

  return (
    <div className="flex items-center justify-center gap-1 text-[16px] text-white/72 sm:text-[18px]">
      <span className="text-white/48">&gt;</span>
      <span className="inline-flex min-w-[7ch] items-center text-left text-[#e8e8e8]">
        <span>{displayedWord}</span>
        <motion.span
          animate={{ opacity: [1, 0, 1] }}
          aria-hidden="true"
          className="inline-block"
          transition={{ duration: 0.9, ease: "linear", repeat: Number.POSITIVE_INFINITY }}
        >
          _
        </motion.span>
      </span>
    </div>
  );
}
