import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { discoveryService } from '../api/services/discovery.service';
import type { DesignerProfile as DesignerProfileType } from '../types/marketplace';
import { Loader2, Star, Briefcase, Mail } from 'lucide-react';
import Navbar from '../components/layout/Navbar';

export default function DesignerProfile() {
  const { designerId } = useParams<{ designerId: string }>();
  const [designer, setDesigner] = useState<DesignerProfileType | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (designerId) {
      fetchDesigner();
    }
  }, [designerId]);

  const fetchDesigner = async () => {
    setIsLoading(true);
    setError('');
    try {
      const response = await discoveryService.getDesignerProfile(designerId!);
      setDesigner(response.data);
    } catch (err: any) {
      console.error(err);
      setError('Failed to load designer profile. They might not exist or the link is invalid.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0D0D0F] font-sans text-[#F5F5F5]">
      <Navbar />

      <main className="pt-32 px-6 max-w-5xl mx-auto pb-24">
        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-20">
            <Loader2 className="animate-spin h-10 w-10 text-accent mb-4" />
            <p className="text-[#9A9AA3]">Loading profile...</p>
          </div>
        ) : error || !designer ? (
          <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-8 rounded-3xl text-center max-w-2xl mx-auto">
            <h2 className="text-2xl font-bold mb-4">Profile Not Found</h2>
            <p>{error}</p>
            <Link to="/designers" className="mt-8 inline-block px-6 py-3 bg-red-500/20 rounded-xl hover:bg-red-500/30 transition-colors font-bold">
              Back to Designers
            </Link>
          </div>
        ) : (
          <div className="space-y-12">
            
            {/* Header Profile Section */}
            <div className="bg-[#15151A] border border-[#2A2A32] rounded-3xl p-8 md:p-12 relative overflow-hidden">
              <div className="absolute top-0 left-0 w-full h-32 bg-gradient-to-r from-accent/20 to-purple-600/20 opacity-50"></div>
              
              <div className="relative z-10 flex flex-col md:flex-row gap-8 items-start md:items-center mt-12">
                <div className="w-32 h-32 rounded-full bg-gradient-to-tr from-accent to-purple-500 p-1 shrink-0 shadow-2xl">
                   <div className="w-full h-full bg-[#0D0D0F] rounded-full flex items-center justify-center text-4xl font-black">
                     {designer.user_id.substring(0, 2).toUpperCase()}
                   </div>
                </div>
                
                <div className="flex-1">
                  <h1 className="text-4xl font-display font-black tracking-tight mb-2">Designer {designer.user_id.substring(0, 5)}</h1>
                  <p className="text-[#9A9AA3] text-lg mb-4 max-w-2xl">{designer.bio || "This creative professional is ready to bring your vision to life."}</p>
                  
                  <div className="flex flex-wrap gap-6 text-sm font-medium">
                    <div className="flex items-center text-[#F5F5F5]">
                      <Star className="w-4 h-4 text-accent fill-accent mr-2" />
                      5.0 (New)
                    </div>

                    <div className="flex items-center text-[#9A9AA3]">
                      <Briefcase className="w-4 h-4 mr-2" />
                      {designer.hourly_rate ? `₹${designer.hourly_rate}/hr` : 'Open to offers'}
                    </div>
                  </div>
                </div>
                
                <div className="shrink-0 w-full md:w-auto">
                  <Link 
                    to="/projects/new"
                    className="block w-full text-center bg-white text-black font-bold px-8 py-4 rounded-xl hover:bg-gray-200 transition-colors shadow-lg shadow-white/10"
                  >
                    Hire Designer
                  </Link>
                  <button className="block w-full text-center mt-4 border border-[#2A2A32] text-white font-bold px-8 py-3 rounded-xl hover:bg-[#2A2A32] transition-colors">
                    <Mail className="w-4 h-4 inline-block mr-2" />
                    Message
                  </button>
                </div>
              </div>
            </div>

            {/* Content Tabs area */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              
              {/* Left Column: Details */}
              <div className="space-y-8">
                <div className="bg-[#15151A] border border-[#2A2A32] rounded-3xl p-8">
                  <h3 className="text-xl font-bold mb-6">Specialties</h3>
                  <div className="flex flex-wrap gap-2">
                    {designer.specialties.map(spec => (
                      <span key={spec} className="bg-[#2A2A32] text-[#F5F5F5] px-3 py-1.5 rounded-lg text-sm font-medium">
                        {spec}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="bg-[#15151A] border border-[#2A2A32] rounded-3xl p-8">
                  <h3 className="text-xl font-bold mb-6">About</h3>
                  <div className="space-y-4 text-[#9A9AA3] text-sm">
                    <div>
                      <span className="block text-[#F5F5F5] font-bold mb-1">Experience</span>
                      Not specified
                    </div>
                    <div>
                      <span className="block text-[#F5F5F5] font-bold mb-1">Response Time</span>
                      Usually within 24 hours
                    </div>
                    <div>
                      <span className="block text-[#F5F5F5] font-bold mb-1">Languages</span>
                      English, Hindi
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Right Column: Portfolio / Work */}
              <div className="lg:col-span-2">
                <div className="bg-[#15151A] border border-[#2A2A32] rounded-3xl p-8 min-h-[400px]">
                  <h3 className="text-xl font-bold mb-6">Portfolio</h3>
                  <div className="flex flex-col items-center justify-center h-64 text-center border-2 border-dashed border-[#2A2A32] rounded-2xl bg-[#0D0D0F]">
                    <p className="text-[#9A9AA3] mb-2">Portfolio items will be displayed here.</p>
                    <p className="text-sm text-[#5A5A63]">The designer is currently updating their public portfolio.</p>
                  </div>
                </div>
              </div>

            </div>

          </div>
        )}
      </main>
    </div>
  );
}
