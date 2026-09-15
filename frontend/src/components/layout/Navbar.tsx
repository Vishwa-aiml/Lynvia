import { Link, useNavigate, useLocation } from "react-router-dom";
import { useEffect, useRef } from "react";
import { useAuth } from "../../context/AuthContext";

export default function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated, user, logout } = useAuth();
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
    <header className="fixed top-0 left-0 right-0 z-50 transition-all duration-300 pointer-events-none">
      {/* Smudged glass backdrop */}
      <div 
        className="absolute inset-x-0 top-0 h-[120px] bg-black/50 backdrop-blur-lg pointer-events-none -z-10"
        style={{
          maskImage: "linear-gradient(to bottom, black 40%, transparent 100%)",
          WebkitMaskImage: "linear-gradient(to bottom, black 40%, transparent 100%)",
        }}
      />
      
      {/* Navbar Content */}
      <div className="relative px-6 py-6 flex justify-between items-center text-white pointer-events-auto">
        <div>
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
        
        <nav className="hidden md:flex items-center gap-8 text-sm font-medium">
          <Link to="/explore" className="hover:opacity-70 transition-opacity">EXPLORE</Link>
          <Link to="/designers" className="hover:opacity-70 transition-opacity">FIND DESIGNERS</Link>
          <a href="#how-it-works" onClick={scrollToHowItWorks} className="hover:opacity-70 transition-opacity cursor-pointer">
            HOW IT WORKS
          </a>
        </nav>
        
        <div className="flex items-center gap-4">
          {isAuthenticated ? (
            <div className="relative group">
              <button className="flex items-center gap-2 hover:opacity-80 transition-opacity focus:outline-none">
                <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-violet-500 to-fuchsia-500 flex items-center justify-center text-white font-bold text-sm shadow-md border-2 border-white/20">
                  {/* Assuming user is available via useAuth, but if not we can just show a default icon. We should fetch user from useAuth */}
                  <span className="uppercase">{user?.full_name?.charAt(0) || user?.email?.charAt(0) || 'U'}</span>
                </div>
              </button>
              
              {/* Dropdown Menu */}
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-xl shadow-xl border border-slate-100 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 transform origin-top-right scale-95 group-hover:scale-100">
                <div className="p-2">
                  <div className="px-3 py-2 border-b border-slate-100 mb-2">
                    <p className="text-sm font-bold text-slate-800 truncate">{user?.full_name || 'User'}</p>
                    <p className="text-xs text-slate-500 truncate">{user?.email}</p>
                  </div>
                  <Link to="/dashboard" className="block px-3 py-2 text-sm text-slate-700 hover:bg-slate-50 rounded-lg font-medium transition-colors">
                    Dashboard
                  </Link>
                  <button 
                    onClick={logout} 
                    className="w-full text-left px-3 py-2 text-sm text-rose-600 hover:bg-rose-50 rounded-lg font-medium transition-colors mt-1"
                  >
                    Logout
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <Link to="/login" className="text-sm font-medium hover:opacity-70 transition-opacity">
              LOGIN
            </Link>
          )}
          <Link to="/projects/new" className="text-sm font-medium border border-white/30 px-5 py-2 rounded-full hover:bg-accent hover:border-accent hover:text-white active:scale-95 transition-all duration-300 ml-2 shadow-[0_0_0_0_rgba(168,85,247,0)] hover:shadow-[0_0_15px_rgba(168,85,247,0.5)]">
            START A PROJECT
          </Link>
        </div>
      </div>
    </header>
  );
}

