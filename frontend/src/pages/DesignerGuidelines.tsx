import { useEffect } from "react";
import { Link } from "react-router-dom";

export default function DesignerGuidelines() {
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  return (
    <div className="bg-ivory min-h-screen">
      {/* Hero banner */}
      <div className="bg-ink text-ivory pt-36 pb-20 px-6 md:px-12">
        <div className="max-w-[860px] mx-auto">
          <p className="text-xs font-bold tracking-[0.3em] text-ivory/40 mb-6">
            FOR DESIGNERS
          </p>
          <h1 className="font-display font-black text-6xl md:text-8xl tracking-tighter leading-none mb-6">
            DESIGNER
            <br />
            GUIDELINES
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
            <div className="space-y-6">
              {section.content.map((block, j) => {
                if (block.type === "text") {
                  return (
                    <p
                      key={j}
                      className="text-ink/75 text-sm leading-relaxed"
                      dangerouslySetInnerHTML={{ __html: block.text }}
                    />
                  );
                }
                if (block.type === "list") {
                  return (
                    <div key={j}>
                      {block.title && (
                        <h3 className="font-bold text-ink mb-3">{block.title}</h3>
                      )}
                      <ul className="list-none space-y-2 pl-0">
                        {block.items.map((item, k) => (
                          <li
                            key={k}
                            className="flex items-start gap-3 text-ink/75 text-sm leading-relaxed"
                          >
                            <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-accent flex-shrink-0" />
                            {item}
                          </li>
                        ))}
                      </ul>
                    </div>
                  );
                }
                return null;
              })}
            </div>
            {i < sections.length - 1 && (
              <div className="border-t border-ink/10 mt-14" />
            )}
          </div>
        ))}

        {/* Contact box */}
        <div className="bg-ink text-ivory p-8 mt-16 mb-16">
          <h2 className="font-display font-black text-2xl tracking-tight mb-4">Contact</h2>
          <p className="text-ivory/70 text-sm leading-relaxed mb-6">
            For questions regarding these guidelines, contact Lynvia through the official contact channel provided on the platform.
          </p>
          <div className="space-y-1 text-sm">
            <p className="font-bold text-ivory">Lynvia</p>
            <p className="text-ivory/60 mb-4">India</p>
            <p className="text-ivory/60">Contact: <span className="text-accent">[Official Email]</span></p>
            <p className="text-ivory/60">Website: <span className="text-accent">[Official Website]</span></p>
          </div>
        </div>

        {/* Important note */}
        <div className="border border-accent/30 p-6 mb-10">
          <h2 className="font-display font-black text-xl tracking-tight text-ink mb-3">
            Important
          </h2>
          <p className="text-ink/70 text-sm leading-relaxed mb-4">
            These Designer Guidelines are intended to explain marketplace expectations and should be read together with Lynvia's <strong>Terms of Service</strong>, <strong>Privacy Policy</strong>, and other applicable policies.
          </p>
          <p className="text-ink/70 text-sm leading-relaxed">
            They are not a substitute for legal advice and should be reviewed before commercial launch to ensure they match Lynvia's actual business model and applicable Indian law.
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

type Block = 
  | { type: "text"; text: string }
  | { type: "list"; title?: string; items: string[] };

type Section = {
  heading: string;
  content: Block[];
};

const sections: Section[] = [
  {
    heading: "1. Welcome to Lynvia",
    content: [
      { type: "text", text: "Lynvia is an India-first creative marketplace built to connect clients with talented designers." },
      { type: "text", text: "Our goal is simple: give designers a professional place to showcase their skills, work with clients, and turn creativity into meaningful opportunities." },
      { type: "text", text: "By becoming a Lynvia designer, you agree to maintain a professional, respectful, and reliable experience for every client." },
    ]
  },
  {
    heading: "2. Your Designer Profile",
    content: [
      { type: "text", text: "Your profile represents you professionally on Lynvia." },
      { type: "text", text: "Please ensure that your:" },
      { type: "list", items: [
        "Name and profile information are accurate.",
        "Profile picture represents you appropriately.",
        "Skills and specializations are genuine.",
        "Experience and qualifications are not misleading.",
        "Services and pricing are clearly described.",
        "Portfolio contains work you are permitted to display.",
      ]},
      { type: "text", text: "Do not impersonate another designer or create misleading credentials." },
    ]
  },
  {
    heading: "3. Portfolio Guidelines",
    content: [
      { type: "text", text: "Your portfolio should demonstrate your actual design abilities." },
      { type: "list", title: "You should:", items: [
        "Upload your own original work or work you have permission to display.",
        "Clearly identify collaborative or team work where appropriate.",
        "Use high-quality images.",
        "Provide accurate descriptions.",
        "Keep your portfolio relevant to the services you offer.",
      ]},
      { type: "list", title: "You must not:", items: [
        "Upload another person's work and claim it as your own.",
        "Upload stolen or unauthorized designs.",
        "Use copyrighted material without appropriate rights or licenses.",
        "Misrepresent client work, employment, awards, or experience.",
      ]},
      { type: "text", text: "Lynvia may remove portfolio content that violates these guidelines." },
    ]
  },
  {
    heading: "4. Creating Services",
    content: [
      { type: "text", text: "When creating a service, clearly explain:" },
      { type: "list", items: [
        "What you are offering.",
        "What the client will receive.",
        "Number of initial concepts or variations, if applicable.",
        "Number of revisions included.",
        "Expected delivery time.",
        "Final file formats.",
        "Price and any additional conditions.",
      ]},
      { type: "text", text: "Avoid vague promises such as \"unlimited everything\" unless you genuinely intend to provide it." },
      { type: "text", text: "Your service description should allow a client to understand exactly what they are purchasing." },
    ]
  },
  {
    heading: "5. Accepting Projects",
    content: [
      { type: "text", text: "Only accept projects that you can reasonably complete." },
      { type: "text", text: "Before accepting a project, make sure you understand:" },
      { type: "list", items: [
        "Client requirements.",
        "Expected deliverables.",
        "Deadline.",
        "Number of revisions.",
        "Agreed price.",
        "Required file formats.",
        "Any special project conditions.",
      ]},
      { type: "text", text: "If the requirements are unclear, communicate with the client before beginning the work." },
      { type: "text", text: "Do not accept multiple projects if doing so would prevent you from meeting your commitments." },
    ]
  },
  {
    heading: "6. Communication",
    content: [
      { type: "text", text: "Professional communication is expected throughout every project." },
      { type: "list", title: "Designers should:", items: [
        "Respond reasonably promptly.",
        "Ask questions when requirements are unclear.",
        "Provide appropriate progress updates.",
        "Communicate delays as early as possible.",
        "Keep discussions related to the project professional.",
      ]},
      { type: "list", title: "Do not:", items: [
        "Harass or threaten clients.",
        "Use abusive or discriminatory language.",
        "Spam clients.",
        "Manipulate reviews or ratings.",
        "Pressure clients into unnecessary purchases.",
        "Share private client information.",
      ]},
    ]
  },
  {
    heading: "7. Deadlines",
    content: [
      { type: "text", text: "Deadlines matter." },
      { type: "text", text: "Once you accept a project, you are responsible for making a reasonable effort to deliver on time." },
      { type: "text", text: "If you expect a delay:" },
      { type: "list", items: [
        "Inform the client as soon as possible.",
        "Explain the reason clearly.",
        "Provide a realistic revised timeline.",
        "Continue communication until the issue is resolved.",
      ]},
      { type: "text", text: "Repeated failure to meet deadlines may affect your account, project eligibility, or designer standing on Lynvia." },
    ]
  },
  {
    heading: "8. Design Quality",
    content: [
      { type: "text", text: "Designers are expected to deliver work that reasonably matches the agreed project requirements." },
      { type: "text", text: "Before delivery, check:" },
      { type: "list", items: [
        "Spelling and grammar.",
        "Dimensions.",
        "Resolution.",
        "File formats.",
        "Brand colors and typography.",
        "Required elements.",
        "Overall visual quality.",
      ]},
      { type: "text", text: "Do not intentionally submit incomplete, corrupted, blank, or unusable deliverables." },
    ]
  },
  {
    heading: "9. Revisions",
    content: [
      { type: "text", text: "Revisions should remain reasonably connected to the original project requirements." },
      { type: "text", text: "If revisions are included in the agreed project, complete them according to the agreed scope." },
      { type: "text", text: "A request that substantially changes the original project may require:" },
      { type: "list", items: [
        "Additional time.",
        "Additional payment.",
        "A new project or revised agreement.",
      ]},
      { type: "text", text: "Communicate with the client before performing substantial additional work." },
    ]
  },
  {
    heading: "10. Originality and Intellectual Property",
    content: [
      { type: "text", text: "Designers must respect intellectual property rights." },
      { type: "text", text: "You are responsible for ensuring that the work you deliver does not knowingly infringe another person's intellectual property rights." },
      { type: "text", text: "This includes unauthorized use of:" },
      { type: "list", items: [
        "Logos.",
        "Illustrations.",
        "Stock assets.",
        "Fonts.",
        "Photographs.",
        "Templates.",
        "AI-generated assets with incompatible licensing conditions.",
        "Other copyrighted or protected materials.",
      ]},
      { type: "text", text: "Where third-party assets are used, the applicable license or usage rights must permit their intended use." },
      { type: "text", text: "Ownership or licensing of the final deliverable should follow the agreement between the client and designer." },
    ]
  },
  {
    heading: "11. Client Materials",
    content: [
      { type: "text", text: "Clients may provide:" },
      { type: "list", items: [
        "Logos.",
        "Images.",
        "Brand assets.",
        "Text.",
        "Product information.",
        "Documents.",
        "Other project materials.",
      ]},
      { type: "text", text: "Use these materials only for legitimate project purposes." },
      { type: "text", text: "Do not publish, sell, distribute, or reuse confidential client materials without appropriate permission." },
    ]
  },
  {
    heading: "12. Confidentiality",
    content: [
      { type: "text", text: "Some projects may contain confidential information." },
      { type: "text", text: "Designers should treat client business information, unreleased products, campaign materials, personal information, and other confidential project information responsibly." },
      { type: "text", text: "Do not publicly share confidential work before the client permits you to do so." },
      { type: "text", text: "If you want to display completed work in your portfolio, obtain appropriate permission when the project or agreement requires it." },
    ]
  },
  {
    heading: "13. Payments and Lynvia Commission",
    content: [
      { type: "text", text: "All project payments should be handled through the Lynvia platform where applicable." },
      { type: "text", text: "Lynvia's platform commission is <strong>12% of the total payment</strong>, with the remaining <strong>88% allocated to the designer</strong>, subject to applicable refunds, disputes, payment-provider fees, taxes, adjustments, and other applicable obligations." },
      { type: "text", text: "Designers must not attempt to bypass Lynvia's payment system or move platform transactions off-platform solely to avoid applicable fees or protections." },
      { type: "text", text: "Earnings may be temporarily held when required for refunds, disputes, fraud prevention, security checks, payment reversals, or other legitimate reasons." },
    ]
  },
  {
    heading: "14. Deliveries",
    content: [
      { type: "text", text: "Final work should be delivered through the designated Lynvia project workflow whenever applicable." },
      { type: "text", text: "Deliverables should:" },
      { type: "list", items: [
        "Match the agreed scope.",
        "Be accessible to the client.",
        "Use the agreed file formats.",
        "Be properly named and organized where appropriate.",
        "Be of reasonable quality.",
      ]},
      { type: "text", text: "Do not intentionally deliver files that are unusable or materially different from what was agreed." },
    ]
  },
  {
    heading: "15. Ratings and Reviews",
    content: [
      { type: "text", text: "Reviews should reflect genuine project experiences." },
      { type: "text", text: "Designers must not:" },
      { type: "list", items: [
        "Create fake reviews.",
        "Ask friends to create fake projects or reviews.",
        "Manipulate ratings.",
        "Threaten clients over negative reviews.",
        "Offer improper incentives in exchange for positive reviews.",
      ]},
      { type: "text", text: "A professional response to criticism is expected." },
    ]
  },
  {
    heading: "16. Prohibited Activities",
    content: [
      { type: "text", text: "Designers must not use Lynvia for:" },
      { type: "list", items: [
        "Fraud or scams.",
        "Impersonation.",
        "Copyright or trademark infringement.",
        "Uploading malicious files.",
        "Unauthorized access to accounts or systems.",
        "Harassment or threats.",
        "Fake transactions.",
        "Fake portfolios or credentials.",
        "Payment manipulation.",
        "Circumventing Lynvia's platform fees or protections.",
        "Illegal activities.",
        "Any activity that compromises the safety or integrity of Lynvia or its users.",
      ]},
    ]
  },
  {
    heading: "17. Use of AI Tools",
    content: [
      { type: "text", text: "Designers may use AI-assisted design tools where appropriate, provided that:" },
      { type: "list", items: [
        "The resulting work complies with the agreed project requirements.",
        "The designer has the necessary rights to use the generated or incorporated material.",
        "The use of AI does not knowingly infringe third-party rights.",
        "The designer does not falsely represent AI-generated work as entirely human-created where disclosure is required by the project or applicable law.",
        "Confidential client information is not entered into third-party AI services in a manner that violates the client's requirements or applicable privacy obligations.",
      ]},
      { type: "text", text: "The designer remains responsible for the final deliverable." },
    ]
  },
  {
    heading: "18. Professional Conduct",
    content: [
      { type: "text", text: "Lynvia is intended to be a professional creative community." },
      { type: "text", text: "Treat clients and other designers with:" },
      { type: "list", items: [
        "Respect.",
        "Honesty.",
        "Professionalism.",
        "Fairness.",
        "Clear communication.",
      ]},
      { type: "text", text: "Disagreements should be handled through communication and Lynvia's available dispute mechanisms rather than harassment or retaliation." },
    ]
  },
  {
    heading: "19. Disputes",
    content: [
      { type: "text", text: "If a disagreement occurs, designers should first attempt to resolve the issue professionally with the client." },
      { type: "text", text: "Where available, Lynvia may provide dispute-resolution tools and may request:" },
      { type: "list", items: [
        "Project requirements.",
        "Messages.",
        "Deliverables.",
        "Payment information.",
        "Revision history.",
        "Other relevant evidence.",
      ]},
      { type: "text", text: "Lynvia may take reasonable platform-level action based on the available information and applicable policies." },
    ]
  },
  {
    heading: "20. Account Standing",
    content: [
      { type: "text", text: "Lynvia may review designer accounts for quality, safety, fraud, policy compliance, and marketplace integrity." },
      { type: "text", text: "Repeated or serious violations may result in:" },
      { type: "list", items: [
        "Removal of content.",
        "Restrictions on accepting projects.",
        "Temporary suspension.",
        "Payment or earnings holds where permitted and necessary.",
        "Account termination.",
      ]},
      { type: "text", text: "Actions will depend on the nature and seriousness of the issue." },
    ]
  },
  {
    heading: "21. Keeping Your Account Secure",
    content: [
      { type: "text", text: "You are responsible for protecting your account credentials." },
      { type: "text", text: "Do not:" },
      { type: "list", items: [
        "Share your password.",
        "Give another person access to your account.",
        "Allow another person to operate your designer account without authorization.",
        "Ignore suspicious account activity.",
      ]},
      { type: "text", text: "Contact Lynvia if you believe your account has been compromised." },
    ]
  },
  {
    heading: "22. Updating These Guidelines",
    content: [
      { type: "text", text: "Lynvia may update these Designer Guidelines as the platform, services, technology, or applicable requirements evolve." },
      { type: "text", text: "The latest version will be made available through the Lynvia website." },
      { type: "text", text: "Designers are expected to follow the guidelines applicable to their use of the platform." },
    ]
  },
  {
    heading: "23. Our Standard",
    content: [
      { type: "text", text: "The principle behind Lynvia is simple:" },
      { type: "text", text: "<strong>Do great work.<br/>Communicate clearly.<br/>Respect your clients.<br/>Respect other creators.<br/>Deliver what you promise.</strong>" },
      { type: "text", text: "We want Lynvia to be a place where designers can build their reputation through the quality of their work—not through shortcuts." },
    ]
  },
];
