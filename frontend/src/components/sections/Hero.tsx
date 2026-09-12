import { motion, useScroll, useTransform } from "framer-motion";
import { useRef } from "react";
import { Link } from "react-router-dom";

export default function Hero() {
  const containerRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end start"],
  });

  const y = useTransform(scrollYProgress, [0, 1], ["0%", "50%"]);
  const opacity = useTransform(scrollYProgress, [0, 0.5], [1, 0]);
  const scale = useTransform(scrollYProgress, [0, 1], [1, 1.1]);

  return (
    <section
      id="hero"
      ref={containerRef}
      className="relative h-screen w-full overflow-hidden bg-ink text-ivory"
    >
      {/* Parallax background video */}
      <motion.div
        className="absolute inset-0 z-0"
        style={{ y, scale }}
      >
        <div className="absolute inset-0 bg-black/50 z-10" />
        <video
          autoPlay
          loop
          muted
          playsInline
          className="w-full h-full object-cover object-center"
        >
          <source src="/hero-bg.mp4" type="video/mp4" />
        </video>
      </motion.div>

      {/* Heading — top-left, below navbar */}
      <motion.div
        className="absolute z-10 left-6 md:left-12 right-6 md:right-12"
        style={{ opacity, top: "96px" }}
        initial={{ y: 50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 1, ease: [0.25, 0.1, 0.25, 1], delay: 0.2 }}
      >
        <h1
          style={{
            fontFamily: "var(--font-display)",
            fontSize: "clamp(3rem, 10vw, 11rem)",
            lineHeight: 0.88,
            fontWeight: 900,
            textTransform: "uppercase",
            marginLeft: "-4px",
          }}
        >
          <span className="block">IDEAS</span>
          <span className="block">DESERVE</span>
          <span className="block">GREAT</span>
          <span className="block">DESIGN.</span>
        </h1>
      </motion.div>

      {/* Buttons — pinned to bottom right */}
      <motion.div
        className="absolute z-10 right-6 md:right-12"
        style={{ opacity, bottom: "48px" }}
        initial={{ y: 30, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 1, ease: [0.25, 0.1, 0.25, 1], delay: 0.55 }}
      >
        <div className="flex flex-row gap-3 shrink-0">
            <Link
              to="/explore"
              className="bg-white text-black px-6 md:px-8 py-3 md:py-4 rounded-full font-bold tracking-wider text-xs md:text-sm hover:bg-white/90 transition-colors text-center whitespace-nowrap"
            >
              EXPLORE DESIGNERS
            </Link>
            <Link
              to="/start"
              className="border border-white/40 text-white px-6 md:px-8 py-3 md:py-4 rounded-full font-bold tracking-wider text-xs md:text-sm hover:bg-white/10 transition-colors text-center whitespace-nowrap"
            >
              START A PROJECT
            </Link>
          </div>
      </motion.div>
    </section>
  );
}
