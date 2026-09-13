import { Link, useNavigate, useLocation } from "react-router-dom";
import { useState, useEffect, useRef } from "react";
import { useAuth } from "../../context/AuthContext";

export default function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated, logout } = useAuth();
  const logoRef = useRef<HTMLAnchorElement>(null);

  useEffect(() => {
    let ticking = false;

    const handleScroll = () => {
      if (!ticking) {
        window.requestAnimationFrame(() => {
          updateLogoTransform();
          ticking = false;
        });
        ticking = true;
      }
    };

    const updateLogoTransform = () => {
      const logo = logoRef.current;
      const wrapper = document.getElementById("navbar-logo-wrapper");
      const placeholder = document.getElementById("footer-logo-placeholder");
      
      if (!logo || !wrapper || !placeholder) return;

      const scrollY = window.scrollY;
      const windowHeight = window.innerHeight;
      const documentHeight = document.documentElement.scrollHeight;
      
      // Calculate how close we are to the bottom.
      const distanceFromBottom = documentHeight - (scrollY + windowHeight);
      
      // We animate over the last 600px of scrolling
      const animationRange = 600;
      let progress = 0;
      if (distanceFromBottom < animationRange) {
        progress = 1 - (distanceFromBottom / animationRange);
      }
      if (progress < 0) progress = 0;
      if (progress > 1) progress = 1;

      // Ensure smooth easing (ease-in-out cubic)
      const easeProgress = progress < 0.5 ? 4 * progress * progress * progress : 1 - Math.pow(-2 * progress + 2, 3) / 2;

      const wrapperRect = wrapper.getBoundingClientRect();
      const placeholderRect = placeholder.getBoundingClientRect();

      const translateX = (placeholderRect.left - wrapperRect.left) * easeProgress;
      const translateY = (placeholderRect.top - wrapperRect.top) * easeProgress;
      
      // Start size: 3rem (48px). Target size: 4.5rem (72px) on mobile, 6rem (96px) on md+
      const startSize = 48;
      const targetSize = window.innerWidth >= 768 ? 96 : 72;
      const currentSize = startSize + (targetSize - startSize) * easeProgress;

      logo.style.transform = `translate(${translateX}px, ${translateY}px)`;
      logo.style.fontSize = `${currentSize}px`;
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    window.addEventListener("resize", handleScroll, { passive: true });
    updateLogoTransform();
    
    return () => {
      window.removeEventListener("scroll", handleScroll);
      window.removeEventListener("resize", handleScroll);
    };
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
    <header className="fixed top-0 left-0 right-0 z-50 px-6 py-6 flex justify-between items-center mix-blend-difference text-white pointer-events-none">
      <div className="pointer-events-auto">
        <div id="navbar-logo-wrapper" className="shrink-0 flex items-center">
          <Link 
            to="/" 
            ref={logoRef}
            onClick={handleLogoClick}
            className="inline-block font-display font-black tracking-tighter leading-none drop-shadow-[0_0_25px_rgba(255,255,255,1)] drop-shadow-[0_0_45px_rgba(255,255,255,0.8)] will-change-transform"
            style={{ fontSize: "48px", transformOrigin: "top left" }}
          >
            LYNVIA
          </Link>
        </div>
      </div>
      
      <nav className="hidden md:flex items-center gap-8 text-sm font-medium pointer-events-auto">
        <Link to="/explore" className="hover:opacity-70 transition-opacity">EXPLORE</Link>
        <Link to="/designers" className="hover:opacity-70 transition-opacity">FIND DESIGNERS</Link>
        <a href="#how-it-works" onClick={scrollToHowItWorks} className="hover:opacity-70 transition-opacity cursor-pointer">
          HOW IT WORKS
        </a>
      </nav>
      
      <div className="flex items-center gap-4 pointer-events-auto">
        {isAuthenticated ? (
          <>
            <Link to="/workspace" className="text-sm font-medium hover:opacity-70 transition-opacity">
              WORKSPACE
            </Link>
            <button 
              onClick={logout} 
              className="text-sm font-medium hover:opacity-70 transition-opacity uppercase"
            >
              LOGOUT
            </button>
          </>
        ) : (
          <Link to="/login" className="text-sm font-medium hover:opacity-70 transition-opacity">
            LOGIN
          </Link>
        )}
        <Link to="/start" className="text-sm font-medium border border-white/30 px-5 py-2 rounded-full hover:bg-white hover:text-black transition-colors ml-2">
          START A PROJECT
        </Link>
      </div>
    </header>
  );
}

