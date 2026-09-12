import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";

export default function FinalCTA() {
  return (
    <section
      id="cta"
      className="relative py-48 bg-ink text-ivory overflow-hidden"
    >
      {/* Decorative background elements */}
      <div className="absolute inset-0 pointer-events-none">
        <div
          className="absolute -top-64 -right-64 w-[600px] h-[600px] rounded-full opacity-10"
          style={{
            background:
              "radial-gradient(circle, #7c3aed 0%, transparent 70%)",
          }}
        />
        <div
          className="absolute -bottom-64 -left-64 w-[500px] h-[500px] rounded-full opacity-10"
          style={{
            background:
              "radial-gradient(circle, #7c3aed 0%, transparent 70%)",
          }}
        />
      </div>

      <div className="max-w-[1400px] mx-auto px-6 md:px-12 relative z-10 text-center">
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, ease: [0.25, 0.1, 0.25, 1] }}
          className="text-xs font-bold tracking-[0.4em] text-ivory/40 mb-8"
        >
          09 — BEGIN
        </motion.p>

        <motion.h2
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 1, ease: [0.25, 0.1, 0.25, 1], delay: 0.1 }}
          className="text-huge text-ivory leading-none mb-12"
        >
          YOUR NEXT
          <br />
          <span className="text-accent">GREAT IDEA</span>
          <br />
          STARTS HERE.
        </motion.h2>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, delay: 0.3, ease: [0.25, 0.1, 0.25, 1] }}
          className="font-serif text-2xl text-ivory/60 max-w-lg mx-auto leading-relaxed mb-16"
        >
          Join thousands of brands who have trusted Lynvia to bring their
          vision to life.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, delay: 0.45, ease: [0.25, 0.1, 0.25, 1] }}
          className="flex flex-col sm:flex-row gap-4 justify-center"
        >
          <Link
            to="/start"
            className="inline-flex items-center justify-center gap-4 bg-ivory text-ink px-10 py-5 rounded-full font-black tracking-wider text-sm hover:gap-6 hover:bg-white transition-all duration-300 text-center"
          >
            POST YOUR PROJECT <ArrowRight size={16} />
          </Link>
          <Link
            to="/designers"
            className="inline-flex items-center justify-center gap-4 border border-ivory/30 text-ivory px-10 py-5 rounded-full font-black tracking-wider text-sm hover:bg-white/10 transition-all duration-300 text-center"
          >
            BROWSE DESIGNERS
          </Link>
        </motion.div>

        {/* Trust row */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 1, delay: 0.6 }}
          className="mt-24 flex flex-wrap items-center justify-center gap-8 text-xs font-bold tracking-widest text-ivory/30"
        >
          <span>NO SUBSCRIPTION</span>
          <span className="text-ivory/10">·</span>
          <span>PAY PER PROJECT</span>
          <span className="text-ivory/10">·</span>
          <span>FULL RIGHTS INCLUDED</span>
          <span className="text-ivory/10">·</span>
          <span>MONEY-BACK GUARANTEE</span>
        </motion.div>
      </div>
    </section>
  );
}
