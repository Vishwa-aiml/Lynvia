import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Layout from "./components/layout/Layout";
import Home from "./pages/Home";
import Explore from "./pages/Explore";
import Designers from "./pages/Designers";
import PrivacyPolicy from "./pages/PrivacyPolicy";
import TermsOfService from "./pages/TermsOfService";
import About from "./pages/About";
import DesignerGuidelines from "./pages/DesignerGuidelines";
import DesignerTerms from "./pages/DesignerTerms";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="explore" element={<Explore />} />
          <Route path="designers" element={<Designers />} />
          <Route path="privacy" element={<PrivacyPolicy />} />
          <Route path="terms" element={<TermsOfService />} />
          <Route path="about" element={<About />} />
          <Route path="designer-guidelines" element={<DesignerGuidelines />} />
          <Route path="designer-terms" element={<DesignerTerms />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;


