import { useEffect } from "react";
import { Link } from "react-router-dom";

export default function About() {
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  return (
    <div className="bg-ivory min-h-screen">
      {/* Hero banner */}
      <div className="bg-ink text-ivory pt-36 pb-20 px-6 md:px-12">
        <div className="max-w-[860px] mx-auto">
          <p className="text-xs font-bold tracking-[0.3em] text-ivory/40 mb-6">COMPANY</p>
          <h1 className="font-display font-black text-6xl md:text-8xl tracking-tighter leading-none mb-6">
            ABOUT
            <br />
            LYNVIA
          </h1>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-[860px] mx-auto px-6 md:px-12 py-20">
        {sections.map((section, i) => (
          <div key={i} className="mb-14">
            <h2 className="font-display font-black text-2xl md:text-3xl tracking-tight text-ink mb-5">
              {section.heading}
            </h2>
            <div className="space-y-4">
              {section.paragraphs.map((para, j) =>
                Array.isArray(para) ? (
                  <ul key={j} className="list-none space-y-2 pl-0">
                    {para.map((item, k) => (
                      <li
                        key={k}
                        className="flex items-start gap-3 text-ink/75 text-sm leading-relaxed"
                      >
                        <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-accent flex-shrink-0" />
                        {item}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p key={j} className="text-ink/75 text-sm leading-relaxed" dangerouslySetInnerHTML={{ __html: para }} />
                )
              )}
            </div>
            {i < sections.length - 1 && (
              <div className="border-t border-ink/10 mt-14" />
            )}
          </div>
        ))}

        {/* Conclusion / CTA */}
        <div className="bg-ink text-ivory p-8 mt-16 mb-16">
          <h2 className="font-display font-black text-3xl tracking-tight mb-8">
            Why Lynvia?
          </h2>
          <p className="text-ivory/70 text-sm leading-relaxed mb-4">
            Because finding great design shouldn't be complicated.
          </p>
          <p className="text-ivory/70 text-sm leading-relaxed mb-10">
            And having great design skills shouldn't mean waiting for the right opportunity to find you.
          </p>
          
          <p className="font-bold text-ivory text-lg mb-8">Lynvia brings both sides together.</p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-10">
            <div>
              <h3 className="font-sans font-bold text-sm tracking-widest text-ivory/40 uppercase mb-2">Have an idea?</h3>
              <p className="text-accent font-bold">Bring it to Lynvia.</p>
            </div>
            <div>
              <h3 className="font-sans font-bold text-sm tracking-widest text-ivory/40 uppercase mb-2">Have the talent?</h3>
              <p className="text-accent font-bold">Build with Lynvia.</p>
            </div>
          </div>

          <p className="font-display font-black text-2xl md:text-3xl tracking-tight text-white mt-8 pt-8 border-t border-ivory/10">
            Lynvia — Where Ideas Meet Design.
          </p>
        </div>

        <div className="border-t border-ink/10 pt-8">
          <Link
            to="/"
            className="inline-flex items-center gap-2 text-xs font-bold tracking-widest text-ink border-b border-ink pb-0.5 hover:text-accent hover:border-accent transition-colors duration-200"
          >
            ← BACK TO HOME
          </Link>
        </div>
      </div>
    </div>
  );
}

const sections = [
  {
    heading: "Design That Connects Ideas With Talent",
    paragraphs: [
      "Lynvia is an India-first creative marketplace built to connect people with talented designers and make professional design more accessible.",
      "Whether you're building a personal brand, launching something new, creating content, or simply bringing an idea to life, Lynvia makes it easier to find the right creative talent for the job.",
      "At the same time, Lynvia gives designers a dedicated space to showcase their skills, connect with meaningful projects, and turn their creativity into opportunities.",
    ],
  },
  {
    heading: "Built Around Design",
    paragraphs: [
      "Unlike broad freelance platforms, Lynvia is focused on the creative design experience.",
      "We believe finding a designer should be simple, communication should be clear, and the journey from an idea to a finished design should feel effortless.",
      "From <strong>logos and branding</strong> to <strong>posters and social media designs</strong>, Lynvia brings clients and designers together through a focused, structured marketplace.",
    ],
  },
  {
    heading: "For People With Ideas",
    paragraphs: [
      "Great design shouldn't be limited to large companies or expensive agencies.",
      "Lynvia is built for:",
      [
        "Students looking to build their personal identity.",
        "Individuals bringing creative ideas to life.",
        "Creators building their personal brands.",
        "Emerging brands looking for professional visual identity.",
      ],
      "We make it easier to discover talented designers and turn your vision into something you can see, share, and be proud of.",
    ],
  },
  {
    heading: "For Designers With Talent",
    paragraphs: [
      "Talent deserves opportunity.",
      "Lynvia gives designers a platform to showcase their work, present their services, connect with clients, and build meaningful creative projects.",
      "Our goal is to create a marketplace where designers can focus on what they do best — <strong>designing</strong> — while Lynvia provides the structure around the experience.",
    ],
  },
  {
    heading: "A Better Creative Experience",
    paragraphs: [
      "We believe a creative marketplace should be more than a place to find someone who can design.",
      "It should create a better experience for everyone involved.",
      "<strong>Simple for clients.</strong><br/>Find the right creative talent without unnecessary complexity.",
      "<strong>Focused for designers.</strong><br/>Showcase your skills and reach people who are looking for what you create.",
      "<strong>Structured for projects.</strong><br/>Keep communication, requirements, files, deliveries, and project progress organized.",
      "<strong>Fair for talent.</strong><br/>Create meaningful opportunities for designers to earn from their skills.",
    ],
  },
  {
    heading: "Our Mission",
    paragraphs: [
      "Our mission is simple:",
      "<strong>Connect clients with talented designers, make professional design accessible, and help designers earn through their skills.</strong>",
      "We are building Lynvia with the belief that great design can start anywhere — with an idea, a student, a creator, or someone taking their first step toward building something of their own.",
    ],
  },
  {
    heading: "Our Vision",
    paragraphs: [
      "We envision Lynvia becoming a trusted creative marketplace where discovering talent and getting great design work done feels simple, professional, and accessible.",
      "Starting in India, we're building the foundation for a platform where <strong>ideas meet creativity, and creativity creates opportunity.</strong>",
    ],
  },
];
