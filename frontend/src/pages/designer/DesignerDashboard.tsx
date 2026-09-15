import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { projectService } from '../../api/services/project.service';
import type { Project } from '../../types/marketplace';
import { Loader2, Briefcase, Clock, CheckCircle, Search, IndianRupee } from 'lucide-react';
import Navbar from '../../components/layout/Navbar';
import { useAuth } from '../../context/AuthContext';

export default function DesignerDashboard() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    setIsLoading(true);
    try {
      const response = await projectService.getDesignerProjects();
      setProjects(response.data);
    } catch (err: any) {
      console.error(err);
      setError('Failed to load your projects.');
    } finally {
      setIsLoading(false);
    }
  };

  const activeProjects = projects.filter(p => ['ACTIVE', 'IN_REVIEW', 'DELIVERED'].includes(p.status));
  const proposedProjects = projects.filter(p => ['PROPOSAL_REVIEW', 'DESIGNER_SELECTED'].includes(p.status));
  const completedProjects = projects.filter(p => p.status === 'COMPLETED');

  // Simple revenue calculation (90% of completed budgets)
  const totalEarnings = completedProjects.reduce((sum, p) => sum + (p.budget * 0.9), 0);

  const getStatusBadge = (status: string) => {
    switch(status) {
      case 'PROPOSAL_REVIEW': return <span className="bg-indigo-500/20 text-indigo-400 px-3 py-1 rounded-full text-xs font-bold uppercase">Proposal Submitted</span>;
      case 'DESIGNER_SELECTED': return <span className="bg-yellow-500/20 text-yellow-400 px-3 py-1 rounded-full text-xs font-bold uppercase">You Were Selected</span>;
      case 'ACTIVE': return <span className="bg-accent/20 text-accent px-3 py-1 rounded-full text-xs font-bold uppercase">Active</span>;
      case 'IN_REVIEW': return <span className="bg-orange-500/20 text-orange-400 px-3 py-1 rounded-full text-xs font-bold uppercase">In Review</span>;
      case 'DELIVERED': return <span className="bg-emerald-500/20 text-emerald-400 px-3 py-1 rounded-full text-xs font-bold uppercase">Delivered</span>;
      case 'COMPLETED': return <span className="bg-emerald-500/20 text-emerald-400 px-3 py-1 rounded-full text-xs font-bold uppercase">Completed</span>;
      default: return <span className="bg-slate-500/20 text-slate-400 px-3 py-1 rounded-full text-xs font-bold uppercase">{status}</span>;
    }
  };

  return (
    <div className="min-h-screen bg-[#0D0D0F] font-sans text-[#F5F5F5]">
      <Navbar />
      
      <main className="pt-32 px-6 max-w-7xl mx-auto pb-24">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-12">
          <div>
            <h1 className="text-4xl font-display font-black tracking-tight uppercase mb-2">
              Welcome back, {user?.full_name?.split(' ')[0] || 'Designer'}
            </h1>
            <p className="text-[#9A9AA3]">Manage your active work and find new opportunities.</p>
          </div>
          <Link 
            to="/explore" 
            className="flex items-center justify-center bg-white text-black px-6 py-3 rounded-xl font-bold hover:bg-gray-200 transition-colors"
          >
            <Search className="w-5 h-5 mr-2" />
            Find Projects
          </Link>
        </div>

        {/* Dashboard Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12">
          <div className="bg-[#15151A] border border-[#2A2A32] rounded-2xl p-6">
            <div className="flex items-center text-[#9A9AA3] mb-4">
               <Briefcase className="w-5 h-5 mr-2" />
               <span className="text-sm font-bold uppercase tracking-wider">Proposals</span>
            </div>
            <p className="text-4xl font-display font-black">{proposedProjects.length}</p>
          </div>
          <div className="bg-[#15151A] border border-[#2A2A32] rounded-2xl p-6">
            <div className="flex items-center text-[#9A9AA3] mb-4">
               <Clock className="w-5 h-5 mr-2" />
               <span className="text-sm font-bold uppercase tracking-wider">Active</span>
            </div>
            <p className="text-4xl font-display font-black text-accent">{activeProjects.length}</p>
          </div>
          <div className="bg-[#15151A] border border-[#2A2A32] rounded-2xl p-6">
            <div className="flex items-center text-[#9A9AA3] mb-4">
               <CheckCircle className="w-5 h-5 mr-2 text-emerald-400" />
               <span className="text-sm font-bold uppercase tracking-wider">Completed</span>
            </div>
            <p className="text-4xl font-display font-black">{completedProjects.length}</p>
          </div>
          <div className="bg-[#15151A] border border-[#2A2A32] rounded-2xl p-6">
            <div className="flex items-center text-[#9A9AA3] mb-4">
               <IndianRupee className="w-5 h-5 mr-2 text-yellow-400" />
               <span className="text-sm font-bold uppercase tracking-wider">Earnings</span>
            </div>
            <p className="text-4xl font-display font-black text-white">₹{totalEarnings}</p>
          </div>
        </div>

        {/* Content */}
        {isLoading ? (
          <div className="flex justify-center py-20">
            <Loader2 className="animate-spin h-10 w-10 text-accent" />
          </div>
        ) : error ? (
           <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-6 rounded-2xl text-center">
             <p>{error}</p>
           </div>
        ) : projects.length === 0 ? (
          <div className="bg-[#15151A] border border-[#2A2A32] rounded-3xl p-16 text-center">
            <div className="w-20 h-20 bg-[#2A2A32] rounded-full flex items-center justify-center mx-auto mb-6">
              <Search className="w-8 h-8 text-[#9A9AA3]" />
            </div>
            <h2 className="text-2xl font-bold mb-4">No projects yet</h2>
            <p className="text-[#9A9AA3] mb-8 max-w-md mx-auto">
              Start browsing the marketplace and submit proposals to win your first client project.
            </p>
            <Link 
              to="/explore" 
              className="inline-flex items-center justify-center bg-accent text-white px-8 py-4 rounded-xl font-bold hover:bg-accent/90 transition-colors"
            >
              Explore Open Projects
            </Link>
          </div>
        ) : (
          <div className="space-y-6">
            <h2 className="text-2xl font-display font-black uppercase">My Work</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {projects.map(project => (
                <div key={project.id} className="bg-[#15151A] border border-[#2A2A32] rounded-2xl overflow-hidden flex flex-col hover:border-accent transition-colors">
                   <div className="p-6 flex-1 flex flex-col">
                     <div className="flex justify-between items-start mb-4">
                        {getStatusBadge(project.status)}
                        <span className="text-sm font-bold text-accent">₹{project.budget * 0.9} (Net)</span>
                     </div>
                     <h3 className="text-xl font-bold mb-2">{project.title}</h3>
                     <p className="text-[#9A9AA3] text-sm line-clamp-2 mb-6 flex-1">
                       {project.description}
                     </p>
                     <button
                       onClick={() => navigate(`/projects/${project.id}`)}
                       className="w-full bg-[#2A2A32] hover:bg-[#3A3A42] text-white font-bold py-3 px-4 rounded-xl transition-colors text-sm"
                     >
                       {project.status === 'DESIGNER_SELECTED' ? 'Accept Project' : 'View Project'}
                     </button>
                   </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
