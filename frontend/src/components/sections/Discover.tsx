import { useRef } from "react";
import { motion, useScroll, useTransform } from "framer-motion";
import { designers } from "../../data/designers";
import { ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";

export default function Discover() {
  const containerRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start end", "end start"],
  });

  const x1 = useTransform(scrollYProgress, [0, 1], ["5%", "-5%"]);
  const x2 = useTransform(scrollYProgress, [0, 1], ["-5%", "5%"]);

  const featuredRow = designers.slice(0, 3);
  const secondaryRow = designers.slice(3, 6);

  return (
    <section
      id="discover"
      ref={containerRef}
      className="relative py-32 bg-ivory overflow-hidden"
    >
      {/* Section Label */}
      <div className="px-6 md:px-12 max-w-[1400px] mx-auto mb-16">
        <div className="flex items-end justify-between">
          <div>
            <p className="text-xs font-bold tracking-[0.3em] text-ink/40 mb-4">
              DISCOVER
            </p>
            <h2 className="text-display-md text-ink leading-none">
              MEET THE
              <br />
              CREATIVES
            </h2>
          </div>
          <Link
            to="/designers"
            className="hidden md:flex items-center gap-3 text-sm font-bold tracking-wider text-ink border-b border-ink pb-1 hover:gap-5 transition-all duration-300"
          >
            VIEW ALL DESIGNERS <ArrowRight size={14} />
          </Link>
        </div>
      </div>

      {/* Row 1 — scrolls left */}
      <motion.div
        style={{ x: x1 }}
        className="flex gap-5 mb-5 pl-6 md:pl-12"
      >
        {featuredRow.map((designer, i) => (
          <motion.div
            key={designer.id}
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8, delay: i * 0.15, ease: [0.25, 0.1, 0.25, 1] }}
            className="relative flex-shrink-0 group cursor-pointer overflow-hidden"
            style={{ width: "clamp(260px, 28vw, 420px)", aspectRatio: "3/4" }}
          >
            <img
              src={designer.image}
              alt={designer.name}
              className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/30 via-transparent to-transparent" />
          </motion.div>
        ))}
      </motion.div>

      {/* Row 2 — scrolls right, offset */}
      <motion.div
        style={{ x: x2 }}
        className="flex gap-5 justify-end pr-6 md:pr-12"
      >
        {secondaryRow.map((designer, i) => (
          <motion.div
            key={designer.id}
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8, delay: i * 0.15 + 0.3, ease: [0.25, 0.1, 0.25, 1] }}
            className="relative flex-shrink-0 group cursor-pointer overflow-hidden"
            style={{ width: "clamp(220px, 22vw, 360px)", aspectRatio: "3/4" }}
          >
            <img
              src={designer.image}
              alt={designer.name}
              className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/20 via-transparent to-transparent" />
          </motion.div>
        ))}
      </motion.div>

      {/* Mobile CTA */}
      <div className="md:hidden px-6 mt-10">
        <Link
          to="/designers"
          className="flex items-center gap-3 text-sm font-bold tracking-wider text-ink border-b border-ink pb-1 w-fit"
        >
          VIEW ALL DESIGNERS <ArrowRight size={14} />
        </Link>
      </div>
    </section>
  );
}
