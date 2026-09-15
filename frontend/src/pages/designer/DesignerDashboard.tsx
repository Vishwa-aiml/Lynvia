import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { projectService } from '../../api/services/project.service';
import type { Project } from '../../types/marketplace';
import { Loader2, Briefcase, Clock, CheckCircle, Search, IndianRupee, Sparkles, ArrowRight } from 'lucide-react';
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
  const totalEarnings = completedProjects.reduce((sum, p) => sum + ((p.budget || 0) * 0.9), 0);

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
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-12"
        >
          <div>
            <h1 className="text-4xl font-display font-black tracking-tight uppercase mb-2">
              Welcome back, {user?.full_name?.split(' ')[0] || 'Designer'}
            </h1>
            <p className="text-[#9A9AA3]">Manage your active work and find new opportunities.</p>
          </div>
          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
            <Link 
              to="/explore" 
              className="flex items-center justify-center bg-white text-black px-6 py-3 rounded-xl font-bold hover:bg-gray-200 transition-colors shadow-[0_0_20px_rgba(255,255,255,0.2)]"
            >
              <Search className="w-5 h-5 mr-2" />
              Find Projects
            </Link>
          </motion.div>
        </motion.div>

        {/* Dashboard Stats */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12"
        >
          {[
            { label: 'Proposals', count: proposedProjects.length, icon: Briefcase, color: 'text-[#9A9AA3]', prefix: '' },
            { label: 'Active', count: activeProjects.length, icon: Clock, color: 'text-accent', prefix: '' },
            { label: 'Completed', count: completedProjects.length, icon: CheckCircle, color: 'text-emerald-400', prefix: '' },
            { label: 'Earnings', count: totalEarnings, icon: IndianRupee, color: 'text-yellow-400', prefix: '₹' },
          ].map((stat, i) => (
            <motion.div 
              key={stat.label}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.1 + i * 0.1 }}
              className="bg-[#15151A] border border-[#2A2A32] rounded-2xl p-6 hover:border-[#3A3A42] transition-colors relative overflow-hidden group"
            >
              <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <div className="flex items-center text-[#9A9AA3] mb-4 relative z-10">
                 <stat.icon className={`w-5 h-5 mr-2 ${stat.color}`} />
                 <span className="text-sm font-bold uppercase tracking-wider">{stat.label}</span>
              </div>
              <p className={`text-4xl font-display font-black relative z-10 ${stat.color === 'text-[#9A9AA3]' ? '' : (stat.color === 'text-yellow-400' ? 'text-white' : stat.color)}`}>{stat.prefix}{stat.count}</p>
            </motion.div>
          ))}
        </motion.div>

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
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-[#15151A] border border-[#2A2A32] rounded-3xl p-16 text-center relative overflow-hidden group"
          >
            {/* Animated background elements */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-accent/10 rounded-full blur-[100px] pointer-events-none group-hover:bg-accent/20 transition-all duration-700"></div>
            
            <motion.div 
              animate={{ 
                y: [0, -10, 0],
                rotate: [0, -5, 5, 0]
              }}
              transition={{ 
                duration: 4,
                repeat: Infinity,
                ease: "easeInOut"
              }}
              className="w-24 h-24 bg-gradient-to-br from-[#2A2A32] to-[#15151A] border border-[#3A3A42] rounded-2xl flex items-center justify-center mx-auto mb-8 relative z-10 shadow-2xl"
            >
              <Search className="w-10 h-10 text-accent" />
            </motion.div>
            
            <h2 className="text-3xl font-display font-black mb-4 relative z-10">Your Pipeline is Empty</h2>
            <p className="text-[#9A9AA3] mb-8 max-w-md mx-auto relative z-10 text-lg">
              Start browsing the marketplace and submit proposals to win your first client project.
            </p>
            
            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} className="relative z-10 inline-block">
              <Link 
                to="/explore" 
                className="inline-flex items-center justify-center bg-accent text-white px-8 py-4 rounded-xl font-bold hover:bg-accent/90 transition-all shadow-[0_0_30px_rgba(168,85,247,0.3)] hover:shadow-[0_0_40px_rgba(168,85,247,0.5)]"
              >
                Explore Open Projects
                <ArrowRight className="w-5 h-5 ml-2" />
              </Link>
            </motion.div>
          </motion.div>
        ) : (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="space-y-6"
          >
            <h2 className="text-2xl font-display font-black uppercase">My Work</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {projects.map((project, index) => (
                <motion.div 
                  key={project.id} 
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 + index * 0.1 }}
                  className="bg-[#15151A] border border-[#2A2A32] rounded-2xl overflow-hidden flex flex-col hover:border-accent transition-all hover:shadow-[0_0_30px_rgba(168,85,247,0.15)] group"
                >
                   <div className="p-6 flex-1 flex flex-col">
                     <div className="flex justify-between items-start mb-4">
                        {getStatusBadge(project.status)}
                        <span className="text-sm font-bold text-accent bg-accent/10 px-3 py-1 rounded-full border border-accent/20">₹{(project.budget || 0) * 0.9} (Net)</span>
                     </div>
                     <h3 className="text-xl font-bold mb-2 group-hover:text-accent transition-colors">{project.title}</h3>
                     <p className="text-[#9A9AA3] text-sm line-clamp-2 mb-6 flex-1">
                       {project.description}
                     </p>
                     <button
                       onClick={() => navigate(`/projects/${project.id}`)}
                       className="w-full bg-[#2A2A32] hover:bg-accent text-white font-bold py-3 px-4 rounded-xl transition-all duration-300 text-sm flex items-center justify-center gap-2"
                     >
                       {project.status === 'DESIGNER_SELECTED' ? 'Accept Project' : 'View Project'}
                       <ArrowRight className="w-4 h-4 opacity-0 group-hover:opacity-100 -ml-4 group-hover:ml-0 transition-all duration-300" />
                     </button>
                   </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </main>
    </div>
  );
}
