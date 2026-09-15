import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { projectService } from '../../api/services/project.service';
import type { Project } from '../../types/marketplace';
import { Loader2, ArrowLeft, Clock, FileText, CheckCircle, AlertCircle } from 'lucide-react';
import Navbar from '../../components/layout/Navbar';
import { useAuth } from '../../context/AuthContext';

export default function ProjectWorkspace() {
  const { projectId } = useParams<{ projectId: string }>();
  const [project, setProject] = useState<Project | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [isPublishing, setIsPublishing] = useState(false);
  const { user, role } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (projectId) {
      fetchProject();
    }
  }, [projectId]);

  const fetchProject = async () => {
    setIsLoading(true);
    setError('');
    try {
      const response = await projectService.getProject(projectId!);
      setProject(response.data);
    } catch (err: any) {
      console.error(err);
      setError('Failed to load project details.');
    } finally {
      setIsLoading(false);
    }
  };

  const handlePublish = async () => {
    if (!project) return;
    setIsPublishing(true);
    try {
      await projectService.publishProject(project.id);
      await fetchProject();
    } catch (err: any) {
      console.error(err);
      alert('Failed to publish project. Please try again.');
    } finally {
      setIsPublishing(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#0D0D0F] font-sans text-[#F5F5F5]">
        <Navbar />
        <main className="pt-32 px-6 flex flex-col items-center justify-center py-20">
          <Loader2 className="animate-spin h-10 w-10 text-accent mb-4" />
          <p className="text-[#9A9AA3]">Loading workspace...</p>
        </main>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="min-h-screen bg-[#0D0D0F] font-sans text-[#F5F5F5]">
        <Navbar />
        <main className="pt-32 px-6 max-w-4xl mx-auto pb-24">
          <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-8 rounded-3xl text-center">
            <h2 className="text-2xl font-bold mb-4">Project Not Found</h2>
            <p>{error}</p>
            <button onClick={() => navigate(-1)} className="mt-8 inline-block px-6 py-3 bg-red-500/20 rounded-xl hover:bg-red-500/30 transition-colors font-bold">
              Go Back
            </button>
          </div>
        </main>
      </div>
    );
  }

  const isClient = user?.id === project.client_id;

  const getStatusBadge = (status: string) => {
    switch(status) {
      case 'DRAFT': return <span className="bg-slate-500/20 text-slate-400 px-4 py-2 rounded-xl text-sm font-bold uppercase">Draft</span>;
      case 'OPEN_FOR_PROPOSALS': return <span className="bg-blue-500/20 text-blue-400 px-4 py-2 rounded-xl text-sm font-bold uppercase">Open for Proposals</span>;
      case 'PROPOSAL_REVIEW': return <span className="bg-indigo-500/20 text-indigo-400 px-4 py-2 rounded-xl text-sm font-bold uppercase">Reviewing</span>;
      case 'DESIGNER_SELECTED': return <span className="bg-yellow-500/20 text-yellow-400 px-4 py-2 rounded-xl text-sm font-bold uppercase">Designer Selected</span>;
      case 'AWAITING_PAYMENT': return <span className="bg-red-500/20 text-red-400 px-4 py-2 rounded-xl text-sm font-bold uppercase">Awaiting Payment</span>;
      case 'ACTIVE': return <span className="bg-accent/20 text-accent px-4 py-2 rounded-xl text-sm font-bold uppercase">Active</span>;
      case 'IN_REVIEW': return <span className="bg-orange-500/20 text-orange-400 px-4 py-2 rounded-xl text-sm font-bold uppercase">In Review</span>;
      case 'DELIVERED': return <span className="bg-emerald-500/20 text-emerald-400 px-4 py-2 rounded-xl text-sm font-bold uppercase">Delivered</span>;
      case 'COMPLETED': return <span className="bg-emerald-500/20 text-emerald-400 px-4 py-2 rounded-xl text-sm font-bold uppercase">Completed</span>;
      default: return <span className="bg-slate-500/20 text-slate-400 px-4 py-2 rounded-xl text-sm font-bold uppercase">{status}</span>;
    }
  };

  return (
    <div className="min-h-screen bg-[#0D0D0F] font-sans text-[#F5F5F5]">
      <Navbar />

      <main className="pt-32 px-6 max-w-5xl mx-auto pb-24">
        
        {/* Back Navigation */}
        <button 
          onClick={() => navigate(-1)} 
          className="flex items-center text-[#9A9AA3] hover:text-white transition-colors mb-8 font-bold"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Dashboard
        </button>

        {/* Workspace Header */}
        <div className="bg-[#15151A] border border-[#2A2A32] rounded-3xl p-8 md:p-12 mb-8 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-64 h-64 bg-accent/10 rounded-full blur-3xl transform translate-x-1/3 -translate-y-1/3"></div>
          
          <div className="relative z-10">
            <div className="flex flex-col md:flex-row md:items-start justify-between gap-6 mb-6">
              <div>
                <div className="flex items-center gap-4 mb-4">
                  {getStatusBadge(project.status)}
                  <span className="text-[#9A9AA3] text-sm font-bold">{project.category}</span>
                </div>
                <h1 className="text-4xl md:text-5xl font-display font-black tracking-tight mb-4">{project.title}</h1>
              </div>
              
              <div className="flex flex-col items-start md:items-end gap-2 shrink-0">
                <div className="text-3xl font-black text-white">₹{project.budget}</div>
                <div className="text-[#9A9AA3] text-sm flex items-center">
                  <Clock className="w-4 h-4 mr-1" />
                  {project.expected_delivery_days} Days Delivery
                </div>
              </div>
            </div>

            {project.status === 'DRAFT' && isClient && (
              <div className="mt-8 pt-8 border-t border-[#2A2A32] flex items-center justify-between">
                <p className="text-[#9A9AA3]">This project is currently a draft. Publish it to start receiving proposals.</p>
                <button 
                  onClick={handlePublish}
                  disabled={isPublishing}
                  className="bg-accent text-white px-8 py-3 rounded-xl font-bold hover:bg-accent/90 transition-colors disabled:opacity-50"
                >
                  {isPublishing ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Publish Project'}
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Workspace Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Main Content Area */}
          <div className="lg:col-span-2 space-y-8">
            <div className="bg-[#15151A] border border-[#2A2A32] rounded-3xl p-8">
              <h2 className="text-2xl font-bold mb-6 flex items-center">
                <FileText className="w-6 h-6 mr-3 text-accent" />
                Project Details
              </h2>
              <div className="prose prose-invert max-w-none">
                <p className="whitespace-pre-wrap text-[#9A9AA3] leading-relaxed">
                  {project.description}
                </p>
              </div>
            </div>

            {/* Render Proposals Section if Client and Status allows */}
            {isClient && ['OPEN_FOR_PROPOSALS', 'PROPOSAL_REVIEW'].includes(project.status) && (
              <div className="bg-[#15151A] border border-[#2A2A32] rounded-3xl p-8">
                <h2 className="text-2xl font-bold mb-6">Proposals</h2>
                <div className="text-center py-12 border-2 border-dashed border-[#2A2A32] rounded-2xl bg-[#0D0D0F]">
                   <p className="text-[#9A9AA3] mb-4">No proposals received yet.</p>
                   <p className="text-sm text-[#5A5A63]">When designers submit proposals, they will appear here.</p>
                </div>
              </div>
            )}

            {/* Designer Proposal Submission */}
            {role === 'DESIGNER' && project.status === 'OPEN_FOR_PROPOSALS' && (
              <div className="bg-[#15151A] border border-accent/20 rounded-3xl p-8">
                <h2 className="text-2xl font-bold mb-6 text-accent">Submit a Proposal</h2>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-bold mb-2">Cover Letter</label>
                    <textarea 
                      className="w-full bg-[#0D0D0F] border border-[#2A2A32] rounded-xl p-4 text-[#F5F5F5] min-h-[150px] focus:border-accent focus:outline-none"
                      placeholder="Explain why you are the best fit for this project..."
                    ></textarea>
                  </div>
                  <div>
                    <label className="block text-sm font-bold mb-2">Proposed Price (₹)</label>
                    <input 
                      type="number"
                      className="w-full md:w-1/3 bg-[#0D0D0F] border border-[#2A2A32] rounded-xl p-4 text-[#F5F5F5] focus:border-accent focus:outline-none"
                      placeholder={project.budget.toString()}
                    />
                  </div>
                  <button className="bg-accent text-white px-8 py-3 rounded-xl font-bold hover:bg-accent/90 transition-colors w-full md:w-auto">
                    Submit Proposal
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-8">
             
            {/* Timeline / Status */}
            <div className="bg-[#15151A] border border-[#2A2A32] rounded-3xl p-8">
              <h3 className="text-xl font-bold mb-6">Timeline</h3>
              
              <div className="space-y-6">
                <div className="flex gap-4">
                  <div className="flex flex-col items-center">
                    <CheckCircle className="w-6 h-6 text-accent" />
                    <div className="w-0.5 h-full bg-accent mt-2"></div>
                  </div>
                  <div className="pb-6">
                    <p className="font-bold">Project Created</p>
                    <p className="text-sm text-[#9A9AA3]">{new Date(project.created_at).toLocaleDateString()}</p>
                  </div>
                </div>

                <div className="flex gap-4">
                  <div className="flex flex-col items-center">
                    {project.status !== 'DRAFT' ? (
                       <CheckCircle className="w-6 h-6 text-accent" />
                    ) : (
                       <div className="w-6 h-6 rounded-full border-2 border-[#2A2A32] bg-[#0D0D0F]"></div>
                    )}
                    <div className={`w-0.5 h-full mt-2 ${project.status !== 'DRAFT' ? 'bg-accent' : 'bg-[#2A2A32]'}`}></div>
                  </div>
                  <div className="pb-6">
                    <p className={`font-bold ${project.status === 'DRAFT' ? 'text-[#9A9AA3]' : ''}`}>Published</p>
                  </div>
                </div>

                <div className="flex gap-4">
                  <div className="flex flex-col items-center">
                    {['DESIGNER_SELECTED', 'AWAITING_PAYMENT', 'ACTIVE', 'IN_REVIEW', 'DELIVERED', 'COMPLETED'].includes(project.status) ? (
                       <CheckCircle className="w-6 h-6 text-accent" />
                    ) : (
                       <div className="w-6 h-6 rounded-full border-2 border-[#2A2A32] bg-[#0D0D0F]"></div>
                    )}
                  </div>
                  <div>
                    <p className={`font-bold ${!['DESIGNER_SELECTED', 'AWAITING_PAYMENT', 'ACTIVE', 'IN_REVIEW', 'DELIVERED', 'COMPLETED'].includes(project.status) ? 'text-[#9A9AA3]' : ''}`}>Designer Selected</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Financial Summary */}
            <div className="bg-[#15151A] border border-[#2A2A32] rounded-3xl p-8">
              <h3 className="text-xl font-bold mb-6">Financials</h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center text-[#9A9AA3]">
                  <span>Project Budget</span>
                  <span className="font-bold text-white">₹{project.budget}</span>
                </div>
                <div className="flex justify-between items-center text-[#9A9AA3]">
                  <span>Platform Fee (10%)</span>
                  <span className="font-bold text-white">₹{project.budget * 0.1}</span>
                </div>
                <div className="pt-4 border-t border-[#2A2A32] flex justify-between items-center">
                  <span className="font-bold">Total Payout</span>
                  <span className="font-bold text-accent text-xl">₹{project.budget * 0.9}</span>
                </div>
              </div>
              
              <div className="mt-6 flex items-start gap-3 bg-blue-500/10 p-4 rounded-xl border border-blue-500/20">
                <AlertCircle className="w-5 h-5 text-blue-400 shrink-0 mt-0.5" />
                <p className="text-xs text-blue-400/90 leading-relaxed">
                  Payments are held securely in escrow until milestones are approved. 100% upfront payment is required upon hiring.
                </p>
              </div>
            </div>

          </div>

        </div>
      </main>
    </div>
  );
}
