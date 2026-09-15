import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { projectService } from '../../api/services/project.service';
import { paymentService } from '../../api/services/payment.service';
import { workspaceService } from '../../api/services/workspace.service';
import type { Project } from '../../types/marketplace';
import type { ProjectWorkspace as WorkspaceType } from '../../types/workspace';
import { Loader2, ArrowLeft, Clock, FileText, CheckCircle, AlertCircle, MessageSquare, Folder, Send } from 'lucide-react';
import Navbar from '../../components/layout/Navbar';
import { useAuth } from '../../context/AuthContext';
import ChatTab from '../../components/workspace/ChatTab';
import FilesTab from '../../components/workspace/FilesTab';
import DeliveriesTab from '../../components/workspace/DeliveriesTab';

export default function ProjectWorkspace() {
  const { projectId } = useParams<{ projectId: string }>();
  const [project, setProject] = useState<Project | null>(null);
  const [workspace, setWorkspace] = useState<WorkspaceType | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('overview');
  const [isPublishing, setIsPublishing] = useState(false);
  const [isProcessingPayment, setIsProcessingPayment] = useState(false);
  const [proposals, setProposals] = useState<any[]>([]);
  const [isSubmittingProposal, setIsSubmittingProposal] = useState(false);
  const [proposalData, setProposalData] = useState({
    proposedPrice: 0,
    deliveryDays: 0,
    conceptCount: 1,
    revisionCount: 1,
    approach: ''
  });
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
      if (response.data.status !== 'DRAFT') {
        fetchProposals();
      }
      if (response.data.status === 'ACTIVE' || response.data.status === 'COMPLETED') {
        fetchWorkspaceData();
      }
    } catch (err: any) {
      console.error(err);
      setError('Failed to load project details.');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchProposals = async () => {
    try {
      const res = await projectService.getProposals(projectId!);
      setProposals(res.data);
    } catch (err) {
      console.error('Failed to load proposals', err);
    }
  };

  const fetchWorkspaceData = async () => {
    try {
      const res = await workspaceService.getWorkspace(projectId!);
      setWorkspace(res.data);
    } catch (err) {
      console.error('Failed to load workspace data', err);
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

  const handleSubmitProposal = async () => {
    if (!project) return;
    if (proposalData.proposedPrice <= 0 || !proposalData.approach) {
      alert("Please provide a valid price and cover letter.");
      return;
    }
    setIsSubmittingProposal(true);
    try {
      await projectService.submitProposal(project.id, proposalData);
      alert("Proposal submitted successfully!");
      fetchProposals();
    } catch (err: any) {
      console.error(err);
      alert(err.response?.data?.detail || 'Failed to submit proposal.');
    } finally {
      setIsSubmittingProposal(false);
    }
  };

  const handleSelectDesigner = async (proposalId: string) => {
    if (!project || !isClient) return;
    try {
      await projectService.selectProposal(project.id, proposalId);
      alert("Designer selected successfully!");
      fetchProject();
    } catch (err: any) {
      console.error(err);
      alert(err.response?.data?.detail || 'Failed to select designer.');
    }
  };

  const handlePayment = async () => {
    if (!project) return;
    setIsProcessingPayment(true);
    try {
      // 1. Create order on backend
      const orderRes = await paymentService.createPayment(project.id);
      const paymentOrder = orderRes.data;

      // 2. Open Razorpay Checkout
      const options = {
        key: import.meta.env.VITE_RAZORPAY_KEY_ID || 'rzp_test_dummy_key',
        amount: paymentOrder.amount, // in paise
        currency: paymentOrder.currency,
        name: 'Lynvia Marketplace',
        description: `Payment for Project: ${project.title}`,
        order_id: paymentOrder.providerOrderId,
        handler: async function (response: any) {
          try {
            // 3. Verify on backend
            await paymentService.verifyPayment(paymentOrder.id, {
              razorpay_order_id: response.razorpay_order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature
            });
            alert("Payment verified successfully! Project is now ACTIVE.");
            fetchProject();
          } catch (err) {
            console.error("Verification failed", err);
            alert("Payment verification failed. Please contact support.");
          }
        },
        prefill: {
          email: user?.email || '',
        },
        theme: {
          color: '#A855F7'
        }
      };

      const rzp = new (window as any).Razorpay(options);
      rzp.on('payment.failed', function (response: any) {
        console.error("Payment failed", response.error);
        alert("Payment failed. Please try again.");
      });
      rzp.open();

    } catch (err: any) {
      console.error("Payment creation failed", err);
      alert(err.response?.data?.detail || "Failed to initiate payment");
    } finally {
      setIsProcessingPayment(false);
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

  const isClient = user?.id === project.clientId;

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
                  {project.deadline ? new Date(project.deadline).toLocaleDateString() : 'Flexible Timeline'}
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
            
            {/* Tabs for Active/Completed Projects */}
            {['ACTIVE', 'IN_REVIEW', 'DELIVERED', 'COMPLETED'].includes(project.status) && (
              <div className="flex items-center gap-2 bg-[#15151A] border border-[#2A2A32] rounded-2xl p-2 overflow-x-auto">
                <button 
                  onClick={() => setActiveTab('overview')}
                  className={`flex items-center px-6 py-3 rounded-xl font-bold whitespace-nowrap transition-colors ${activeTab === 'overview' ? 'bg-accent text-white' : 'text-[#9A9AA3] hover:text-white hover:bg-[#2A2A32]'}`}
                >
                  <FileText className="w-4 h-4 mr-2" />
                  Overview
                </button>
                <button 
                  onClick={() => setActiveTab('chat')}
                  className={`flex items-center px-6 py-3 rounded-xl font-bold whitespace-nowrap transition-colors ${activeTab === 'chat' ? 'bg-accent text-white' : 'text-[#9A9AA3] hover:text-white hover:bg-[#2A2A32]'}`}
                >
                  <MessageSquare className="w-4 h-4 mr-2" />
                  Chat
                </button>
                <button 
                  onClick={() => setActiveTab('files')}
                  className={`flex items-center px-6 py-3 rounded-xl font-bold whitespace-nowrap transition-colors ${activeTab === 'files' ? 'bg-accent text-white' : 'text-[#9A9AA3] hover:text-white hover:bg-[#2A2A32]'}`}
                >
                  <Folder className="w-4 h-4 mr-2" />
                  Files
                </button>
                <button 
                  onClick={() => setActiveTab('deliveries')}
                  className={`flex items-center px-6 py-3 rounded-xl font-bold whitespace-nowrap transition-colors ${activeTab === 'deliveries' ? 'bg-accent text-white' : 'text-[#9A9AA3] hover:text-white hover:bg-[#2A2A32]'}`}
                >
                  <Send className="w-4 h-4 mr-2" />
                  Deliveries
                </button>
              </div>
            )}

            {activeTab === 'overview' && (
              <>
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
            {isClient && ['OPEN_FOR_PROPOSALS', 'PROPOSAL_REVIEW', 'DESIGNER_SELECTED', 'AWAITING_PAYMENT'].includes(project.status) && (
              <div className="bg-[#15151A] border border-[#2A2A32] rounded-3xl p-8">
                <h2 className="text-2xl font-bold mb-6">Proposals ({proposals.length})</h2>
                {proposals.length === 0 ? (
                  <div className="text-center py-12 border-2 border-dashed border-[#2A2A32] rounded-2xl bg-[#0D0D0F]">
                     <p className="text-[#9A9AA3] mb-4">No proposals received yet.</p>
                     <p className="text-sm text-[#5A5A63]">When designers submit proposals, they will appear here.</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {proposals.map(proposal => (
                      <div key={proposal.id} className="bg-[#0D0D0F] border border-[#2A2A32] rounded-2xl p-6">
                        <div className="flex justify-between items-start mb-4">
                          <h3 className="font-bold text-lg">Designer: {proposal.designerId}</h3>
                          <div className="text-right">
                            <span className="text-accent font-bold text-xl">₹{proposal.proposedPrice}</span>
                            <div className="text-sm text-[#9A9AA3]">{proposal.deliveryDays} Days</div>
                          </div>
                        </div>
                        <p className="text-[#9A9AA3] text-sm whitespace-pre-wrap mb-6">{proposal.approach}</p>
                        <div className="flex justify-between items-center">
                          <span className={`px-3 py-1 rounded-full text-xs font-bold ${proposal.status === 'SELECTED' ? 'bg-accent/20 text-accent' : 'bg-[#2A2A32] text-white'}`}>
                            {proposal.status}
                          </span>
                          {project.status === 'OPEN_FOR_PROPOSALS' && proposal.status === 'SUBMITTED' && (
                            <button 
                              onClick={() => handleSelectDesigner(proposal.id)}
                              className="px-6 py-2 bg-white text-black rounded-lg font-bold hover:bg-white/90 transition-colors"
                            >
                              Select Designer
                            </button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Designer Proposal Submission */}
            {role === 'DESIGNER' && project.status === 'OPEN_FOR_PROPOSALS' && (
              <div className="bg-[#15151A] border border-accent/20 rounded-3xl p-8">
                {proposals.some(p => p.designerId === user?.id) ? (
                   <div className="text-center py-8">
                     <CheckCircle className="w-12 h-12 text-accent mx-auto mb-4" />
                     <h3 className="text-xl font-bold mb-2">Proposal Submitted</h3>
                     <p className="text-[#9A9AA3]">You have successfully submitted your proposal for this project. The client will review it shortly.</p>
                   </div>
                ) : (
                  <>
                    <h2 className="text-2xl font-bold mb-6 text-accent">Submit a Proposal</h2>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-bold mb-2">Cover Letter</label>
                        <textarea 
                          value={proposalData.approach}
                          onChange={(e) => setProposalData({...proposalData, approach: e.target.value})}
                          className="w-full bg-[#0D0D0F] border border-[#2A2A32] rounded-xl p-4 text-[#F5F5F5] min-h-[150px] focus:border-accent focus:outline-none"
                          placeholder="Explain why you are the best fit for this project..."
                        ></textarea>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-bold mb-2">Proposed Price (₹)</label>
                          <input 
                            type="number"
                            value={proposalData.proposedPrice || ''}
                            onChange={(e) => setProposalData({...proposalData, proposedPrice: Number(e.target.value)})}
                            className="w-full bg-[#0D0D0F] border border-[#2A2A32] rounded-xl p-4 text-[#F5F5F5] focus:border-accent focus:outline-none"
                            placeholder={project.budget?.toString()}
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-bold mb-2">Delivery Time (Days)</label>
                          <input 
                            type="number"
                            value={proposalData.deliveryDays || ''}
                            onChange={(e) => setProposalData({...proposalData, deliveryDays: Number(e.target.value)})}
                            className="w-full bg-[#0D0D0F] border border-[#2A2A32] rounded-xl p-4 text-[#F5F5F5] focus:border-accent focus:outline-none"
                            placeholder="7"
                          />
                        </div>
                      </div>
                      <button 
                        onClick={handleSubmitProposal}
                        disabled={isSubmittingProposal}
                        className="bg-accent text-white px-8 py-3 rounded-xl font-bold hover:bg-accent/90 transition-colors w-full md:w-auto mt-4 disabled:opacity-50"
                      >
                        {isSubmittingProposal ? <Loader2 className="w-5 h-5 animate-spin mx-auto" /> : 'Submit Proposal'}
                      </button>
                    </div>
                  </>
                )}
              </div>
            )}

            {/* Client Payment Section */}
            {isClient && project.status === 'AWAITING_PAYMENT' && (
              <div className="bg-accent/10 border border-accent rounded-3xl p-8 text-center">
                 <h2 className="text-3xl font-bold mb-4 text-white">Action Required: Make Payment</h2>
                 <p className="text-[#9A9AA3] mb-8 max-w-lg mx-auto">
                   The designer has accepted the project! To start the work and transition this project to <strong>ACTIVE</strong>, please complete the upfront payment of <strong>₹{project.budget}</strong>. Funds are held securely in escrow.
                 </p>
                 <button 
                   onClick={handlePayment}
                   disabled={isProcessingPayment}
                   className="bg-accent text-white px-10 py-4 rounded-xl font-bold text-lg hover:bg-accent/90 transition-colors w-full md:w-auto shadow-[0_0_20px_rgba(168,85,247,0.4)] disabled:opacity-50 flex items-center justify-center gap-2 mx-auto"
                 >
                   {isProcessingPayment ? <Loader2 className="w-5 h-5 animate-spin" /> : null}
                   Pay ₹{project.budget} to Start Project
                 </button>
              </div>
            )}

            {/* Designer Accept Project */}
            {role === 'DESIGNER' && project.status === 'DESIGNER_SELECTED' && project.designerId === user?.id && (
              <div className="bg-accent/10 border border-accent rounded-3xl p-8 text-center">
                 <h2 className="text-3xl font-bold mb-4 text-white">Congratulations! 🎉</h2>
                 <p className="text-[#9A9AA3] mb-8">The client has selected your proposal. Please accept the project to proceed to the payment phase.</p>
                 <button 
                   onClick={async () => {
                     try {
                       await projectService.acceptProject(project.id);
                       alert("Project accepted!");
                       fetchProject();
                     } catch (err) {
                       console.error(err);
                       alert("Failed to accept project.");
                     }
                   }}
                   className="bg-accent text-white px-10 py-4 rounded-xl font-bold text-lg hover:bg-accent/90 transition-colors w-full md:w-auto shadow-[0_0_20px_rgba(168,85,247,0.4)]"
                 >
                   Accept Project
                 </button>
              </div>
            )}
            </>
            )}

            {activeTab === 'chat' && (
              project.status === 'ACTIVE' || project.status === 'COMPLETED' ? (
                <ChatTab projectId={project.id} />
              ) : (
                <div className="bg-[#15151A] border border-[#2A2A32] rounded-3xl p-8 min-h-[500px] flex flex-col items-center justify-center text-center">
                  <MessageSquare className="w-12 h-12 text-[#2A2A32] mb-4" />
                  <h3 className="text-xl font-bold mb-2">Project Chat</h3>
                  <p className="text-[#9A9AA3]">Real-time chat functionality will be available once the project is ACTIVE.</p>
                </div>
              )
            )}

            {activeTab === 'files' && (
              project.status === 'ACTIVE' || project.status === 'COMPLETED' ? (
                workspace ? (
                  <FilesTab 
                    projectId={project.id} 
                    initialFiles={workspace.files} 
                    onFileAdded={() => fetchWorkspaceData()} 
                  />
                ) : <Loader2 className="w-8 h-8 animate-spin text-accent mx-auto" />
              ) : (
                <div className="bg-[#15151A] border border-[#2A2A32] rounded-3xl p-8 min-h-[500px] flex flex-col items-center justify-center text-center">
                  <Folder className="w-12 h-12 text-[#2A2A32] mb-4" />
                  <h3 className="text-xl font-bold mb-2">Project Files</h3>
                  <p className="text-[#9A9AA3]">File management system will be available once the project is ACTIVE.</p>
                </div>
              )
            )}

            {activeTab === 'deliveries' && (
              project.status === 'ACTIVE' || project.status === 'COMPLETED' ? (
                workspace ? (
                  <DeliveriesTab 
                    project={project} 
                    initialDeliveries={workspace.deliveries}
                    workspaceFiles={workspace.files}
                    onDeliveryUpdated={() => {
                      fetchWorkspaceData();
                      fetchProject(); // Might update project status
                    }}
                  />
                ) : <Loader2 className="w-8 h-8 animate-spin text-accent mx-auto" />
              ) : (
                <div className="bg-[#15151A] border border-[#2A2A32] rounded-3xl p-8 min-h-[500px] flex flex-col items-center justify-center text-center">
                  <Send className="w-12 h-12 text-[#2A2A32] mb-4" />
                  <h3 className="text-xl font-bold mb-2">Deliveries & Revisions</h3>
                  <p className="text-[#9A9AA3]">Delivery management will be available once the project is ACTIVE.</p>
                </div>
              )
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
                    <p className="text-sm text-[#9A9AA3]">{new Date(project.createdAt).toLocaleDateString()}</p>
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
                  <span className="font-bold text-white">₹{(project.budget || 0) * 0.1}</span>
                </div>
                <div className="pt-4 border-t border-[#2A2A32] flex justify-between items-center">
                  <span className="font-bold">Total Payout</span>
                  <span className="font-bold text-accent text-xl">₹{(project.budget || 0) * 0.9}</span>
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
