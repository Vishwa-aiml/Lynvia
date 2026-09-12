import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

export default function SplashScreen({ onComplete }: { onComplete: () => void }) {
  const [sweepDone, setSweepDone] = useState(false);

  return (
    <AnimatePresence onExitComplete={onComplete}>
      {!sweepDone && (
        <motion.div
          key="splash"
          initial={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.6, ease: "easeInOut" }}
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 9999,
            background: "linear-gradient(135deg, #2e0652 0%, #5b21b6 55%, #7c3aed 100%)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            overflow: "hidden",
          }}
        >
          {/* Deep radial glow */}
          <div
            style={{
              position: "absolute",
              inset: 0,
              background:
                "radial-gradient(ellipse 80% 50% at 50% 50%, rgba(139,92,246,0.3) 0%, transparent 70%)",
              pointerEvents: "none",
            }}
          />

          {/* The word — starts fully off-screen right, exits fully off-screen left */}
          <motion.div
            initial={{ x: "105vw" }}
            animate={{ x: "-105vw" }}
            transition={{
              duration: 6,          // slow-motion glide
              ease: "linear",       // constant speed = true slow-mo feel
              delay: 0.15,
            }}
            onAnimationComplete={() => setSweepDone(true)}
            style={{
              position: "absolute",
              whiteSpace: "nowrap",
              display: "flex",
              alignItems: "center",
              gap: "0.15em",
              /* slight skew for extra sporty slant */
              transform: "skewX(-10deg)",
            }}
          >
            {/* Main word */}
            <span
              style={{
                fontFamily: "'Barlow Condensed', 'Arial Narrow', Impact, sans-serif",
                fontWeight: 900,
                fontStyle: "italic",
                /*
                 * 18vw ≈ the word "LYNVIA" fills ~2/3 of the viewport width
                 * at condensed proportions (each char ≈ 0.55em wide).
                 * clamp keeps it reasonable on very small / very large screens.
                 */
                fontSize: "clamp(110px, 18vw, 260px)",
                letterSpacing: "0.06em",
                textTransform: "uppercase",
                color: "#ffffff",
                lineHeight: 1,
                textShadow:
                  "0 0 60px rgba(255,255,255,1), 0 0 120px rgba(255,255,255,1), 0 0 200px rgba(255,255,255,0.8)",
                userSelect: "none",
              }}
            >
              LYNVIA
            </span>
          </motion.div>

          {/* Thin horizontal speed-lines — burst in at start */}
          {[...Array(8)].map((_, i) => {
            const offsets = [-3, -2, -1.2, -0.4, 0.4, 1.2, 2, 3];
            return (
              <motion.div
                key={i}
                initial={{ scaleX: 0, opacity: 0 }}
                animate={{ scaleX: 1, opacity: [0, 0.15, 0] }}
                transition={{
                  duration: 1.2,
                  delay: 0.18 + i * 0.06,
                  ease: "easeOut",
                }}
                style={{
                  position: "absolute",
                  top: `calc(50% + ${offsets[i] * 28}px)`,
                  left: 0,
                  right: 0,
                  height: "1px",
                  background: "rgba(255,255,255,0.7)",
                  transformOrigin: "left center",
                  pointerEvents: "none",
                }}
              />
            );
          })}
        </motion.div>
      )}
    </AnimatePresence>
  );
}
