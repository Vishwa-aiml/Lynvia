import Navbar from '../components/layout/Navbar';

export default function Disputes() {
  return (
    <div className="min-h-screen bg-[#0D0D0F] font-sans text-[#F5F5F5]">
      <Navbar />
      <main className="pt-32 px-6 max-w-7xl mx-auto pb-24">
        <h1 className="text-4xl font-display font-black tracking-tight uppercase mb-8">Disputes</h1>
        <div className="bg-[#15151A] border border-[#2A2A32] rounded-3xl p-16 text-center">
          <p className="text-[#9A9AA3] text-lg">This feature is currently under development.</p>
        </div>
      </main>
    </div>
  );
}
