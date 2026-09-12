import { useRef } from "react";
import { motion, useScroll, useTransform } from "framer-motion";

export default function Deliver() {
  const containerRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start end", "end start"],
  });

  const scale = useTransform(scrollYProgress, [0, 0.5, 1], [0.85, 1, 1.05]);
  const opacity = useTransform(scrollYProgress, [0, 0.2, 0.8, 1], [0, 1, 1, 0]);
  const textY = useTransform(scrollYProgress, [0.2, 0.6], ["40px", "0px"]);

  return (
    <section
      id="deliver"
      ref={containerRef}
      className="relative h-screen flex items-center justify-center overflow-hidden bg-ivory"
    >
      {/* Full-bleed image */}
      <motion.div
        style={{ scale }}
        className="absolute inset-0 z-0"
      >
        <img
          src="https://images.unsplash.com/photo-1561070791-2526d30994b5?q=80&w=2560&auto=format&fit=crop"
          alt="Delivered Creative Work"
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-black/50" />
      </motion.div>

      {/* Centered content */}
      <motion.div
        style={{ opacity, y: textY }}
        className="relative z-10 text-center text-ivory px-6"
      >
        <p className="text-xs font-bold tracking-[0.3em] text-ivory/50 mb-6">
          07 — DELIVER
        </p>
        <h2 className="text-huge leading-none mb-8">
          YOUR VISION,
          <br />
          DELIVERED.
        </h2>
        <p className="font-serif text-2xl text-ivory/70 max-w-xl mx-auto leading-relaxed">
          Premium creative assets. All rights included. No surprises, ever.
        </p>

        {/* Stats row */}
        <div className="mt-16 flex flex-col sm:flex-row justify-center gap-12 sm:gap-24">
          {[
            { value: "4.4/5", label: "User Rating" },
            { value: "98%", label: "Client Satisfaction" },
            { value: "72h", label: "Average First Draft" },
          ].map((stat) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8, ease: [0.25, 0.1, 0.25, 1] }}
              className="text-center"
            >
              <p className="text-5xl font-display font-black text-ivory">
                {stat.value}
              </p>
              <p className="text-xs font-bold tracking-widest text-ivory/50 mt-2">
                {stat.label}
              </p>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </section>
  );
}
