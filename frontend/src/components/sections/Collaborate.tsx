import { motion } from "framer-motion";

const timelineItems = [
  {
    phase: "DISCOVERY",
    duration: "Day 1–2",
    description: "Brief alignment, vision boarding, and scope definition.",
    color: "border-accent bg-accent/10",
    dot: "bg-accent",
  },
  {
    phase: "CONCEPT",
    duration: "Day 3–7",
    description: "Initial concepts presented. Feedback loop begins.",
    color: "border-ivory/20 bg-ivory/5",
    dot: "bg-ivory/40",
  },
  {
    phase: "REFINEMENT",
    duration: "Day 8–14",
    description: "Chosen direction developed. Multiple revision rounds.",
    color: "border-ivory/20 bg-ivory/5",
    dot: "bg-ivory/40",
  },
  {
    phase: "PRODUCTION",
    duration: "Day 15–21",
    description: "Final files, assets, and deliverables produced.",
    color: "border-ivory/20 bg-ivory/5",
    dot: "bg-ivory/40",
  },
  {
    phase: "DELIVERY",
    duration: "Day 22",
    description: "All files handed over. Rights transferred. Done.",
    color: "border-green-400/50 bg-green-400/10",
    dot: "bg-green-400",
  },
];

export default function Collaborate() {
  return (
    <section
      id="collaborate"
      className="py-32 bg-ink text-ivory"
    >
      <div className="max-w-[1400px] mx-auto px-6 md:px-12">
        <p className="text-xs font-bold tracking-[0.3em] text-ivory/40 mb-4">
          06 — COLLABORATE
        </p>
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-8 mb-24">
          <h2 className="text-display-md text-ivory leading-none">
            BUILT TO
            <br />
            COLLABORATE
          </h2>
          <p className="max-w-sm font-serif text-xl text-ivory/60 leading-relaxed">
            A typical project timeline — structured yet flexible to fit every
            creative vision.
          </p>
        </div>

        {/* Timeline */}
        <div className="relative">
          {/* Vertical line */}
          <div className="absolute left-6 top-0 bottom-0 w-[1px] bg-ivory/10 hidden md:block" />

          <div className="space-y-6">
            {timelineItems.map((item, i) => (
              <motion.div
                key={item.phase}
                initial={{ opacity: 0, x: -40 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{
                  duration: 0.7,
                  delay: i * 0.15,
                  ease: [0.25, 0.1, 0.25, 1],
                }}
                className="relative flex items-start gap-8 md:pl-16"
              >
                {/* Timeline dot */}
                <div
                  className={`absolute left-[18px] top-6 w-3 h-3 rounded-full hidden md:block ${item.dot}`}
                />

                <div
                  className={`flex-1 border rounded-2xl p-6 md:p-8 flex flex-col md:flex-row md:items-center gap-4 md:gap-0 ${item.color}`}
                >
                  <div className="md:w-1/4">
                    <h3 className="text-2xl font-display font-black">
                      {item.phase}
                    </h3>
                  </div>
                  <p className="md:w-3/4 font-serif text-lg text-ivory/70 leading-relaxed">
                    {item.description}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
