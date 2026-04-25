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
    <div className="flex items-center justify-center gap-1 text-[16px] text-white/72 sm:text-[18px]">
      <span className="text-white/48">&gt;</span>
      <AnimatePresence mode="wait">
        <motion.span
          animate={{ opacity: 1, y: 0 }}
          className="inline-block min-w-[7ch] text-left text-[#e8e8e8]"
          exit={{ opacity: 0, y: -6 }}
          initial={{ opacity: 0, y: 6 }}
          key={words[index]}
          transition={{ duration: 0.18, ease: "easeOut" }}
        >
          {words[index]}
        </motion.span>
      </AnimatePresence>
      <motion.span
        animate={{ opacity: [1, 0, 1] }}
        aria-hidden="true"
        className="text-[#e8e8e8]"
        transition={{ duration: 0.9, ease: "linear", repeat: Number.POSITIVE_INFINITY }}
      >
        _
      </motion.span>
    </div>
  );
}
