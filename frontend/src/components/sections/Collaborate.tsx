import { motion } from "framer-motion";
import { 
  Compass, 
  Lightbulb, 
  RefreshCw, 
  Settings, 
  CheckCircle,
  User,
  PenTool,
  ShieldCheck,
  MessageSquare,
  Star,
  TrendingUp,
  Users
} from "lucide-react";

const timelineItems = [
  {
    phase: "Discovery",
    number: "01",
    description: "Client shares their vision, goals and requirements.",
    tags: ["Requirements", "References", "Goals", "Budget"],
    clientRole: "Shares brief, references and expectations.",
    designerRole: "Reviews the brief, asks questions if needed.",
    icon: Compass,
    color: "border-purple-400/80 bg-purple-400/20",
    dot: "bg-purple-400",
    glow: "rgba(192,132,252,0.15)",
  },
  {
    phase: "Concept",
    number: "02",
    description: "Designer presents initial design directions.",
    tags: ["Concepts", "Styles", "Moodboards", "Direction"],
    designerRole: "Shares initial concepts and creative direction.",
    clientRole: "Reviews and gives feedback.",
    icon: Lightbulb,
    color: "border-slate-300/80 bg-slate-300/20",
    dot: "bg-slate-300",
    glow: "rgba(203,213,225,0.15)",
  },
  {
    phase: "Refinement",
    number: "03",
    description: "We collaborate to fine-tune the design.",
    tags: ["Feedback", "Revisions", "Approval"],
    clientRole: "Shares feedback and requests changes.",
    designerRole: "Makes revisions and prepares the final version.",
    icon: RefreshCw,
    color: "border-yellow-400/80 bg-yellow-400/20",
    dot: "bg-yellow-400",
    glow: "rgba(250,204,21,0.15)",
  },
  {
    phase: "Production",
    number: "04",
    description: "Final design is prepared with all required assets.",
    tags: ["Final artwork", "Assets", "Formats", "Quality check"],
    designerRole: "Creates final files and ensures quality standards.",
    clientRole: "Reviews the final design before delivery.",
    icon: Settings,
    color: "border-teal-400/80 bg-teal-400/20",
    dot: "bg-teal-400",
    glow: "rgba(45,212,191,0.15)",
  },
  {
    phase: "Delivery",
    number: "05",
    description: "Your project is completed and ready to use.",
    tags: ["Final files", "Handover", "Rights transfer"],
    designerRole: "Delivers all files and assets.",
    clientRole: "Receives the final files and project is marked complete.",
    icon: CheckCircle,
    color: "border-green-400/80 bg-green-400/20",
    dot: "bg-green-400",
    glow: "rgba(74,222,128,0.15)",
  },
];

export default function Collaborate() {
  return (
    <section id="collaborate" className="py-32 bg-[#0b0c10] text-ivory">
      <div className="max-w-[1200px] mx-auto px-6 md:px-12">
        <div className="text-center mb-24">
          <h2 className="text-display-md text-ivory leading-none mb-6">
            BUILT TO COLLABORATE
          </h2>
          <p className="font-serif text-xl text-ivory/60 leading-relaxed mx-auto max-w-2xl">
            A typical project timeline — structured yet flexible to fit every creative vision. 
            Clients and designers aligned from the first idea to the final delivery.
          </p>
        </div>

        {/* Timeline */}
        <div className="relative mb-24">
          {/* Vertical line */}
          <div className="absolute left-6 top-10 bottom-10 w-[2px] bg-ivory/10 hidden md:block" />

          <div className="space-y-6">
            {timelineItems.map((item, i) => {
              const Icon = item.icon;
              return (
                <motion.div
                  key={item.phase}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: i * 0.1 }}
                  className="relative flex flex-col md:flex-row items-stretch gap-6 md:pl-16"
                >
                  {/* Timeline dot */}
                  <div
                    className={`absolute left-[20px] top-1/2 -translate-y-1/2 w-3 h-3 rounded-full hidden md:block ${item.dot}`}
                    style={{ boxShadow: `0 0 10px ${item.glow}` }}
                  />

                  <div
                    className={`flex-1 border rounded-[2rem] p-6 md:p-8 flex flex-col md:flex-row gap-8 items-center ${item.color}`}
                    style={{ background: `linear-gradient(90deg, ${item.glow} 0%, transparent 100%)` }}
                  >
                    {/* Left: Icon */}
                    <div className="shrink-0 flex items-center justify-center w-20 h-20 rounded-2xl bg-black/40 border border-white/5 backdrop-blur-sm shadow-xl">
                      <Icon className="w-8 h-8" style={{ color: item.glow.replace('0.15', '1') }} />
                    </div>

                    {/* Middle: Phase Details */}
                    <div className="flex-1 text-center md:text-left">
                      <div className="flex items-center justify-center md:justify-start gap-3 mb-1">
                        <span className="text-xs font-bold tracking-widest text-white/50">{item.number}</span>
                      </div>
                      <h3 className="text-2xl font-bold mb-2">{item.phase}</h3>
                      <p className="text-sm text-ivory/60 mb-4">{item.description}</p>
                      
                      {/* Tags */}
                      <div className="flex flex-wrap items-center justify-center md:justify-start gap-2">
                        {item.tags.map((tag, tagIdx) => (
                          <div key={tagIdx} className="flex items-center gap-2">
                            <span className="text-[11px] font-medium tracking-wider text-white/40 uppercase">{tag}</span>
                            {tagIdx < item.tags.length - 1 && (
                              <div className="w-1 h-1 rounded-full bg-white/20" />
                            )}
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Right: Roles */}
                    <div className="w-full md:w-[340px] shrink-0 border-t md:border-t-0 md:border-l border-white/10 pt-6 md:pt-0 md:pl-8 flex flex-col gap-4">
                      {/* Client Role (or Designer role depending on phase, but we list both) */}
                      {/* First Role Row */}
                      <div className="flex items-start gap-4">
                        <div className="shrink-0 w-8 h-8 rounded-full bg-white/5 border border-white/10 flex items-center justify-center">
                          <User className="w-4 h-4 text-white/60" />
                        </div>
                        <div>
                          <p className="text-xs font-bold text-white/80 mb-1">
                            {item.phase === "Concept" || item.phase === "Production" || item.phase === "Delivery" ? "Designer" : "Client"}
                          </p>
                          <p className="text-xs text-white/40 leading-relaxed">
                            {item.phase === "Concept" || item.phase === "Production" || item.phase === "Delivery" ? item.designerRole : item.clientRole}
                          </p>
                        </div>
                      </div>
                      
                      {/* Second Role Row */}
                      <div className="flex items-start gap-4">
                        <div className="shrink-0 w-8 h-8 rounded-full bg-white/5 border border-white/10 flex items-center justify-center">
                          <User className="w-4 h-4 text-white/60" />
                        </div>
                        <div>
                          <p className="text-xs font-bold text-white/80 mb-1">
                            {item.phase === "Concept" || item.phase === "Production" || item.phase === "Delivery" ? "Client" : "Designer"}
                          </p>
                          <p className="text-xs text-white/40 leading-relaxed">
                            {item.phase === "Concept" || item.phase === "Production" || item.phase === "Delivery" ? item.clientRole : item.designerRole}
                          </p>
                        </div>
                      </div>
                    </div>

                  </div>
                </motion.div>
              );
            })}
          </div>
        </div>

        {/* Bottom Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* For Clients */}
          <div className="border border-purple-500/30 bg-purple-500/5 rounded-[2rem] p-8 relative overflow-hidden flex flex-col">
            <div className="absolute top-0 right-0 w-64 h-64 bg-purple-500/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2" />
            
            <div className="flex items-center gap-6 mb-6">
              <div className="w-16 h-16 rounded-2xl bg-purple-500/20 border border-purple-500/30 flex items-center justify-center shrink-0">
                <User className="w-7 h-7 text-purple-400" />
              </div>
              <div>
                <h4 className="text-sm font-bold tracking-widest text-white/80 mb-1">FOR CLIENTS</h4>
              </div>
            </div>
            
            <p className="text-sm text-white/60 leading-relaxed mb-10 flex-1">
              Share your vision, collaborate with your designer, review progress and receive your final design.
            </p>
            
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-6 border-t border-white/10">
              <div className="flex flex-col gap-2">
                <ShieldCheck className="w-5 h-5 text-purple-400" />
                <p className="text-xs text-white/50">Safe & secure payments</p>
              </div>
              <div className="flex flex-col gap-2">
                <MessageSquare className="w-5 h-5 text-purple-400" />
                <p className="text-xs text-white/50">Direct collaboration with designers</p>
              </div>
              <div className="flex flex-col gap-2">
                <Star className="w-5 h-5 text-purple-400" />
                <p className="text-xs text-white/50">Professional quality designs</p>
              </div>
            </div>
          </div>

          {/* For Designers */}
          <div className="border border-green-500/30 bg-green-500/5 rounded-[2rem] p-8 relative overflow-hidden flex flex-col">
            <div className="absolute top-0 left-0 w-64 h-64 bg-green-500/10 rounded-full blur-3xl -translate-y-1/2 -translate-x-1/2" />
            
            <div className="flex items-center gap-6 mb-6">
              <div className="w-16 h-16 rounded-2xl bg-green-500/20 border border-green-500/30 flex items-center justify-center shrink-0">
                <PenTool className="w-7 h-7 text-green-400" />
              </div>
              <div>
                <h4 className="text-sm font-bold tracking-widest text-white/80 mb-1">FOR DESIGNERS</h4>
              </div>
            </div>
            
            <p className="text-sm text-white/60 leading-relaxed mb-10 flex-1">
              Understand the brief, present your ideas, collaborate with the client and deliver professional final assets.
            </p>
            
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-6 border-t border-white/10">
              <div className="flex flex-col gap-2">
                <TrendingUp className="w-5 h-5 text-green-400" />
                <p className="text-xs text-white/50">Fair earnings & commission</p>
              </div>
              <div className="flex flex-col gap-2">
                <Users className="w-5 h-5 text-green-400" />
                <p className="text-xs text-white/50">Access to global clients</p>
              </div>
              <div className="flex flex-col gap-2">
                <Star className="w-5 h-5 text-green-400" />
                <p className="text-xs text-white/50">Build your creative portfolio</p>
              </div>
            </div>
          </div>
        </div>

      </div>
    </section>
  );
}
