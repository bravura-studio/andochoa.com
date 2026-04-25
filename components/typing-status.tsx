"use client";

import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useState } from "react";

const words = ["builder", "maker", "father", "dreamer"];

export function TypingStatus() {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const interval = window.setInterval(() => {
      setIndex((current) => (current + 1) % words.length);
    }, 2200);

    return () => window.clearInterval(interval);
  }, []);

  return (
    <div className="flex items-center gap-2 text-sm text-white/68 sm:text-base">
      <span className="text-white/38">&gt;</span>
      <AnimatePresence mode="wait">
        <motion.span
          animate={{ opacity: 1, y: 0 }}
          className="inline-block min-w-[7ch] text-white"
          exit={{ opacity: 0, y: -8 }}
          initial={{ opacity: 0, y: 8 }}
          key={words[index]}
          transition={{ duration: 0.2, ease: "easeOut" }}
        >
          {words[index]}
        </motion.span>
      </AnimatePresence>
      <span className="h-5 w-2 animate-blink rounded-full bg-white/85" />
    </div>
  );
}
