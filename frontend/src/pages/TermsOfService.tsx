import { useEffect } from "react";
import { Link } from "react-router-dom";

export default function TermsOfService() {
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  return (
    <div className="bg-ivory min-h-screen">
      {/* Hero banner */}
      <div className="bg-ink text-ivory pt-36 pb-20 px-6 md:px-12">
        <div className="max-w-[860px] mx-auto">
          <p className="text-xs font-bold tracking-[0.3em] text-ivory/40 mb-6">LEGAL</p>
          <h1 className="font-display font-black text-6xl md:text-8xl tracking-tighter leading-none mb-6">
            TERMS OF
            <br />
            SERVICE
          </h1>

        </div>
      </div>

      {/* Content */}
      <div className="max-w-[860px] mx-auto px-6 md:px-12 py-20">
        <p className="text-ink/80 text-base leading-relaxed mb-6">
          Welcome to <strong className="text-ink">Lynvia</strong>. These Terms of Service
          (&quot;Terms&quot;) govern your use of the Lynvia platform, website, and services.
        </p>
        <p className="text-ink/80 text-base leading-relaxed mb-16">
          By creating an account or using Lynvia, you agree to these Terms. If you do not agree
          with these Terms, please do not use Lynvia.
        </p>

        <div className="border-t border-ink/10 mb-16" />

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
                  <p key={j} className="text-ink/75 text-sm leading-relaxed">
                    {para}
                  </p>
                )
              )}
            </div>
          </div>
        ))}

        {/* Contact box */}
        <div className="bg-ink text-ivory p-8 mt-4 mb-16">
          <h2 className="font-display font-black text-2xl tracking-tight mb-4">22. Contact Us</h2>
          <p className="text-ivory/70 text-sm leading-relaxed mb-6">
            If you have questions regarding these Terms of Service, you can contact Lynvia through
            the official contact details provided on the platform.
          </p>
          <div className="space-y-1 text-sm">
            <p className="font-bold text-ivory">Lynvia</p>
            <p className="text-ivory/60">
              Email: <span className="text-accent">[Official Email Address]</span>
            </p>
            <p className="text-ivory/60">
              Website: <span className="text-accent">[Official Website]</span>
            </p>
            <p className="text-ivory/60">
              Legal Entity: <span className="text-accent">[Legal Entity Name]</span>
            </p>
          </div>
        </div>

        {/* Acceptance note */}
        <div className="border border-accent/30 p-6 mb-10">
          <h2 className="font-display font-black text-xl tracking-tight text-ink mb-3">
            23. Acceptance of Terms
          </h2>
          <p className="text-ink/70 text-sm leading-relaxed">
            By creating an account, placing an order, accepting a project, making a payment, or
            otherwise using Lynvia, you acknowledge that you have read and agree to these Terms of
            Service.
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
    heading: "1. About Lynvia",
    paragraphs: [
      "Lynvia is an online marketplace that connects Clients who need creative design services with Designers who provide those services.",
      "Lynvia provides the platform and tools that allow Clients and Designers to discover each other, create projects, communicate, exchange files, make payments, manage deliveries, and use other marketplace features.",
      "Unless explicitly stated otherwise, Designers are independent service providers and are responsible for the services they provide.",
    ],
  },
  {
    heading: "2. Eligibility",
    paragraphs: [
      "You must be legally permitted to use Lynvia under applicable laws.",
      "By using Lynvia, you confirm that:",
      [
        "The information you provide is accurate and up to date.",
        "You are responsible for your account and account activity.",
        "You will comply with these Terms and applicable laws.",
        "You will not use Lynvia for unlawful or fraudulent purposes.",
      ],
    ],
  },
  {
    heading: "3. User Accounts",
    paragraphs: [
      "Users may create accounts as Clients or Designers.",
      "You are responsible for:",
      [
        "Providing accurate account information.",
        "Maintaining the security of your login credentials.",
        "All activity performed through your account.",
        "Notifying Lynvia if you believe your account has been accessed without authorization.",
      ],
      "You must not impersonate another person, create fraudulent accounts, or use another person's account without permission.",
    ],
  },
  {
    heading: "4. Client Responsibilities",
    paragraphs: [
      "Clients are responsible for providing accurate project information and requirements. This may include:",
      [
        "Company or brand information.",
        "Project descriptions.",
        "Design requirements.",
        "References and examples.",
        "Files and materials.",
        "Delivery expectations.",
      ],
      "Clients must have the necessary rights or permissions to provide any materials uploaded to Lynvia.",
      "Clients are responsible for reviewing project requirements and communicating necessary feedback to Designers.",
    ],
  },
  {
    heading: "5. Designer Responsibilities",
    paragraphs: [
      "Designers are responsible for the services and work they provide through Lynvia. Designers agree to:",
      [
        "Provide accurate information about their services and portfolio.",
        "Complete projects according to agreed requirements.",
        "Communicate professionally with Clients.",
        "Make reasonable efforts to meet agreed deadlines.",
        "Provide original work or appropriately licensed materials.",
        "Respect Client information and confidential materials.",
        "Comply with applicable laws and Lynvia's platform rules.",
      ],
      "Designers must not knowingly provide work that infringes another person's intellectual property rights.",
    ],
  },
  {
    heading: "6. Projects and Orders",
    paragraphs: [
      "A project or order may be created when a Client engages a Designer through Lynvia. Project details may include:",
      [
        "Requirements.",
        "Price.",
        "Deliverables.",
        "Milestones.",
        "Deadlines.",
        "Revisions.",
        "Other terms agreed between the Client and Designer.",
      ],
      "Both parties are responsible for reviewing the project details before proceeding.",
      "Changes to the original requirements may require additional time, cost, or agreement between the Client and Designer.",
    ],
  },
  {
    heading: "7. Payments",
    paragraphs: [
      "Payments made through Lynvia may be processed through third-party payment providers.",
      "Lynvia may receive information necessary to manage transactions, including payment status, transaction identifiers, amount, and currency.",
      "Payment processing may also be subject to the terms and policies of the applicable payment provider.",
    ],
  },
  {
    heading: "8. Lynvia Platform Commission",
    paragraphs: [
      "Lynvia charges a platform commission on transactions conducted through the platform.",
      "Unless otherwise clearly stated, Lynvia's platform commission is 12% of the total payment amount.",
      "The remaining 88% is allocated to the Designer, subject to applicable adjustments, refunds, disputes, payment-provider fees, taxes, and other applicable obligations.",
      "The applicable payment amount and commission may be displayed during the transaction process.",
    ],
  },
  {
    heading: "9. Designer Earnings and Withdrawals",
    paragraphs: [
      "Designer earnings may become available for withdrawal after applicable payment, project, security, and dispute checks have been completed.",
      "Lynvia may temporarily hold or restrict earnings when reasonably necessary because of:",
      [
        "Payment reversals.",
        "Disputes.",
        "Fraud or suspected abuse.",
        "Security investigations.",
        "Violations of these Terms.",
        "Legal or regulatory requirements.",
      ],
      "Additional withdrawal requirements may apply.",
    ],
  },
  {
    heading: "10. Deliveries and Revisions",
    paragraphs: [
      "Designers are expected to provide project deliverables through the applicable Lynvia workflow.",
      "Clients may request revisions according to the terms agreed for the project.",
      "Revision requests should reasonably relate to the original project requirements unless additional work is separately agreed.",
    ],
  },
  {
    heading: "11. Intellectual Property",
    paragraphs: [
      "Each user retains ownership of intellectual property they owned before using Lynvia.",
      "Client-provided materials remain the property of the Client or their respective owners.",
      "Designer-owned resources, including pre-existing templates, tools, reusable assets, fonts, stock materials, and other resources, remain subject to the Designer's or third party's rights.",
      "Ownership or licensing of final project deliverables should be agreed between the Client and Designer.",
      "Third-party materials remain subject to their applicable licenses and restrictions.",
    ],
  },
  {
    heading: "12. User Content",
    paragraphs: [
      "Users may upload content including images, logos, documents, design references, project files, messages, and deliverables.",
      "Users retain ownership of their content.",
      "By uploading content to Lynvia, you grant Lynvia the limited rights necessary to store, process, transmit, display, and otherwise use that content to operate the platform and provide requested services.",
      "This does not transfer ownership of your content to Lynvia.",
      "You are responsible for ensuring that your uploaded content does not violate applicable laws or third-party rights.",
    ],
  },
  {
    heading: "13. Prohibited Activities",
    paragraphs: [
      "Users must not use Lynvia to:",
      [
        "Commit fraud or financial abuse.",
        "Impersonate another person or organization.",
        "Infringe intellectual property rights.",
        "Upload malicious or harmful files.",
        "Harass, threaten, or abuse other users.",
        "Manipulate reviews, ratings, orders, or platform systems.",
        "Create fake transactions or accounts.",
        "Attempt unauthorized access to Lynvia systems.",
        "Conduct illegal activities.",
        "Distribute unlawful or harmful content.",
        "Circumvent Lynvia's payment or commission system.",
        "Move transactions off-platform for the purpose of avoiding applicable Lynvia fees or protections.",
      ],
      "Lynvia may investigate suspected violations and take appropriate action.",
    ],
  },
  {
    heading: "14. Communications",
    paragraphs: [
      "Lynvia may provide communication tools between Clients and Designers.",
      "Users must use these tools responsibly and must not use them for harassment, threats, fraud, spam, abuse, or illegal activities.",
      "Relevant communications and project records may be retained when reasonably necessary for platform operation, security, support, dispute resolution, or legal compliance.",
    ],
  },
  {
    heading: "15. Disputes",
    paragraphs: [
      "Lynvia may provide tools or procedures to help resolve disputes between Clients and Designers.",
      "Users may be required to provide relevant information or evidence, including project requirements, messages, files, delivery records, revision history, and payment information.",
      "Lynvia may take reasonable platform-level actions based on available evidence.",
      "Nothing in these Terms prevents a user from exercising rights available under applicable law.",
    ],
  },
  {
    heading: "16. Account Suspension and Termination",
    paragraphs: [
      "Lynvia may suspend, restrict, or terminate an account when reasonably necessary, including when a user:",
      [
        "Violates these Terms.",
        "Engages in fraud or abuse.",
        "Creates security risks.",
        "Infringes third-party rights.",
        "Attempts to bypass platform protections.",
        "Uses Lynvia unlawfully.",
      ],
      "Where appropriate, Lynvia may provide notice regarding account restrictions.",
      "Termination does not automatically remove obligations that arose before termination.",
    ],
  },
  {
    heading: "17. Platform Availability",
    paragraphs: [
      "Lynvia aims to provide a reliable platform but does not guarantee that the platform will always be available, error-free, uninterrupted, or secure against every possible threat.",
      "Lynvia may modify, suspend, or discontinue features when reasonably necessary.",
    ],
  },
  {
    heading: "18. Disclaimer",
    paragraphs: [
      "Lynvia provides the platform on an \"as available\" basis to the extent permitted by applicable law.",
      "Lynvia does not guarantee the quality, originality, suitability, or availability of services provided by independent Designers.",
      "Clients are responsible for determining whether a Designer or service is suitable for their requirements.",
    ],
  },
  {
    heading: "19. Limitation of Liability",
    paragraphs: [
      "To the maximum extent permitted by applicable law, Lynvia will not be responsible for indirect, incidental, special, consequential, or unforeseeable losses arising from the use of the platform or interactions between users.",
      "Nothing in these Terms excludes or limits liability that cannot legally be excluded or limited under applicable law.",
    ],
  },
  {
    heading: "20. Changes to the Terms",
    paragraphs: [
      "Lynvia may update these Terms from time to time.",
      "When changes are made, the Last Updated date will be changed accordingly.",
      "Where appropriate, Lynvia may provide additional notice of significant changes.",
      "Continued use of Lynvia after updated Terms become effective constitutes acceptance of the revised Terms, to the extent permitted by applicable law.",
    ],
  },
  {
    heading: "21. Governing Law",
    paragraphs: [
      "These Terms shall be governed by the applicable laws of India, subject to any mandatory rights and protections available to users under applicable law.",
      "Disputes relating to these Terms shall be handled by the appropriate courts or authorities as required by applicable law.",
    ],
  },
];
