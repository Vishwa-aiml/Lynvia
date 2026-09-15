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
import DesignerProfile from "./pages/DesignerProfile";
import ProjectNew from "./pages/projects/ProjectNew";
import ProjectWorkspace from "./pages/projects/ProjectWorkspace";
import ProtectedRoute from "./components/auth/ProtectedRoute";
import ClientDashboard from "./pages/client/ClientDashboard";
import DesignerDashboard from "./pages/designer/DesignerDashboard";
import Settings from "./pages/Settings";
import Earnings from "./pages/Earnings";
import Messages from "./pages/Messages";
import Notifications from "./pages/Notifications";
import Disputes from "./pages/Disputes";

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Home />} />
            <Route path="explore" element={<Explore />} />
            <Route path="designers" element={<Designers />} />
            <Route path="designers/:designerId" element={<DesignerProfile />} />
            <Route path="privacy" element={<PrivacyPolicy />} />
            <Route path="terms" element={<TermsOfService />} />
            <Route path="about" element={<About />} />
            <Route path="designer-guidelines" element={<DesignerGuidelines />} />
            <Route path="designer-terms" element={<DesignerTerms />} />
            <Route path="login" element={<Login />} />
            <Route path="register" element={<Register />} />
            
            {/* Shared Protected Routes */}
            <Route path="settings" element={
              <ProtectedRoute allowedRoles={['CLIENT', 'DESIGNER']}>
                <Settings />
              </ProtectedRoute>
            } />
            <Route path="messages" element={
              <ProtectedRoute allowedRoles={['CLIENT', 'DESIGNER']}>
                <Messages />
              </ProtectedRoute>
            } />
            <Route path="notifications" element={
              <ProtectedRoute allowedRoles={['CLIENT', 'DESIGNER']}>
                <Notifications />
              </ProtectedRoute>
            } />
            <Route path="disputes" element={
              <ProtectedRoute allowedRoles={['CLIENT', 'DESIGNER']}>
                <Disputes />
              </ProtectedRoute>
            } />

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
            <Route path="projects/:projectId" element={
              <ProtectedRoute allowedRoles={['CLIENT', 'DESIGNER']}>
                <ProjectWorkspace />
              </ProtectedRoute>
            } />

            {/* Designer Routes */}
            <Route path="designer/dashboard" element={
              <ProtectedRoute allowedRoles={['DESIGNER']}>
                <DesignerDashboard />
              </ProtectedRoute>
            } />
            <Route path="earnings" element={
              <ProtectedRoute allowedRoles={['DESIGNER']}>
                <Earnings />
              </ProtectedRoute>
            } />
          </Route>
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;


