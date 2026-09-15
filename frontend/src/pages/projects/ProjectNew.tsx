import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { projectService } from '../../api/services/project.service';
import { Loader2, ArrowRight } from 'lucide-react';
import Navbar from '../../components/layout/Navbar';

export default function ProjectNew() {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: 'Logo & Branding',
    budget: '',
    expected_delivery_days: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const categories = ['Logo & Branding', 'Posters', 'Social Media Design', 'Brand Identity', 'Marketing Creatives'];

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const budget = parseFloat(formData.budget);
      const expected_delivery_days = parseInt(formData.expected_delivery_days);
      
      if (isNaN(budget) || budget < 1000) {
        throw new Error("Budget must be at least ₹1000.");
      }
      
      if (isNaN(expected_delivery_days) || expected_delivery_days < 1) {
        throw new Error("Delivery days must be at least 1.");
      }

      await projectService.createProject({
        ...formData,
        budget,
        expected_delivery_days
      });
      
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Failed to create project. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0D0D0F] font-sans text-[#F5F5F5]">
      <Navbar />
      
      <main className="pt-32 px-6 max-w-3xl mx-auto pb-24">
        <div className="mb-12">
          <h1 className="text-4xl md:text-5xl font-display font-black tracking-tight uppercase mb-4 drop-shadow-sm">
            Start a New Project
          </h1>
          <p className="text-[#9A9AA3] text-lg">
            Give us the details, and we'll match you with top creative talent.
          </p>
        </div>

        <div className="bg-[#15151A] border border-[#2A2A32] rounded-3xl p-8 md:p-12 shadow-xl">
          {error && (
             <div className="mb-8 p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 font-bold text-center">
               {error}
             </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-8">
            <div className="space-y-2">
              <label className="block text-sm font-bold text-[#9A9AA3] uppercase tracking-wider">Project Title</label>
              <input 
                type="text" 
                name="title"
                required
                value={formData.title}
                onChange={handleChange}
                placeholder="e.g. Complete Brand Identity for Tech Startup"
                className="w-full bg-[#0D0D0F] border border-[#2A2A32] rounded-xl px-5 py-4 text-white focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent transition-colors"
              />
            </div>

            <div className="space-y-2">
              <label className="block text-sm font-bold text-[#9A9AA3] uppercase tracking-wider">Project Category</label>
              <select 
                name="category"
                value={formData.category}
                onChange={handleChange}
                className="w-full bg-[#0D0D0F] border border-[#2A2A32] rounded-xl px-5 py-4 text-white focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent transition-colors appearance-none"
              >
                {categories.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>

            <div className="space-y-2">
              <label className="block text-sm font-bold text-[#9A9AA3] uppercase tracking-wider">Description & Requirements</label>
              <textarea 
                name="description"
                required
                value={formData.description}
                onChange={handleChange}
                rows={5}
                placeholder="Describe your vision, target audience, and any specific requirements..."
                className="w-full bg-[#0D0D0F] border border-[#2A2A32] rounded-xl px-5 py-4 text-white focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent transition-colors resize-none"
              ></textarea>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="space-y-2">
                <label className="block text-sm font-bold text-[#9A9AA3] uppercase tracking-wider">Budget (₹)</label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-5 flex items-center pointer-events-none">
                    <span className="text-[#9A9AA3] font-bold">₹</span>
                  </div>
                  <input 
                    type="number" 
                    name="budget"
                    required
                    min="1000"
                    value={formData.budget}
                    onChange={handleChange}
                    placeholder="10000"
                    className="w-full bg-[#0D0D0F] border border-[#2A2A32] rounded-xl pl-12 pr-5 py-4 text-white focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent transition-colors"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="block text-sm font-bold text-[#9A9AA3] uppercase tracking-wider">Expected Delivery (Days)</label>
                <input 
                  type="number" 
                  name="expected_delivery_days"
                  required
                  min="1"
                  value={formData.expected_delivery_days}
                  onChange={handleChange}
                  placeholder="7"
                  className="w-full bg-[#0D0D0F] border border-[#2A2A32] rounded-xl px-5 py-4 text-white focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent transition-colors"
                />
              </div>
            </div>

            <div className="pt-6">
              <button
                type="submit"
                disabled={isLoading}
                className="w-full flex justify-center items-center py-5 px-6 border border-transparent rounded-xl shadow-lg shadow-accent/20 text-lg font-bold text-white bg-accent hover:bg-accent/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-[#0D0D0F] focus:ring-accent transition-all disabled:opacity-70 disabled:cursor-not-allowed hover:-translate-y-1"
              >
                {isLoading ? (
                  <Loader2 className="animate-spin h-6 w-6" />
                ) : (
                  <>
                    Post Project for Proposals
                    <ArrowRight className="ml-3 h-5 w-5" />
                  </>
                )}
              </button>
              <p className="text-center text-xs text-[#9A9AA3] mt-4 font-bold uppercase tracking-wider">
                No upfront payment required to post a project.
              </p>
            </div>
          </form>
        </div>
      </main>
    </div>
  );
}
