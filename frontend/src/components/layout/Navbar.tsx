import { Link, useNavigate, useLocation } from "react-router-dom";
import { useState, useEffect } from "react";

export default function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const [atBottom, setAtBottom] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      const scrollY = window.scrollY;
      const windowHeight = window.innerHeight;
      const documentHeight = document.documentElement.scrollHeight;
      
      // If we are within 250px of the bottom, we consider it reaching the footer
      const isAtBottom = documentHeight - (scrollY + windowHeight) < 250;
      setAtBottom(isAtBottom);
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    // Trigger once on mount to handle initial load at bottom
    handleScroll();
    
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const scrollToHowItWorks = (e: React.MouseEvent) => {
    e.preventDefault();
    if (location.pathname === "/") {
      document.getElementById("how-it-works")?.scrollIntoView({ behavior: "smooth" });
    } else {
      navigate("/");
      setTimeout(() => {
        document.getElementById("how-it-works")?.scrollIntoView({ behavior: "smooth" });
      }, 150);
    }
  };

  const handleLogoClick = (e: React.MouseEvent) => {
    if (location.pathname === "/") {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  };

  return (
    <header className="fixed top-0 left-0 right-0 z-50 px-6 py-6 flex justify-between items-center mix-blend-difference text-white">
      <Link 
        to="/" 
        onClick={handleLogoClick}
        className={`font-display font-black text-5xl tracking-tighter leading-none transition-opacity duration-500 drop-shadow-[0_0_25px_rgba(255,255,255,1)] drop-shadow-[0_0_45px_rgba(255,255,255,0.8)] ${
          atBottom ? "opacity-0 pointer-events-none" : "opacity-100"
        }`}
      >
        LYNVIA
      </Link>
      
      <nav className="hidden md:flex items-center gap-8 text-sm font-medium">
        <Link to="/explore" className="hover:opacity-70 transition-opacity">EXPLORE</Link>
        <Link to="/designers" className="hover:opacity-70 transition-opacity">FIND DESIGNERS</Link>
        <a href="#how-it-works" onClick={scrollToHowItWorks} className="hover:opacity-70 transition-opacity cursor-pointer">
          HOW IT WORKS
        </a>
      </nav>
      
      <Link to="/start" className="text-sm font-medium border border-white/30 px-5 py-2 rounded-full hover:bg-white hover:text-black transition-colors">
        START A PROJECT
      </Link>
    </header>
  );
}

