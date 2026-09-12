import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

const chapters = [
  { id: "hero", number: "00", title: "IDEAS" },
  { id: "discover", number: "01", title: "DISCOVER" },
  { id: "the-creative", number: "02", title: "CREATIVE" },
  { id: "featured-work", number: "03", title: "WORK" },
  { id: "create", number: "04", title: "CREATE" },
  { id: "how-it-works", number: "05", title: "PROCESS" },
  { id: "collaborate", number: "06", title: "COLLABORATE" },
  { id: "deliver", number: "07", title: "DELIVER" },
  { id: "people", number: "08", title: "THE PEOPLE" },
  { id: "cta", number: "09", title: "BEGIN" },
];

export default function ChapterNav() {
  const [activeChapter, setActiveChapter] = useState("hero");

  useEffect(() => {
    const handleScroll = () => {
      let current = "hero";
      for (const chapter of chapters) {
        const section = document.getElementById(chapter.id);
        if (!section) continue;
        const rect = section.getBoundingClientRect();
        if (rect.top <= window.innerHeight * 0.45) {
          current = chapter.id;
        }
      }
      setActiveChapter(current);
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    handleScroll();
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // Determine if we're on a light or dark section for text color
  const darkSections = ["the-creative", "create", "how-it-works", "collaborate", "cta"];
  const isDark = !darkSections.includes(activeChapter);
  // hero and deliver are also dark (dark bg)
  const heroDeliverDark = ["hero", "deliver"].includes(activeChapter);
  const textClass = isDark || heroDeliverDark ? "text-white" : "text-ink";

  return (
    <div className={`fixed left-5 top-1/2 -translate-y-1/2 z-40 hidden lg:flex flex-col gap-4 transition-colors duration-500 ${textClass}`}>
      {chapters.map((chapter) => {
        const isActive = activeChapter === chapter.id;
        return (
          <a
            key={chapter.id}
            href={`#${chapter.id}`}
            onClick={(e) => {
              e.preventDefault();
              document.getElementById(chapter.id)?.scrollIntoView({ behavior: "smooth" });
            }}
            className={`group flex items-center gap-3 text-[10px] font-black tracking-[0.2em] transition-all duration-300 ${
              isActive ? "opacity-100" : "opacity-20 hover:opacity-60"
            }`}
          >
            <div className={`w-1 rounded-full transition-all duration-500 ${isActive ? "h-6 bg-current" : "h-1 bg-current"}`} />
            <AnimatePresence>
              {isActive && (
                <motion.span
                  initial={{ opacity: 0, x: -6, width: 0 }}
                  animate={{ opacity: 1, x: 0, width: "auto" }}
                  exit={{ opacity: 0, x: -6, width: 0 }}
                  className="overflow-hidden whitespace-nowrap"
                >
                  {chapter.title}
                </motion.span>
              )}
            </AnimatePresence>
          </a>
        );
      })}
    </div>
  );
}
