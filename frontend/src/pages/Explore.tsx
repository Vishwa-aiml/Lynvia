import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { discoveryService } from '../api/services/discovery.service';
import type { Project, DesignerProfile } from '../types/marketplace';
import { Loader2, Search, Filter } from 'lucide-react';
import Navbar from '../components/layout/Navbar';

export default function Explore() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [designers, setDesigners] = useState<DesignerProfile[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [activeCategory, setActiveCategory] = useState('All');

  const categories = ['All', 'Logo & Branding', 'Posters', 'Social Media Design', 'Brand Identity', 'Marketing Creatives'];

  useEffect(() => {
    fetchDiscoveryData();
  }, [activeCategory]);

  const fetchDiscoveryData = async () => {
    setIsLoading(true);
    setError('');
    try {
      const categoryParam = activeCategory === 'All' ? undefined : activeCategory;
      const [projectsRes, designersRes] = await Promise.all([
        discoveryService.getProjects(categoryParam),
        discoveryService.getDesigners(categoryParam)
      ]);
      setProjects(projectsRes.data);
      setDesigners(designersRes.data);
    } catch (err: any) {
      console.error(err);
      setError('Failed to load explore data. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0D0D0F] font-sans text-[#F5F5F5]">
      <Navbar />

      <main className="pt-32 px-6 max-w-7xl mx-auto pb-24">
        {/* Hero Section */}
        <div className="mb-16 text-center max-w-3xl mx-auto">
          <h1 className="text-5xl md:text-6xl font-display font-black tracking-tight uppercase mb-6 drop-shadow-sm">
            Explore Creative Work
          </h1>
          <p className="text-[#9A9AA3] text-lg mb-10">
            Discover the best projects and top-tier designers on Lynvia.
          </p>

          {/* Search Bar */}
          <div className="relative max-w-xl mx-auto">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-[#9A9AA3]" />
            </div>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search designs, categories, designers..."
              className="block w-full pl-12 pr-4 py-4 bg-[#15151A] border border-[#2A2A32] rounded-2xl text-[#F5F5F5] placeholder-[#9A9AA3]/50 focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent transition-colors"
            />
          </div>
        </div>

        {/* Category Filters */}
        <div className="flex flex-wrap items-center justify-center gap-3 mb-16">
          <Filter className="h-5 w-5 text-[#9A9AA3] mr-2" />
          {categories.map(category => (
            <button
              key={category}
              onClick={() => setActiveCategory(category)}
              className={`px-5 py-2 rounded-full text-sm font-bold transition-all ${
                activeCategory === category 
                  ? 'bg-accent text-white border-transparent' 
                  : 'bg-[#15151A] text-[#9A9AA3] border border-[#2A2A32] hover:border-[#9A9AA3] hover:text-white'
              }`}
            >
              {category}
            </button>
          ))}
        </div>

        {/* Content Area */}
        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-20">
            <Loader2 className="animate-spin h-10 w-10 text-accent mb-4" />
            <p className="text-[#9A9AA3]">Loading explore feed...</p>
          </div>
        ) : error ? (
          <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-6 rounded-2xl text-center max-w-2xl mx-auto">
            <p>{error}</p>
            <button onClick={fetchDiscoveryData} className="mt-4 px-4 py-2 bg-red-500/20 rounded-lg hover:bg-red-500/30 transition-colors">
              Try Again
            </button>
          </div>
        ) : (
          <div className="space-y-24">
            
            {/* Open Projects Section */}
            <section>
              <div className="flex items-center justify-between mb-8">
                <h2 className="text-3xl font-display font-black uppercase">Open Projects</h2>
                <Link to="/projects/new" className="text-accent hover:text-white transition-colors font-bold text-sm">
                  Start a Project &rarr;
                </Link>
              </div>
              
              {projects.length === 0 ? (
                <div className="bg-[#15151A] border border-[#2A2A32] rounded-3xl p-12 text-center">
                  <p className="text-[#9A9AA3] mb-4">No open projects found in this category.</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {projects.filter(p => p.title.toLowerCase().includes(searchQuery.toLowerCase())).map(project => (
                    <Link to={`/projects/${project.id}`} key={project.id} className="group bg-[#15151A] border border-[#2A2A32] rounded-2xl overflow-hidden hover:border-accent transition-colors block">
                      <div className="p-6">
                        <div className="flex justify-between items-start mb-4">
                          <span className="bg-white/5 text-white/70 px-3 py-1 rounded-full text-xs font-bold uppercase">{project.category}</span>
                          <span className="text-accent font-bold">₹{project.budget}</span>
                        </div>
                        <h3 className="text-xl font-bold mb-2 group-hover:text-accent transition-colors">{project.title}</h3>
                        <p className="text-[#9A9AA3] text-sm line-clamp-3 mb-6">
                          {project.description}
                        </p>
                        <div className="flex items-center justify-between text-xs text-[#9A9AA3]">
                          <span>{project.deadline ? new Date(project.deadline).toLocaleDateString() : 'Flexible Timeline'}</span>
                          <span className="font-bold text-white bg-accent/20 px-2 py-1 rounded">Open</span>
                        </div>
                      </div>
                    </Link>
                  ))}
                </div>
              )}
            </section>

            {/* Featured Designers Section */}
            <section>
              <div className="flex items-center justify-between mb-8">
                <h2 className="text-3xl font-display font-black uppercase">Featured Designers</h2>
                <Link to="/designers" className="text-accent hover:text-white transition-colors font-bold text-sm">
                  View All &rarr;
                </Link>
              </div>

              {designers.length === 0 ? (
                <div className="bg-[#15151A] border border-[#2A2A32] rounded-3xl p-12 text-center">
                  <p className="text-[#9A9AA3] mb-4">No designers found in this category.</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                  {designers.filter(d => d.user_id.toLowerCase().includes(searchQuery.toLowerCase())).map(designer => (
                    <Link to={`/designers/${designer.user_id}`} key={designer.user_id} className="group bg-[#15151A] border border-[#2A2A32] rounded-2xl overflow-hidden hover:border-accent transition-colors block text-center p-6">
                       <div className="w-20 h-20 rounded-full bg-gradient-to-tr from-accent to-purple-500 mx-auto mb-4 p-1">
                          <div className="w-full h-full bg-[#0D0D0F] rounded-full flex items-center justify-center text-xl font-bold">
                            {designer.user_id.substring(0, 2).toUpperCase()}
                          </div>
                       </div>
                       <h3 className="font-bold text-lg group-hover:text-accent transition-colors mb-1 truncate">Designer {designer.user_id.substring(0, 5)}</h3>
                       <p className="text-xs text-[#9A9AA3] mb-4 h-8 overflow-hidden">{designer.specialties.join(', ')}</p>
                       <span className="text-xs font-bold bg-[#2A2A32] px-3 py-1.5 rounded-full">
                         {designer.hourly_rate ? `₹${designer.hourly_rate}/hr` : 'Open to offers'}
                       </span>
                    </Link>
                  ))}
                </div>
              )}
            </section>

          </div>
        )}

      </main>
    </div>
  );
}
