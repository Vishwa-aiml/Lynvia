import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { discoveryService } from '../api/services/discovery.service';
import type { DesignerProfile } from '../types/marketplace';
import { Loader2, Search, Star, Briefcase } from 'lucide-react';
import Navbar from '../components/layout/Navbar';

export default function Designers() {
  const [designers, setDesigners] = useState<DesignerProfile[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    fetchDesigners();
  }, []);

  const fetchDesigners = async () => {
    setIsLoading(true);
    setError('');
    try {
      const response = await discoveryService.getDesigners();
      setDesigners(response.data);
    } catch (err: any) {
      console.error(err);
      setError('Failed to load designers. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  };

  const filteredDesigners = designers.filter(d => 
    d.user_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
    d.specialties.some(s => s.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <div className="min-h-screen bg-[#0D0D0F] font-sans text-[#F5F5F5]">
      <Navbar />

      <main className="pt-32 px-6 max-w-7xl mx-auto pb-24">
        {/* Header */}
        <div className="mb-12">
          <h1 className="text-4xl md:text-5xl font-display font-black tracking-tight uppercase mb-4 drop-shadow-sm">
            Find Designers
          </h1>
          <p className="text-[#9A9AA3] text-lg max-w-2xl mb-8">
            Browse our curated list of professional designers ready to bring your vision to life.
          </p>

          <div className="relative max-w-md">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-[#9A9AA3]" />
            </div>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by name or specialty..."
              className="block w-full pl-12 pr-4 py-3 bg-[#15151A] border border-[#2A2A32] rounded-xl text-[#F5F5F5] placeholder-[#9A9AA3]/50 focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent transition-colors"
            />
          </div>
        </div>

        {/* Content */}
        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-20">
            <Loader2 className="animate-spin h-10 w-10 text-accent mb-4" />
            <p className="text-[#9A9AA3]">Loading designers...</p>
          </div>
        ) : error ? (
          <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-6 rounded-2xl text-center max-w-2xl mx-auto">
            <p>{error}</p>
            <button onClick={fetchDesigners} className="mt-4 px-4 py-2 bg-red-500/20 rounded-lg hover:bg-red-500/30 transition-colors">
              Try Again
            </button>
          </div>
        ) : filteredDesigners.length === 0 ? (
          <div className="bg-[#15151A] border border-[#2A2A32] rounded-3xl p-16 text-center">
            <p className="text-[#9A9AA3] text-lg mb-4">No designers found matching your search.</p>
            <button onClick={() => setSearchQuery('')} className="text-accent hover:text-white transition-colors font-bold">
              Clear Search
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredDesigners.map(designer => (
              <div key={designer.user_id} className="bg-[#15151A] border border-[#2A2A32] rounded-2xl overflow-hidden flex flex-col transition-all hover:border-[#3A3A42]">
                <div className="p-6 flex-1 flex flex-col">
                  
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-4">
                      <div className="w-14 h-14 rounded-full bg-gradient-to-tr from-accent to-purple-500 p-0.5">
                         <div className="w-full h-full bg-[#0D0D0F] rounded-full flex items-center justify-center text-lg font-bold">
                           {designer.user_id.substring(0, 2).toUpperCase()}
                         </div>
                      </div>
                      <div>
                        <h3 className="font-bold text-lg leading-tight">Designer {designer.user_id.substring(0, 5)}</h3>
                        <p className="text-sm text-[#9A9AA3]">Creative Professional</p>
                      </div>
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-2 mb-4">
                    {designer.specialties.map(spec => (
                      <span key={spec} className="bg-[#2A2A32] text-[#9A9AA3] text-xs px-2.5 py-1 rounded-md">
                        {spec}
                      </span>
                    ))}
                  </div>

                  <p className="text-sm text-[#9A9AA3] mb-6 line-clamp-3 flex-1">
                    {designer.bio || "This designer hasn't added a bio yet but is available for new projects."}
                  </p>

                  <div className="flex items-center justify-between pt-4 border-t border-[#2A2A32]">
                    <div className="flex items-center gap-4">
                      <div className="flex items-center text-sm font-bold text-white">
                        <Star className="w-4 h-4 text-accent fill-accent mr-1" />
                        5.0
                      </div>
                      <div className="flex items-center text-sm text-[#9A9AA3]">
                        <Briefcase className="w-4 h-4 mr-1" />
                        {designer.hourly_rate ? `₹${designer.hourly_rate}/hr` : 'Open'}
                      </div>
                    </div>
                    <Link 
                      to={`/designers/${designer.user_id}`}
                      className="text-sm font-bold text-accent hover:text-white transition-colors"
                    >
                      View Profile &rarr;
                    </Link>
                  </div>

                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
