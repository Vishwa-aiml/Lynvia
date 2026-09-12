import { useEffect } from "react";
import { Link } from "react-router-dom";

export default function DesignerTerms() {
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
            TERMS
          </h1>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-[860px] mx-auto px-6 md:px-12 py-20">
        <p className="text-ink/80 text-base leading-relaxed mb-16">
          By joining Lynvia as a Designer, you agree to the following terms.
        </p>

        <div className="border-t border-ink/10 mb-16" />

        {sections.map((section, i) => (
          <div key={i} className="mb-14">
            <h2 className="font-display font-black text-2xl md:text-3xl tracking-tight text-ink mb-5">
              {section.heading}
            </h2>
            <div className="space-y-4">
              {section.paragraphs.map((para, j) => (
                <p key={j} className="text-ink/75 text-sm leading-relaxed" dangerouslySetInnerHTML={{ __html: para }} />
              ))}
            </div>
          </div>
        ))}

        {/* Contact box */}
        <div className="bg-ink text-ivory p-8 mt-4 mb-16">
          <h2 className="font-display font-black text-2xl tracking-tight mb-4">15. Acceptance</h2>
          <p className="text-ivory/70 text-sm leading-relaxed mb-6">
            By registering or continuing to use Lynvia as a Designer, you confirm that you have read and agree to these Designer Terms.
          </p>
          <div className="space-y-1 text-sm">
            <p className="font-bold text-ivory">Lynvia</p>
            <p className="text-ivory/60">
              Email: <span className="text-accent">[Official Email]</span>
            </p>
            <p className="text-ivory/60">
              Website: <span className="text-accent">[Official Website]</span>
            </p>
          </div>
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
    heading: "1. Designer Account",
    paragraphs: [
      "You must provide accurate information and keep your account secure. You are responsible for all activity under your account."
    ],
  },
  {
    heading: "2. Professional Services",
    paragraphs: [
      "You agree to provide the services you offer professionally and according to the project requirements, agreed price, deliverables, and deadline."
    ],
  },
  {
    heading: "3. Original Work",
    paragraphs: [
      "You must have the necessary rights to all work, images, fonts, templates, and other assets you use. You must not submit stolen, copied, or unauthorized work."
    ],
  },
  {
    heading: "4. Client Communication",
    paragraphs: [
      "You must communicate respectfully and professionally with Clients. Harassment, fraud, misleading information, or abusive behaviour is not permitted."
    ],
  },
  {
    heading: "5. Payments",
    paragraphs: [
      "All project payments must be processed through Lynvia where applicable.",
      "Lynvia's platform commission is <strong>12% of the total payment</strong>, and the remaining <strong>88% is allocated to the Designer</strong>, subject to applicable refunds, disputes, payment-provider fees, taxes, reversals, and other adjustments."
    ],
  },
  {
    heading: "6. Designer Earnings",
    paragraphs: [
      "Designer earnings may remain pending until the applicable project, payment, refund, dispute, or verification process is completed. Withdrawals are subject to Lynvia's payout requirements."
    ],
  },
  {
    heading: "7. Intellectual Property",
    paragraphs: [
      "Ownership or licensing of the final design should follow the agreement between the Client and Designer. You must respect Client-owned materials and third-party intellectual-property rights."
    ],
  },
  {
    heading: "8. Confidentiality",
    paragraphs: [
      "You must keep Client information, files, and unreleased work confidential and use them only for legitimate project purposes."
    ],
  },
  {
    heading: "9. Off-Platform Transactions",
    paragraphs: [
      "You must not move Lynvia projects or payments outside the platform to intentionally avoid Lynvia's applicable fees, protections, or processes."
    ],
  },
  {
    heading: "10. Prohibited Activities",
    paragraphs: [
      "Fraud, fake accounts, fake reviews, plagiarism, intellectual-property infringement, payment manipulation, malicious files, unauthorized access, and other unlawful or abusive activities are prohibited."
    ],
  },
  {
    heading: "11. Disputes",
    paragraphs: [
      "You agree to cooperate with Lynvia's dispute-resolution process and provide relevant project information when reasonably requested."
    ],
  },
  {
    heading: "12. Suspension or Termination",
    paragraphs: [
      "Lynvia may suspend or terminate a Designer account for serious or repeated violations of these Terms, Lynvia's Designer Guidelines, or other applicable policies."
    ],
  },
  {
    heading: "13. Changes",
    paragraphs: [
      "Lynvia may update these Terms when necessary. Updated Terms will be made available on the platform."
    ],
  },
  {
    heading: "14. Governing Law",
    paragraphs: [
      "These Terms are governed by the laws of India, subject to applicable law."
    ],
  },
];
