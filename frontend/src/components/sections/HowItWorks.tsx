import { useRef, useState, useEffect } from "react";
import { motion, AnimatePresence, useScroll } from "framer-motion";
import { Lightbulb, Sparkles, MessageSquare, Users, PackageCheck } from "lucide-react";

const steps = [
  {
    number: "01",
    title: "POST YOUR IDEA",
    description:
      "Describe your project in your own words. No briefs required. Just share what you're imagining — we'll help shape it.",
    icon: Lightbulb,
    bg: "linear-gradient(135deg, #1a0533 0%, #3b0764 60%, #6d28d9 100%)",
    accent: "#a855f7",
  },
  {
    number: "02",
    title: "MATCH WITH CREATIVES",
    description:
      "Our platform surfaces designers whose style, specialty, and experience match your vision. Explore their portfolios.",
    icon: Sparkles,
    bg: "linear-gradient(135deg, #0f172a 0%, #1e3a5f 60%, #1d4ed8 100%)",
    accent: "#60a5fa",
  },
  {
    number: "03",
    title: "ALIGN & BRIEF",
    description:
      "Have a direct conversation with your chosen designer. Refine the brief, set milestones, and agree on deliverables.",
    icon: MessageSquare,
    bg: "linear-gradient(135deg, #0d1f0f 0%, #14532d 60%, #16a34a 100%)",
    accent: "#4ade80",
  },
  {
    number: "04",
    title: "COLLABORATE",
    description:
      "Track progress through our shared workspace. Provide feedback, iterate together, and watch your idea come to life.",
    icon: Users,
    bg: "linear-gradient(135deg, #1c0a00 0%, #7c2d12 60%, #ea580c 100%)",
    accent: "#fb923c",
  },
  {
    number: "05",
    title: "RECEIVE & OWN",
    description:
      "Once you're satisfied, finalize payment and receive all files. Full rights. No hidden fees. Forever yours.",
    icon: PackageCheck,
    bg: "linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 60%, #16213e 100%)",
    accent: "#e2e8f0",
  },
];

export default function HowItWorks() {
  const containerRef = useRef<HTMLDivElement>(null);
  const [activeStep, setActiveStep] = useState(0);

  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end end"],
  });

  useEffect(() => {
    const unsubscribe = scrollYProgress.on("change", (v) => {
      const index = Math.min(steps.length - 1, Math.floor(v * steps.length));
      setActiveStep(index);
    });
    return unsubscribe;
  }, [scrollYProgress]);

  const step = steps[activeStep];
  const Icon = step.icon;

  return (
    <section
      id="how-it-works"
      ref={containerRef}
      className="relative bg-ivory"
      style={{ height: `${steps.length * 100}vh` }}
    >
      <div className="sticky top-0 h-screen flex overflow-hidden">

        {/* ── Left info panel ── */}
        <div className="w-full md:w-[42%] flex flex-col justify-center px-8 md:px-12 border-r border-black/10 shrink-0">
          <p className="text-xs font-bold tracking-[0.3em] text-black/40 mb-4">
            04 — HOW IT WORKS
          </p>
          <h2
            style={{
              fontFamily: "var(--font-display)",
              fontSize: "clamp(2.8rem, 5.5vw, 6.5rem)",
              lineHeight: 0.9,
              fontWeight: 900,
              textTransform: "uppercase",
            }}
          >
            FROM IDEA
            <br />
            TO ICON
          </h2>
          <p
            className="mt-5 max-w-xs text-black/55 text-base leading-relaxed hidden md:block"
            style={{ fontFamily: "var(--font-serif)" }}
          >
            A seamless process built around creativity, clarity, and confidence.
          </p>

          {/* Progress bar */}
          <div className="mt-10 w-full max-w-[220px]">
            <div className="h-[1px] bg-black/10 w-full relative overflow-hidden">
              <motion.div
                className="absolute inset-y-0 left-0"
                animate={{ width: `${((activeStep + 1) / steps.length) * 100}%`, backgroundColor: step.accent }}
                transition={{ duration: 0.5, ease: "easeInOut" }}
                style={{ backgroundColor: step.accent }}
              />
            </div>
            <div className="flex justify-between mt-2 text-[10px] text-black/30 font-bold tracking-wider">
              <span>START</span>
              <span>DELIVER</span>
            </div>
          </div>

          {/* Dot indicators */}
          <div className="mt-5 flex gap-2 items-center">
            {steps.map((s, i) => (
              <motion.div
                key={i}
                animate={{
                  width: i === activeStep ? 20 : 8,
                  backgroundColor: i === activeStep ? s.accent : "rgba(17,17,17,0.15)",
                }}
                transition={{ duration: 0.35 }}
                style={{ height: 8, borderRadius: 4 }}
              />
            ))}
          </div>

          {/* Step counter */}
          <motion.p
            key={activeStep}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-8 text-xs font-bold tracking-widest text-black/30"
          >
            STEP {steps[activeStep].number} OF {String(steps.length).padStart(2, "0")}
          </motion.p>
        </div>

        {/* ── Right card panel ── */}
        <div className="hidden md:flex flex-1 items-center justify-center px-8 md:px-12 bg-ivory overflow-hidden">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeStep}
              initial={{ opacity: 0, y: 80, scale: 0.92, rotateX: 8 }}
              animate={{ opacity: 1, y: 0, scale: 1, rotateX: 0 }}
              exit={{ opacity: 0, y: -60, scale: 0.95, rotateX: -6 }}
              transition={{ duration: 0.55, ease: [0.25, 0.1, 0.25, 1] }}
              style={{
                width: "100%",
                maxWidth: 480,
                borderRadius: 24,
                background: step.bg,
                boxShadow: `0 32px 80px rgba(0,0,0,0.35), 0 0 0 1px rgba(255,255,255,0.08), inset 0 1px 0 rgba(255,255,255,0.12)`,
                padding: "3rem",
                position: "relative",
                overflow: "hidden",
                perspective: 800,
              }}
            >
              {/* Watermark number */}
              <span
                style={{
                  position: "absolute",
                  right: "-0.5rem",
                  bottom: "-2rem",
                  fontFamily: "var(--font-display)",
                  fontSize: "clamp(8rem, 16vw, 18rem)",
                  fontWeight: 900,
                  lineHeight: 1,
                  color: "rgba(255,255,255,0.06)",
                  userSelect: "none",
                  pointerEvents: "none",
                  letterSpacing: "-0.05em",
                }}
              >
                {step.number}
              </span>

              {/* Glow orb */}
              <div style={{
                position: "absolute",
                top: -80,
                right: -80,
                width: 240,
                height: 240,
                borderRadius: "50%",
                background: `radial-gradient(circle, ${step.accent}33 0%, transparent 70%)`,
                pointerEvents: "none",
              }} />

              {/* Icon */}
              <motion.div
                initial={{ scale: 0.5, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: 0.15, duration: 0.4, ease: "backOut" }}
                style={{
                  width: 56,
                  height: 56,
                  borderRadius: 16,
                  background: `${step.accent}22`,
                  border: `1px solid ${step.accent}44`,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  marginBottom: "1.5rem",
                }}
              >
                <Icon size={26} color={step.accent} strokeWidth={1.5} />
              </motion.div>

              {/* Step label */}
              <p style={{
                fontFamily: "var(--font-sans)",
                fontSize: "0.65rem",
                fontWeight: 700,
                letterSpacing: "0.3em",
                color: `${step.accent}99`,
                marginBottom: "0.75rem",
                textTransform: "uppercase",
              }}>
                STEP {step.number}
              </p>

              {/* Title */}
              <motion.h3
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.1, duration: 0.4 }}
                style={{
                  fontFamily: "var(--font-display)",
                  fontSize: "clamp(1.8rem, 3vw, 2.6rem)",
                  fontWeight: 900,
                  textTransform: "uppercase",
                  color: "#ffffff",
                  lineHeight: 0.95,
                  letterSpacing: "-0.02em",
                  marginBottom: "1.25rem",
                }}
              >
                {step.title}
              </motion.h3>

              {/* Description */}
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.2, duration: 0.4 }}
                style={{
                  fontFamily: "var(--font-serif)",
                  fontSize: "1.05rem",
                  color: "rgba(255,255,255,0.65)",
                  lineHeight: 1.7,
                  position: "relative",
                  zIndex: 1,
                }}
              >
                {step.description}
              </motion.p>

              {/* Bottom accent line */}
              <motion.div
                initial={{ scaleX: 0 }}
                animate={{ scaleX: 1 }}
                transition={{ delay: 0.3, duration: 0.5, ease: "easeOut" }}
                style={{
                  marginTop: "2rem",
                  height: 2,
                  background: `linear-gradient(90deg, ${step.accent} 0%, transparent 100%)`,
                  borderRadius: 1,
                  transformOrigin: "left",
                }}
              />
            </motion.div>
          </AnimatePresence>
        </div>

      </div>
    </section>
  );
}
