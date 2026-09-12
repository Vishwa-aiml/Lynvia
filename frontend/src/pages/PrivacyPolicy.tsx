import { useEffect } from "react";
import { Link } from "react-router-dom";

export default function PrivacyPolicy() {
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  return (
    <div className="bg-ivory min-h-screen">
      {/* Hero banner */}
      <div className="bg-ink text-ivory pt-36 pb-20 px-6 md:px-12">
        <div className="max-w-[860px] mx-auto">
          <p className="text-xs font-bold tracking-[0.3em] text-ivory/40 mb-6">
            LEGAL
          </p>
          <h1 className="font-display font-black text-6xl md:text-8xl tracking-tighter leading-none mb-6">
            PRIVACY
            <br />
            POLICY
          </h1>

        </div>
      </div>

      {/* Content */}
      <div className="max-w-[860px] mx-auto px-6 md:px-12 py-20">

        <p className="text-ink/80 text-base leading-relaxed mb-12">
          At <strong className="text-ink">Lynvia</strong>, we respect your privacy and are committed to protecting
          the information you share with us. This Privacy Policy explains what information we collect,
          how we use it, and how we protect it when you use the Lynvia platform.
        </p>
        <p className="text-ink/80 text-base leading-relaxed mb-16">
          By using Lynvia, you acknowledge this Privacy Policy and our practices described below.
        </p>

        {/* Divider */}
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
                      <li key={k} className="flex items-start gap-3 text-ink/75 text-sm leading-relaxed">
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
        <div className="border border-ink/10 rounded-none p-8 bg-ink text-ivory mt-4 mb-16">
          <h2 className="font-display font-black text-2xl tracking-tight mb-4">14. Contact Us</h2>
          <p className="text-ivory/70 text-sm leading-relaxed mb-6">
            If you have questions, concerns, or requests regarding this Privacy Policy or your
            personal information, please contact us:
          </p>
          <div className="space-y-1 text-sm">
            <p className="font-bold text-ivory">Lynvia</p>
            <p className="text-ivory/60">Email: <span className="text-accent">[your official email address]</span></p>
            <p className="text-ivory/60">Website: <span className="text-accent">[your Lynvia website]</span></p>
            <p className="text-ivory/60">Legal Entity: <span className="text-accent">[your legal entity name]</span></p>
          </div>
        </div>

        <div className="border-t border-ink/10 pt-8">
          <p className="text-ink/50 text-xs leading-relaxed">
            By using Lynvia, you acknowledge that you have read and understood this Privacy Policy.
          </p>
          <Link
            to="/"
            className="inline-flex items-center gap-2 mt-8 text-xs font-bold tracking-widest text-ink border-b border-ink pb-0.5 hover:text-accent hover:border-accent transition-colors duration-200"
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
    heading: "1. Information We Collect",
    paragraphs: [
      "When you use Lynvia, we may collect information such as:",
      [
        "Your name and email address",
        "Profile information and profile image",
        "Account type, such as Client or Designer",
        "Company name and company type",
        "Project requirements and descriptions",
        "Portfolio and service information",
        "Files, images, and other materials uploaded to projects",
        "Messages between Clients and Designers",
        "Payment and transaction information",
        "Information about your use of the Lynvia platform",
      ],
      "When you sign in using services such as Google, we may receive basic account information provided by that service, such as your name, email address, and profile image.",
    ],
  },
  {
    heading: "2. How We Use Your Information",
    paragraphs: [
      "We use your information to:",
      [
        "Create and manage your Lynvia account",
        "Connect Clients with Designers",
        "Facilitate design projects and orders",
        "Enable communication between Clients and Designers",
        "Process payments, refunds, and transactions",
        "Manage Designer earnings and payouts",
        "Provide customer support",
        "Prevent fraud, abuse, and unauthorized activity",
        "Improve the functionality and experience of Lynvia",
        "Send important account, project, payment, and service notifications",
      ],
      "We only use information for purposes that are reasonably necessary to operate and improve Lynvia and as otherwise permitted by applicable law.",
    ],
  },
  {
    heading: "3. Information Shared With Other Users",
    paragraphs: [
      "Because Lynvia is a marketplace, certain information may be shared between Clients and Designers when necessary to complete a project.",
      "For example, a Designer may receive the project requirements and files necessary to complete a Client's order.",
      "Similarly, Clients may see relevant Designer information such as a Designer's profile, portfolio, services, and project-related communications.",
      "We encourage users not to share unnecessary personal or confidential information through project messages or uploads.",
    ],
  },
  {
    heading: "4. Payments",
    paragraphs: [
      "Payments made through Lynvia may be processed by third-party payment providers.",
      "Lynvia may receive transaction-related information such as payment status, transaction identifiers, amount, and currency.",
      "Payment providers may independently process payment information according to their own privacy policies and terms.",
      "Lynvia does not intentionally store complete payment-card details when those details are processed directly by our payment provider.",
    ],
  },
  {
    heading: "5. Files and Uploaded Content",
    paragraphs: [
      "Lynvia allows users to upload files and creative materials required for projects.",
      "Uploaded content may include logos, images, documents, references, brand materials, and design deliverables.",
      "We use these materials to provide project services, facilitate communication, maintain project records, and resolve disputes when necessary.",
      "You are responsible for ensuring that you have the necessary rights and permissions to upload content to Lynvia.",
    ],
  },
  {
    heading: "6. Cookies and Technical Information",
    paragraphs: [
      "We may use cookies and similar technologies to:",
      [
        "Keep you signed in",
        "Maintain secure sessions",
        "Remember preferences",
        "Improve website performance",
        "Understand how users interact with Lynvia",
        "Detect and prevent security issues",
      ],
      "We may also automatically collect limited technical information such as your browser type, device information, IP address, and activity logs.",
    ],
  },
  {
    heading: "7. Third-Party Services",
    paragraphs: [
      "Lynvia may use trusted third-party services for purposes such as:",
      [
        "Authentication",
        "Payment processing",
        "Cloud hosting",
        "File storage",
        "Email and notifications",
        "Security and analytics",
      ],
      "These services may process information as necessary to provide their services. Their own privacy policies may also apply.",
    ],
  },
  {
    heading: "8. Data Security",
    paragraphs: [
      "We take reasonable measures to protect your information from unauthorized access, loss, misuse, alteration, or disclosure.",
      "However, no online service can guarantee complete security. We encourage you to use a strong password and keep your account credentials confidential.",
    ],
  },
  {
    heading: "9. Data Retention",
    paragraphs: [
      "We retain information for as long as reasonably necessary to provide our services, maintain accounts and transactions, resolve disputes, prevent fraud, comply with legal obligations, and protect the security of Lynvia.",
      "When information is no longer required, we may delete or anonymize it where appropriate and permitted by applicable law.",
    ],
  },
  {
    heading: "10. Your Rights",
    paragraphs: [
      "Depending on applicable law, you may have rights relating to your personal information, including the ability to:",
      [
        "Request access to your information",
        "Request correction of inaccurate information",
        "Request deletion where applicable",
        "Withdraw consent where applicable",
        "Raise a privacy-related complaint or grievance",
      ],
      "To make a privacy request, please contact us using the details below.",
    ],
  },
  {
    heading: "11. Account Deletion",
    paragraphs: [
      "You may request deletion of your Lynvia account through the available account settings or by contacting us.",
      "Some information may need to be retained after account deletion where required by law or reasonably necessary for security, fraud prevention, financial records, or dispute resolution.",
    ],
  },
  {
    heading: "12. Children's Privacy",
    paragraphs: [
      "Lynvia is not intended for individuals who are not legally permitted to use the Platform under applicable law.",
      "We do not knowingly collect personal information from children in violation of applicable legal requirements.",
    ],
  },
  {
    heading: "13. Changes to This Privacy Policy",
    paragraphs: [
      "We may update this Privacy Policy from time to time as Lynvia, our services, or applicable laws change.",
      "When we make significant changes, we may update the \"Last Updated\" date and provide additional notice where appropriate.",
    ],
  },
];
