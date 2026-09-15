import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import Layout from "./components/layout/Layout";
import Home from "./pages/Home";
import Explore from "./pages/Explore";
import Designers from "./pages/Designers";
import PrivacyPolicy from "./pages/PrivacyPolicy";
import TermsOfService from "./pages/TermsOfService";
import About from "./pages/About";
import DesignerGuidelines from "./pages/DesignerGuidelines";
import DesignerTerms from "./pages/DesignerTerms";
import Login from "./pages/auth/Login";
import Register from "./pages/auth/Register";
import ProtectedRoute from "./components/auth/ProtectedRoute";
import ClientDashboard from "./pages/client/ClientDashboard";
import DesignerDashboard from "./pages/designer/DesignerDashboard";
import ProjectNew from "./pages/projects/ProjectNew";

function App() {
  return (
    <AuthProvider>
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
            <Route path="login" element={<Login />} />
            <Route path="register" element={<Register />} />
            
            {/* Client Routes */}
            <Route path="dashboard" element={
              <ProtectedRoute allowedRoles={['CLIENT']}>
                <ClientDashboard />
              </ProtectedRoute>
            } />
            <Route path="projects/new" element={
              <ProtectedRoute allowedRoles={['CLIENT']}>
                <ProjectNew />
              </ProtectedRoute>
            } />

            {/* Designer Routes */}
            <Route path="designer/dashboard" element={
              <ProtectedRoute allowedRoles={['DESIGNER']}>
                <DesignerDashboard />
              </ProtectedRoute>
            } />
          </Route>
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;


