import { useRef } from "react";
import { motion, useScroll, useTransform } from "framer-motion";
import { designers } from "../../data/designers";

export default function TheCreative() {
  const containerRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start end", "end start"],
  });

  const imageY = useTransform(scrollYProgress, [0, 1], ["15%", "-15%"]);

  const featured = designers[0];
  const secondary = designers[1];

  return (
    <section
      id="the-creative"
      ref={containerRef}
      className="relative py-32 bg-ink text-ivory overflow-hidden"
    >
      <div className="max-w-[1400px] mx-auto px-6 md:px-12">
        <p className="text-xs font-bold tracking-[0.3em] text-ivory/40 mb-16">
          02 — THE CREATIVE
        </p>

        {/* Feature — Large asymmetric layout */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-0 items-stretch mb-40">
          {/* Image side */}
          <div className="relative overflow-hidden" style={{ aspectRatio: "4/5" }}>
            <motion.img
              src={featured.portrait}
              alt={featured.name}
              style={{ y: imageY }}
              className="w-full h-[120%] object-cover object-top -mt-[10%]"
            />
            <div className="absolute inset-0 bg-gradient-to-r from-transparent to-ink/20" />
          </div>

          {/* Text side */}
          <div className="flex flex-col justify-center pl-0 md:pl-16 pt-12 md:pt-0">
            <motion.p
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8, ease: [0.25, 0.1, 0.25, 1] }}
              className="text-editorial text-ivory/80 mb-10 italic"
            >
              &ldquo;{featured.quote}&rdquo;
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8, delay: 0.2, ease: [0.25, 0.1, 0.25, 1] }}
            >
              <h3 className="text-5xl font-serif font-medium mb-2">
                {featured.name}
              </h3>
              <p className="text-sm font-bold tracking-widest text-ivory/40 mb-8">
                {featured.specialty} · {featured.location}
              </p>



            </motion.div>
          </div>
        </div>

        {/* Secondary — Reversed layout */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-0 items-stretch">
          <div className="flex flex-col justify-center pr-0 md:pr-16 pb-12 md:pb-0 order-2 md:order-1">
            <motion.p
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8, ease: [0.25, 0.1, 0.25, 1] }}
              className="text-editorial text-ivory/80 mb-10 italic"
            >
              &ldquo;{secondary.quote}&rdquo;
            </motion.p>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8, delay: 0.2, ease: [0.25, 0.1, 0.25, 1] }}
            >
              <h3 className="text-5xl font-serif font-medium mb-2">
                {secondary.name}
              </h3>
              <p className="text-sm font-bold tracking-widest text-ivory/40">
                {secondary.specialty} · {secondary.location}
              </p>
            </motion.div>
          </div>

          <div
            className="relative overflow-hidden order-1 md:order-2"
            style={{ aspectRatio: "4/5" }}
          >
            <motion.img
              src={secondary.portrait}
              alt={secondary.name}
              style={{ y: imageY }}
              className="w-full h-[120%] object-cover object-top -mt-[10%]"
            />
          </div>
        </div>
      </div>
    </section>
  );
}
