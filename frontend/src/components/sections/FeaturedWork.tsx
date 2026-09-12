import { motion } from "framer-motion";
import { featuredProjects } from "../../data/projects";

export default function FeaturedWork() {
  return (
    <section id="featured-work" className="py-32 bg-ivory overflow-hidden">
      <div className="max-w-[1400px] mx-auto px-6 md:px-12 mb-16">
        <p className="text-xs font-bold tracking-[0.3em] text-ink/40 mb-4">
          03 — FEATURED WORK
        </p>
        <h2 className="text-display-md text-ink leading-none">
          IDEAS MADE
          <br />
          REAL
        </h2>
      </div>

      <div className="px-6 md:px-12 max-w-[1400px] mx-auto">
        {/* Row 1 — large left + medium right */}
        <div className="grid grid-cols-12 gap-4 mb-4">
          <motion.div
            initial={{ opacity: 0, y: 60 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.9, ease: [0.25, 0.1, 0.25, 1] }}
            className="col-span-12 md:col-span-7 relative group overflow-hidden cursor-pointer"
            style={{ aspectRatio: "16/10" }}
          >
            <img
              src={featuredProjects[0].image}
              alt={featuredProjects[0].title}
              className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-[1.04]"
            />
            <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors duration-500" />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 60 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.9, delay: 0.15, ease: [0.25, 0.1, 0.25, 1] }}
            className="col-span-12 md:col-span-5 relative group overflow-hidden cursor-pointer"
            style={{ aspectRatio: "5/4" }}
          >
            <img
              src={featuredProjects[1].image}
              alt={featuredProjects[1].title}
              className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-[1.04]"
            />
            <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors duration-500" />
          </motion.div>
        </div>

        {/* Row 2 — medium left + large right */}
        <div className="grid grid-cols-12 gap-4">
          <motion.div
            initial={{ opacity: 0, y: 60 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.9, delay: 0.2, ease: [0.25, 0.1, 0.25, 1] }}
            className="col-span-12 md:col-span-5 relative group overflow-hidden cursor-pointer"
            style={{ aspectRatio: "5/4" }}
          >
            <img
              src={featuredProjects[2].image}
              alt={featuredProjects[2].title}
              className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-[1.04]"
            />
            <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors duration-500" />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 60 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.9, delay: 0.3, ease: [0.25, 0.1, 0.25, 1] }}
            className="col-span-12 md:col-span-7 relative group overflow-hidden cursor-pointer"
            style={{ aspectRatio: "16/10" }}
          >
            <img
              src={featuredProjects[3].image}
              alt={featuredProjects[3].title}
              className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-[1.04]"
            />
            <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors duration-500" />
          </motion.div>
        </div>
      </div>
    </section>
  );
}
