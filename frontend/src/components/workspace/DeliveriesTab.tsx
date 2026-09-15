import React, { useState } from 'react';
import type { Delivery, FileMetadata } from '../../types/workspace';
import { workspaceService } from '../../api/services/workspace.service';
import { useAuth } from '../../context/AuthContext';
import { Package, CheckCircle, AlertCircle, Clock, FileIcon, Loader2 } from 'lucide-react';
import type { Project } from '../../types/marketplace';

interface DeliveriesTabProps {
  project: Project;
  initialDeliveries: Delivery[];
  workspaceFiles: FileMetadata[];
  onDeliveryUpdated: () => void; // Trigger a refresh of the workspace
}

export default function DeliveriesTab({ project, initialDeliveries, workspaceFiles, onDeliveryUpdated }: DeliveriesTabProps) {
  const { user } = useAuth();
  const [deliveries] = useState<Delivery[]>(initialDeliveries);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [deliveryMessage, setDeliveryMessage] = useState('');
  const [selectedFileIds, setSelectedFileIds] = useState<string[]>([]);
  
  // Revision state
  const [activeDeliveryId, setActiveDeliveryId] = useState<string | null>(null);
  const [revisionReason, setRevisionReason] = useState('');
  const [revisionComment, setRevisionComment] = useState('');
  const [isRequestingRevision, setIsRequestingRevision] = useState(false);
  const [isAccepting, setIsAccepting] = useState(false);

  const isClient = user?.id === project.clientId;
  const isDesigner = user?.id === project.designerId;
  const latestDelivery = deliveries.length > 0 ? deliveries[deliveries.length - 1] : null;

  const handleSubmitDelivery = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!deliveryMessage.trim()) return;

    try {
      setIsSubmitting(true);
      await workspaceService.submitDelivery(project.id, {
        message: deliveryMessage,
        fileIds: selectedFileIds
      });
      setDeliveryMessage('');
      setSelectedFileIds([]);
      onDeliveryUpdated();
    } catch (err) {
      console.error("Failed to submit delivery", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleAcceptDelivery = async (deliveryId: string) => {
    try {
      setIsAccepting(true);
      await workspaceService.acceptDelivery(project.id, deliveryId);
      onDeliveryUpdated();
    } catch (err) {
      console.error("Failed to accept delivery", err);
    } finally {
      setIsAccepting(false);
    }
  };

  const handleRequestRevision = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeDeliveryId || !revisionReason.trim() || !revisionComment.trim()) return;

    try {
      setIsRequestingRevision(true);
      await workspaceService.requestRevision(project.id, activeDeliveryId, {
        requestReason: revisionReason,
        clientComment: revisionComment
      });
      setActiveDeliveryId(null);
      setRevisionReason('');
      setRevisionComment('');
      onDeliveryUpdated();
    } catch (err) {
      console.error("Failed to request revision", err);
    } finally {
      setIsRequestingRevision(false);
    }
  };

  const toggleFileSelection = (fileId: string) => {
    setSelectedFileIds(prev => 
      prev.includes(fileId) ? prev.filter(id => id !== fileId) : [...prev, fileId]
    );
  };

  return (
    <div className="space-y-8">
      
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-display font-black uppercase">Project Deliveries</h3>
        <span className="bg-[#15151A] border border-[#2A2A32] text-[#9A9AA3] px-4 py-1.5 rounded-full text-sm font-medium flex items-center gap-2">
          <Package className="h-4 w-4" />
          {deliveries.length} Submissions
        </span>
      </div>

      {/* Designer Submission Form (Only show if designer and latest delivery is not SUBMITTED/ACCEPTED) */}
      {isDesigner && (!latestDelivery || latestDelivery.status === 'REJECTED' || latestDelivery.status === 'IN_REVISION') && project.status === 'ACTIVE' && (
        <div className="bg-[#15151A] border border-accent/30 rounded-2xl p-6 relative overflow-hidden">
          <div className="absolute top-0 left-0 w-1 h-full bg-accent"></div>
          <h4 className="text-lg font-bold mb-4">Submit New Delivery</h4>
          
          <form onSubmit={handleSubmitDelivery} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-[#9A9AA3] uppercase tracking-wider mb-2">
                Delivery Message / Notes
              </label>
              <textarea
                required
                value={deliveryMessage}
                onChange={(e) => setDeliveryMessage(e.target.value)}
                rows={3}
                placeholder="Describe what you are delivering..."
                className="block w-full px-4 py-3 bg-[#0D0D0F] border border-[#2A2A32] rounded-lg text-[#F5F5F5] placeholder-[#9A9AA3]/50 focus:outline-none focus:border-accent"
              />
            </div>
            
            <div>
              <label className="block text-xs font-medium text-[#9A9AA3] uppercase tracking-wider mb-2">
                Attach Files from Workspace
              </label>
              {workspaceFiles.length === 0 ? (
                <p className="text-sm text-[#9A9AA3] bg-[#0D0D0F] p-3 rounded-lg border border-[#2A2A32]">
                  No files available in the workspace. Upload files in the Files tab first.
                </p>
              ) : (
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {workspaceFiles.map(file => (
                    <div 
                      key={file.id}
                      onClick={() => toggleFileSelection(file.id)}
                      className={`p-3 rounded-lg border cursor-pointer flex items-center gap-3 transition-colors ${
                        selectedFileIds.includes(file.id) 
                          ? 'bg-accent/10 border-accent text-white' 
                          : 'bg-[#0D0D0F] border-[#2A2A32] text-[#9A9AA3] hover:border-[#9A9AA3]'
                      }`}
                    >
                      <FileIcon className="h-5 w-5 shrink-0" />
                      <span className="text-xs truncate">{file.filename}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="flex justify-end pt-2">
              <button
                type="submit"
                disabled={isSubmitting || !deliveryMessage.trim()}
                className="flex items-center gap-2 px-6 py-2.5 bg-accent text-white rounded-lg font-bold text-sm hover:bg-accent/90 transition-colors disabled:opacity-50"
              >
                {isSubmitting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Package className="h-4 w-4" />}
                Submit Delivery
              </button>
            </div>
          </form>
        </div>
      )}

      {/* History Log */}
      <div className="space-y-4">
        {deliveries.length === 0 ? (
          <div className="text-center py-12 bg-[#15151A] rounded-2xl border border-[#2A2A32]">
            <Clock className="h-10 w-10 text-[#2A2A32] mx-auto mb-3" />
            <p className="text-[#9A9AA3]">No deliveries have been made yet.</p>
          </div>
        ) : (
          [...deliveries].reverse().map(delivery => (
            <div key={delivery.id} className="bg-[#15151A] border border-[#2A2A32] rounded-2xl p-6">
              <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6 pb-4 border-b border-[#2A2A32]">
                <div>
                  <div className="flex items-center gap-3 mb-1">
                    <h4 className="text-lg font-bold">Delivery v{delivery.version}</h4>
                    <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                      delivery.status === 'ACCEPTED' ? 'bg-green-500/10 text-green-400 border border-green-500/20' :
                      delivery.status === 'IN_REVISION' ? 'bg-orange-500/10 text-orange-400 border border-orange-500/20' :
                      'bg-blue-500/10 text-blue-400 border border-blue-500/20'
                    }`}>
                      {delivery.status}
                    </span>
                  </div>
                  <p className="text-xs text-[#9A9AA3]">Submitted on {new Date(delivery.submittedAt).toLocaleDateString()}</p>
                </div>
                
                {/* Client Actions */}
                {isClient && delivery.status === 'SUBMITTED' && (
                  <div className="flex gap-3">
                    <button 
                      onClick={() => setActiveDeliveryId(delivery.id)}
                      className="px-4 py-2 bg-[#2A2A32] text-white rounded-lg text-sm font-medium hover:bg-[#3A3A42] transition-colors"
                    >
                      Request Revision
                    </button>
                    <button 
                      onClick={() => handleAcceptDelivery(delivery.id)}
                      disabled={isAccepting}
                      className="px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg text-sm font-bold transition-colors flex items-center gap-2"
                    >
                      {isAccepting ? <Loader2 className="h-4 w-4 animate-spin" /> : <CheckCircle className="h-4 w-4" />}
                      Approve & Release Funds
                    </button>
                  </div>
                )}
              </div>

              <div className="mb-6">
                <h5 className="text-sm font-medium text-[#9A9AA3] mb-2">Designer's Notes</h5>
                <p className="text-sm bg-[#0D0D0F] p-4 rounded-lg border border-[#2A2A32]">{delivery.message}</p>
              </div>

              {/* Attached Files - assuming backend links FileMetadata or we cross-reference fileIds */}
              {/* For MVP, we'll just show that files were attached, matching against workspaceFiles if possible */}
              
              {/* Revisions Log */}
              {delivery.revisions && delivery.revisions.length > 0 && (
                <div className="mt-6 pt-6 border-t border-[#2A2A32]">
                  <h5 className="text-sm font-medium text-[#9A9AA3] mb-4 flex items-center gap-2">
                    <AlertCircle className="h-4 w-4" /> Revision History
                  </h5>
                  <div className="space-y-4">
                    {delivery.revisions.map((rev: any) => (
                      <div key={rev.id} className="bg-orange-500/5 border border-orange-500/20 rounded-lg p-4">
                        <div className="flex justify-between items-start mb-2">
                          <span className="text-xs font-bold text-orange-400 uppercase tracking-wider">{rev.requestReason}</span>
                          <span className="text-xs text-[#9A9AA3]">{new Date(rev.createdAt).toLocaleDateString()}</span>
                        </div>
                        <p className="text-sm">{rev.clientComment}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Revision Request Form (Client) */}
              {activeDeliveryId === delivery.id && (
                <form onSubmit={handleRequestRevision} className="mt-6 pt-6 border-t border-[#2A2A32] animate-in fade-in slide-in-from-top-4">
                  <h5 className="text-sm font-bold text-orange-400 mb-4">Requesting Revision</h5>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-xs font-medium text-[#9A9AA3] uppercase tracking-wider mb-2">Reason</label>
                      <select
                        required
                        value={revisionReason}
                        onChange={(e) => setRevisionReason(e.target.value)}
                        className="block w-full px-4 py-3 bg-[#0D0D0F] border border-[#2A2A32] rounded-lg text-[#F5F5F5] focus:outline-none focus:border-accent"
                      >
                        <option value="">Select a reason...</option>
                        <option value="Minor Adjustments">Minor Adjustments</option>
                        <option value="Major Changes Required">Major Changes Required</option>
                        <option value="Does Not Meet Requirements">Does Not Meet Requirements</option>
                        <option value="Other">Other</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-[#9A9AA3] uppercase tracking-wider mb-2">Feedback Details</label>
                      <textarea
                        required
                        value={revisionComment}
                        onChange={(e) => setRevisionComment(e.target.value)}
                        rows={3}
                        placeholder="Provide specific feedback on what needs to be changed..."
                        className="block w-full px-4 py-3 bg-[#0D0D0F] border border-[#2A2A32] rounded-lg text-[#F5F5F5] placeholder-[#9A9AA3]/50 focus:outline-none focus:border-accent"
                      />
                    </div>
                    <div className="flex justify-end gap-3 pt-2">
                      <button 
                        type="button"
                        onClick={() => setActiveDeliveryId(null)}
                        className="px-4 py-2 text-[#9A9AA3] hover:text-white transition-colors"
                      >
                        Cancel
                      </button>
                      <button 
                        type="submit"
                        disabled={isRequestingRevision || !revisionReason || !revisionComment.trim()}
                        className="px-6 py-2 bg-orange-500 text-white rounded-lg font-bold text-sm hover:bg-orange-600 transition-colors disabled:opacity-50 flex items-center gap-2"
                      >
                        {isRequestingRevision ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
                        Submit Revision Request
                      </button>
                    </div>
                  </div>
                </form>
              )}

            </div>
          ))
        )}
      </div>
    </div>
  );
}
