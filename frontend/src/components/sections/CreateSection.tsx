import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";

const transitions = [
  { from: "IDEA", to: "BRIEF", connector: "becomes" },
  { from: "BRIEF", to: "CREATIVE", connector: "attracts" },
  { from: "CREATIVE", to: "WORK", connector: "produces" },
];

export default function CreateSection() {
  return (
    <section
      id="create"
      className="py-40 bg-ink text-ivory overflow-hidden"
    >
      <div className="max-w-[1400px] mx-auto px-6 md:px-12">
        <p className="text-xs font-bold tracking-[0.3em] text-ivory/40 mb-4">
          05 — CREATE
        </p>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          {/* Left text */}
          <div>
            <h2 className="text-display-md text-ivory leading-none mb-12">
              START
              <br />
              CREATING
              <br />
              TODAY
            </h2>
            <p className="font-serif text-xl text-ivory/70 leading-relaxed max-w-md mb-12">
              Every great piece of work starts with a spark. Lynvia turns that
              spark into something the world can see, feel, and remember.
            </p>
            <Link
              to="/start"
              className="inline-flex items-center gap-4 bg-ivory text-ink px-8 py-4 rounded-full font-bold tracking-wider text-sm hover:gap-6 transition-all duration-300"
            >
              POST A PROJECT <ArrowRight size={16} />
            </Link>
          </div>

          {/* Right — Relationship chain visualization */}
          <div className="space-y-0">
            {transitions.map((t, i) => (
              <motion.div
                key={t.from}
                initial={{ opacity: 0, x: 60 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{
                  duration: 0.8,
                  delay: i * 0.2,
                  ease: [0.25, 0.1, 0.25, 1],
                }}
                className="flex items-center gap-0"
              >
                <div className="flex-1">
                  <div className="border border-ivory/20 rounded-2xl p-6 hover:border-accent hover:bg-accent/5 transition-all duration-500 cursor-default group">
                    <p className="text-xs text-ivory/40 font-bold tracking-widest mb-2">
                      {String(i + 1).padStart(2, "0")}
                    </p>
                    <p className="text-4xl font-display font-black text-ivory group-hover:text-accent transition-colors duration-300">
                      {t.from}
                    </p>
                  </div>
                </div>

                <div className="flex flex-col items-center px-4 shrink-0">
                  <p className="text-xs text-ivory/30 font-bold tracking-widest -rotate-90 whitespace-nowrap">
                    {t.connector}
                  </p>
                  <ArrowRight size={20} className="text-ivory/30 mt-1" />
                </div>
              </motion.div>
            ))}

            {/* Final node */}
            <motion.div
              initial={{ opacity: 0, x: 60 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8, delay: 0.6, ease: [0.25, 0.1, 0.25, 1] }}
              className="flex-1 mt-0"
            >
              <div className="border-2 border-accent rounded-2xl p-6 bg-accent/10">
                <p className="text-xs text-accent/60 font-bold tracking-widest mb-2">
                  04
                </p>
                <p className="text-4xl font-display font-black text-accent">
                  WORK
                </p>
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </section>
  );
}
