import { motion } from "framer-motion";
import { designers } from "../../data/designers";

export default function ThePeople() {
  return (
    <section
      id="people"
      className="py-32 bg-ivory overflow-hidden"
    >
      <div className="max-w-[1400px] mx-auto px-6 md:px-12 mb-20">
        <p className="text-xs font-bold tracking-[0.3em] text-ink/40 mb-4">
          08 — THE PEOPLE
        </p>
        <h2 className="text-display-md text-ink leading-none">
          TALENT FROM
          <br />
          EVERYWHERE
        </h2>
      </div>

      {/* Portrait grid — editorial proportions */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2 px-2">
        {designers.map((designer, i) => (
          <motion.div
            key={designer.id}
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{
              duration: 0.8,
              delay: i * 0.1,
              ease: [0.25, 0.1, 0.25, 1],
            }}
            // Alternate heights for editorial stagger
            className={`relative group overflow-hidden cursor-pointer ${
              i % 2 === 0 ? "mt-0" : "mt-8"
            }`}
            style={{ aspectRatio: "3/4" }}
          >
            <img
              src={designer.portrait}
              alt={designer.name}
              className="w-full h-full object-cover object-top grayscale group-hover:grayscale-0 transition-all duration-700 group-hover:scale-105"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            <div className="absolute bottom-0 left-0 p-4 text-ivory transform translate-y-4 group-hover:translate-y-0 transition-transform duration-500 opacity-0 group-hover:opacity-100">
              <h3 className="text-sm font-serif font-medium">{designer.name}</h3>
              <p className="text-xs text-ivory/70">{designer.specialty}</p>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Pull quote */}
      <motion.div
        initial={{ opacity: 0, y: 40 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 1, ease: [0.25, 0.1, 0.25, 1] }}
        className="max-w-[1400px] mx-auto px-6 md:px-12 mt-24 text-center"
      >
        <p className="text-editorial text-ink italic max-w-3xl mx-auto leading-tight">
          &ldquo;We believe the best creative talent shouldn't be hidden behind
          agency doors.&rdquo;
        </p>
        <p className="mt-6 text-sm font-bold tracking-widest text-ink/40">
          — LYNVIA FOUNDING TEAM
        </p>
      </motion.div>
    </section>
  );
}
