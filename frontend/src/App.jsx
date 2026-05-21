import React, { useState, useEffect, useRef } from 'react';
import { 
  Send, 
  Bot, 
  User, 
  Settings, 
  GraduationCap,
  MessageSquare,
  Bell,
  Compass,
  Library,
  Activity,
  Globe,
  ShieldCheck,
  Calendar,
  LayoutDashboard,
  RefreshCw,
  Plus,
  Trash2,
  Edit,
  Database,
  X
} from 'lucide-react';

const MODEL_NAME = "Campus-AI-Core";
const API_BASE_URL = "http://localhost:8002/api/v1";

const schemaMap = {
  faculties: [
    { name: 'name', type: 'text', label: 'Faculty Name', required: true },
    { name: 'description', type: 'textarea', label: 'Description' },
    { name: 'image_url', type: 'text', label: 'Image URL' }
  ],
  study_programs: [
    { name: 'faculty_id', type: 'number', label: 'Faculty ID', required: true },
    { name: 'name', type: 'text', label: 'Program Name', required: true },
    { name: 'degree', type: 'text', label: 'Degree (e.g., S1, S2)', required: true },
    { name: 'description', type: 'textarea', label: 'Description' },
    { name: 'accreditation', type: 'text', label: 'Accreditation' },
    { name: 'image_url', type: 'text', label: 'Image URL' }
  ],
  buildings: [
    { name: 'name', type: 'text', label: 'Building Name', required: true },
    { name: 'category', type: 'text', label: 'Category', required: true },
    { name: 'description', type: 'textarea', label: 'Description' },
    { name: 'address', type: 'textarea', label: 'Address' },
    { name: 'latitude', type: 'number', label: 'Latitude', step: 'any' },
    { name: 'longitude', type: 'number', label: 'Longitude', step: 'any' },
    { name: 'image_url', type: 'text', label: 'Image URL' }
  ],
  news: [
    { name: 'title', type: 'text', label: 'News Title', required: true },
    { name: 'content', type: 'textarea', label: 'Content', required: true },
    { name: 'image_url', type: 'text', label: 'Image URL' }
  ],
  products: [
    { name: 'name', type: 'text', label: 'Product Name', required: true },
    { name: 'description', type: 'textarea', label: 'Description' },
    { name: 'price', type: 'number', label: 'Price', required: true },
    { name: 'stock', type: 'number', label: 'Stock', required: true }
  ]
};

const App = () => {
  // --- Main States ---
  const [activeTab, setActiveTab] = useState('chat');
  const scrollRef = useRef(null);

  // --- Chat States ---
  const [messages, setMessages] = useState([
    { role: 'assistant', text: 'Selamat datang di Smart Campus! Saya adalah Asisten AI Akademik Anda. Ada yang bisa saya bantu terkait jadwal, fasilitas, atau informasi kampus hari ini?' }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  // --- Announcements State ---
  const [announcements, setAnnouncements] = useState([
    { time: '08:00 AM', msg: 'Pendaftaran Semester Pendek telah dibuka.', type: 'info' },
    { time: '09:30 AM', msg: 'Kuliah Umum: AI in Education di Aula Utama.', type: 'success' },
    { time: '10:15 AM', msg: 'Sistem KRS sedang dalam pemeliharaan rutin.', type: 'warning' }
  ]);
  
  // --- Admin Dashboard States ---
  const [adminSubTab, setAdminSubTab] = useState('faculties');
  const [adminData, setAdminData] = useState({
    faculties: [],
    study_programs: [],
    buildings: [],
    news: [],
    products: []
  });
  const [adminLoading, setAdminLoading] = useState(false);
  
  // Modal States
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, announcements, isTyping]);

  // Fetch admin data when sub-tab changes (or on load)
  useEffect(() => {
    if (activeTab === 'admin') {
      fetchAdminData(adminSubTab);
    }
  }, [activeTab, adminSubTab]);

  const addAnnouncement = (msg, type = 'info') => {
    const time = new Date().toLocaleTimeString([], { hour12: false, hour: '2-digit', minute:'2-digit' });
    setAnnouncements(prev => [...prev, { time, msg, type }]);
  };

  // --- Chat Logic ---
  const callBackend = async (userQuery) => {
    setIsTyping(true);
    addAnnouncement(`Memproses permintaan Anda...`, 'info');

    try {
      const history = messages.map(m => ({
        role: m.role,
        text: m.text
      }));

      const response = await fetch(`${API_BASE_URL}/chat/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: userQuery,
          history: history
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Server Error ${response.status}`);
      }

      const result = await response.json();
      const aiText = result.response || "Maaf, saya tidak dapat menemukan respons yang tepat.";
      
      setMessages(prev => [...prev, { role: 'assistant', text: aiText }]);
      addAnnouncement(`Respons diterima dari asisten.`, 'success');
    } catch (error) {
      addAnnouncement(`Error Koneksi: ${error.message}`, 'error');
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        text: `Error: ${error.message}. Pastikan server FastAPI Modul 3 berjalan di localhost:8002.` 
      }]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleSend = () => {
    if (!input.trim() || isTyping) return;
    const query = input.trim();
    setMessages(prev => [...prev, { role: 'user', text: query }]);
    setInput('');
    callBackend(query);
  };

  // --- Admin Logic ---
  const fetchAdminData = async (endpoint) => {
    setAdminLoading(true);
    try {
      // Endpoint mapping handling (some endpoints have dashes)
      const urlEndpoint = endpoint === 'study_programs' ? 'study-programs' : endpoint;
      const response = await fetch(`${API_BASE_URL}/${urlEndpoint}/`);
      
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      
      setAdminData(prev => ({
        ...prev,
        [endpoint]: data
      }));
    } catch (error) {
      console.error("Failed to fetch admin data:", error);
      addAnnouncement(`Gagal mengambil data ${endpoint} dari server.`, 'error');
    } finally {
      setAdminLoading(false);
    }
  };

  const handleOpenModal = () => {
    setFormData({});
    setIsModalOpen(true);
  };

  const handleInputChange = (e) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'number' && value !== '' ? Number(value) : value
    }));
  };

  const handleFormSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const urlEndpoint = adminSubTab === 'study_programs' ? 'study-programs' : adminSubTab;
      const response = await fetch(`${API_BASE_URL}/${urlEndpoint}/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Server Error ${response.status}`);
      }
      
      addAnnouncement(`Berhasil menambahkan data ke ${adminSubTab.replace('_', ' ')}`, 'success');
      setIsModalOpen(false);
      fetchAdminData(adminSubTab); // Refresh data
    } catch (error) {
      console.error("Failed to submit form:", error);
      addAnnouncement(`Gagal menambahkan data. Error: ${error.message}`, 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Yakin ingin menghapus data ini?")) return;
    try {
      const urlEndpoint = adminSubTab === 'study_programs' ? 'study-programs' : adminSubTab;
      const response = await fetch(`${API_BASE_URL}/${urlEndpoint}/${id}`, {
        method: 'DELETE',
      });
      
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      
      addAnnouncement(`Data berhasil dihapus dari ${adminSubTab.replace('_', ' ')}`, 'success');
      fetchAdminData(adminSubTab); // Refresh data
    } catch (error) {
      console.error("Failed to delete data:", error);
      addAnnouncement(`Gagal menghapus data.`, 'error');
    }
  };

  const adminTabs = [
    { id: 'faculties', label: 'Faculties' },
    { id: 'study_programs', label: 'Study Programs' },
    { id: 'buildings', label: 'Buildings' },
    { id: 'news', label: 'News' },
    { id: 'products', label: 'Products' }
  ];

  return (
    <div className="flex h-screen bg-[#0f172a] text-slate-100 font-sans overflow-hidden relative">
      {/* Sidebar */}
      <div className="w-16 md:w-64 bg-slate-900/80 backdrop-blur-xl border-r border-slate-800 flex flex-col items-center py-6 gap-8 shadow-xl z-20">
        <div className="flex items-center gap-3 px-4 w-full justify-center md:justify-start">
          <div className="p-2 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl shadow-lg shadow-blue-500/30">
            <GraduationCap size={24} className="text-white" />
          </div>
          <span className="hidden md:block font-bold text-xl tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-indigo-400">Smart Campus</span>
        </div>

        <nav className="flex-1 w-full px-3 space-y-2">
          {[
            { id: 'chat', icon: <MessageSquare size={20} />, label: 'Campus Assistant' },
            { id: 'announcements', icon: <Bell size={20} />, label: 'Announcements' },
            { id: 'services', icon: <Compass size={20} />, label: 'Student Services' },
            { id: 'library', icon: <Library size={20} />, label: 'Library & Resources' },
            { id: 'admin', icon: <LayoutDashboard size={20} />, label: 'Admin Dashboard' },
          ].map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center justify-center md:justify-start gap-3 p-3 rounded-xl transition-all duration-300 ${
                activeTab === item.id 
                  ? 'bg-blue-500/15 text-blue-400 border border-blue-500/30 shadow-[inset_0_1px_1px_rgba(255,255,255,0.1)]' 
                  : 'hover:bg-slate-800 hover:text-slate-200 text-slate-400 border border-transparent'
              }`}
            >
              {item.icon}
              <span className="hidden md:block font-medium">{item.label}</span>
            </button>
          ))}
        </nav>

        <div className="px-4 w-full">
          <div className="bg-slate-800/40 backdrop-blur-md p-3 rounded-xl border border-slate-700 hidden md:block transition-all hover:bg-slate-800/60">
            <div className="flex items-center gap-2 mb-2">
              <Activity size={14} className="text-emerald-400" />
              <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider">System Status</span>
            </div>
            <p className="text-[10px] text-slate-500 mb-1">Campus Network: Online</p>
            <div className="h-1.5 w-full bg-slate-700 rounded-full overflow-hidden">
              <div className="h-full bg-gradient-to-r from-emerald-400 to-teal-500 w-full animate-pulse shadow-[0_0_10px_rgba(52,211,153,0.5)]"></div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col relative overflow-hidden bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-slate-800 via-slate-900 to-[#0f172a]">
        
        {/* Header */}
        <header className="h-16 border-b border-slate-800 flex items-center justify-between px-8 bg-slate-900/40 backdrop-blur-xl z-10 sticky top-0 shadow-sm">
          <div className="flex items-center gap-4">
            <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-widest">
              {activeTab === 'chat' && 'Interactive Assistant'}
              {activeTab === 'announcements' && 'Campus Bulletin'}
              {activeTab === 'services' && 'Student Portal'}
              {activeTab === 'library' && 'Digital Repository'}
              {activeTab === 'admin' && 'Central Administration'}
            </h2>
            <div className="flex items-center gap-2 bg-slate-800/60 px-3 py-1 rounded-full border border-slate-700/50 shadow-inner">
              <div className="w-2 h-2 bg-emerald-400 rounded-full shadow-[0_0_8px_rgba(52,211,153,0.8)]"></div>
              <span className="text-[10px] font-bold text-slate-300 tracking-wider">CONNECTED</span>
            </div>
          </div>
          <div className="flex items-center gap-5 text-slate-400">
            <Calendar size={18} className="cursor-pointer hover:text-blue-400 transition-colors" />
            <Globe size={18} className="cursor-pointer hover:text-blue-400 transition-colors" />
            <Settings size={18} className="cursor-pointer hover:text-blue-400 transition-colors" />
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500 border-2 border-slate-800 shadow-md"></div>
          </div>
        </header>

        {/* Tab Content */}
        <div className="flex-1 overflow-hidden relative">
          
          {/* Chat Tab */}
          {activeTab === 'chat' && (
            <div className="h-full flex flex-col max-w-4xl mx-auto w-full px-4 pt-6 pb-4">
              <div className="flex-1 overflow-y-auto pr-2 space-y-6 custom-scrollbar" ref={scrollRef}>
                {messages.map((msg, idx) => (
                  <div key={idx} className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-in fade-in slide-in-from-bottom-2 duration-300`}>
                    {msg.role === 'assistant' && (
                      <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shrink-0 shadow-lg shadow-blue-500/20">
                        <Bot size={20} className="text-white" />
                      </div>
                    )}
                    <div className={`max-w-[80%] p-4 rounded-2xl shadow-md leading-relaxed ${
                      msg.role === 'user' 
                      ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-tr-sm shadow-blue-900/20' 
                      : 'bg-slate-800/80 backdrop-blur-sm text-slate-100 border border-slate-700/50 rounded-tl-sm shadow-slate-900/50'
                    }`}>
                      <p className="text-[14px] whitespace-pre-wrap">{msg.text}</p>
                    </div>
                    {msg.role === 'user' && (
                      <div className="w-9 h-9 rounded-xl bg-slate-700/80 flex items-center justify-center shrink-0 border border-slate-600 shadow-inner">
                        <User size={20} className="text-slate-300" />
                      </div>
                    )}
                  </div>
                ))}
                {isTyping && (
                  <div className="flex gap-4 justify-start animate-in fade-in">
                    <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shrink-0 shadow-lg shadow-blue-500/20">
                      <Bot size={20} className="text-white" />
                    </div>
                    <div className="bg-slate-800/80 backdrop-blur-sm p-4 rounded-2xl rounded-tl-sm border border-slate-700/50 flex gap-2 items-center shadow-sm">
                      <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce [animation-delay:-.2s]"></div>
                      <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce [animation-delay:-.4s]"></div>
                    </div>
                  </div>
                )}
              </div>

              {/* Input Area */}
              <div className="pt-4 mt-auto">
                <div className="relative group">
                  <div className="absolute -inset-1 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-2xl blur opacity-20 group-focus-within:opacity-40 transition duration-500"></div>
                  <div className="relative flex items-center bg-slate-900/80 backdrop-blur-xl border border-slate-700/80 rounded-2xl p-2 pl-5 shadow-2xl">
                    <input
                      type="text"
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                      placeholder="Tanyakan sesuatu tentang jadwal, ruangan, atau kegiatan kampus..."
                      className="flex-1 bg-transparent border-none outline-none text-slate-200 placeholder-slate-500 text-[14px]"
                    />
                    <button 
                      onClick={handleSend}
                      disabled={isTyping || !input.trim()}
                      className="p-3 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white rounded-xl transition-all shadow-lg hover:shadow-blue-500/25 ml-2"
                    >
                      <Send size={18} className="ml-0.5" />
                    </button>
                  </div>
                </div>
                <p className="text-[10px] text-center mt-4 text-slate-500 uppercase font-semibold tracking-widest flex items-center justify-center gap-2">
                  <ShieldCheck size={12} />
                  Powered by {MODEL_NAME}
                </p>
              </div>
            </div>
          )}

          {/* Announcements Tab */}
          {activeTab === 'announcements' && (
            <div className="h-full p-6 md:p-10 font-sans max-w-5xl mx-auto w-full">
              <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800/80 rounded-2xl h-full flex flex-col shadow-2xl overflow-hidden">
                <div className="bg-slate-800/40 px-6 py-4 border-b border-slate-800/80 flex items-center gap-3">
                  <div className="p-2 bg-amber-500/10 rounded-lg">
                    <Bell size={18} className="text-amber-400" />
                  </div>
                  <div>
                    <h3 className="text-slate-200 font-bold">Campus Bulletin</h3>
                    <p className="text-xs text-slate-500">Pengumuman dan pemberitahuan terbaru</p>
                  </div>
                </div>
                <div className="flex-1 overflow-y-auto p-6 space-y-4 custom-scrollbar" ref={scrollRef}>
                  {announcements.map((ann, i) => (
                    <div key={i} className="flex gap-4 bg-slate-800/30 hover:bg-slate-800/60 p-4 rounded-xl border border-slate-700/30 transition-all group">
                      <div className="shrink-0 flex flex-col items-center justify-center w-16">
                        <span className="text-xs font-semibold text-slate-500 group-hover:text-slate-400">{ann.time}</span>
                      </div>
                      <div className="w-px bg-slate-700/50 group-hover:bg-slate-600"></div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wider ${
                            ann.type === 'error' ? 'bg-rose-500/10 text-rose-400' :
                            ann.type === 'success' ? 'bg-emerald-500/10 text-emerald-400' :
                            ann.type === 'warning' ? 'bg-amber-500/10 text-amber-400' :
                            'bg-blue-500/10 text-blue-400'
                          }`}>
                            {ann.type}
                          </span>
                        </div>
                        <p className="text-slate-300 text-sm">{ann.msg}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Services Tab */}
          {activeTab === 'services' && (
            <div className="p-8 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 overflow-y-auto h-full custom-scrollbar max-w-7xl mx-auto">
              {[
                { name: 'KRS Online', desc: 'Isi Kartu Rencana Studi dan atur jadwal perkuliahan.', status: 'Active', icon: <Calendar className="text-blue-400" /> },
                { name: 'Campus Map', desc: 'Navigasi gedung, ruangan, dan fasilitas kampus terpadu.', status: 'Active', icon: <Compass className="text-emerald-400" /> },
                { name: 'E-Payment', desc: 'Pembayaran UKT dan tagihan layanan akademik lainnya.', status: 'Maintenance', icon: <ShieldCheck className="text-rose-400" /> },
                { name: 'Student Analytics', desc: 'Pantau IPK, absensi, dan performa akademik Anda.', status: 'Active', icon: <Activity className="text-indigo-400" /> },
              ].map((tool, i) => (
                <div key={i} className="bg-slate-800/40 backdrop-blur-md border border-slate-700/50 p-6 rounded-2xl hover:border-blue-500/50 hover:bg-slate-800/80 transition-all group shadow-lg hover:shadow-blue-500/10 flex flex-col h-full">
                  <div className="flex justify-between items-start mb-5">
                    <div className="p-3.5 bg-slate-900/80 border border-slate-700 rounded-xl group-hover:scale-110 transition-transform shadow-inner">
                      {tool.icon}
                    </div>
                    <span className={`text-[10px] font-bold px-2.5 py-1 rounded-full ${
                      tool.status === 'Active' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                    }`}>
                      {tool.status}
                    </span>
                  </div>
                  <h3 className="font-bold text-slate-100 mb-2 text-lg">{tool.name}</h3>
                  <p className="text-sm text-slate-400 mb-6 leading-relaxed flex-1">{tool.desc}</p>
                  <button className="w-full py-2.5 bg-slate-900/50 hover:bg-blue-600 text-slate-300 hover:text-white rounded-xl text-sm font-medium transition-colors border border-slate-700 hover:border-transparent">
                    Akses Layanan
                  </button>
                </div>
              ))}
            </div>
          )}

          {/* Library Tab */}
          {activeTab === 'library' && (
             <div className="h-full flex flex-col items-center justify-center text-center p-12 bg-slate-900/20">
               <div className="p-8 bg-gradient-to-br from-indigo-500/20 to-purple-600/20 border border-indigo-500/30 rounded-full mb-8 shadow-[0_0_30px_rgba(99,102,241,0.2)]">
                 <Library size={56} className="text-indigo-400" />
               </div>
               <h2 className="text-3xl font-bold mb-4 text-slate-100">Perpustakaan & Repositori</h2>
               <p className="text-slate-400 max-w-lg mb-8 leading-relaxed">
                 Jelajahi ribuan jurnal, tesis, dan literatur akademik. Sistem integrasi perpustakaan sedang dalam tahap sinkronisasi dengan database utama.
               </p>
               <button className="px-6 py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-medium transition-all shadow-lg shadow-indigo-500/25">
                 Jelajahi Katalog (Beta)
               </button>
             </div>
          )}

          {/* Admin Dashboard Tab */}
          {activeTab === 'admin' && (
            <div className="h-full flex flex-col p-6 font-sans">
              
              {/* Admin Navigation */}
              <div className="flex items-center gap-2 mb-6 border-b border-slate-800 pb-4 overflow-x-auto custom-scrollbar">
                {adminTabs.map(tab => (
                  <button
                    key={tab.id}
                    onClick={() => setAdminSubTab(tab.id)}
                    className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all whitespace-nowrap ${
                      adminSubTab === tab.id 
                        ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/20' 
                        : 'bg-slate-800/50 text-slate-400 hover:bg-slate-800 hover:text-slate-200 border border-slate-700/50'
                    }`}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>

              {/* Data View Area */}
              <div className="flex-1 bg-slate-900/60 backdrop-blur-xl border border-slate-800 rounded-2xl shadow-xl flex flex-col overflow-hidden">
                {/* Header Data View */}
                <div className="flex justify-between items-center px-6 py-4 border-b border-slate-800/80 bg-slate-800/30">
                  <h3 className="font-bold text-lg text-slate-100 capitalize">
                    Manage {adminSubTab.replace('_', ' ')}
                  </h3>
                  <div className="flex items-center gap-3">
                    <button 
                      onClick={() => fetchAdminData(adminSubTab)}
                      disabled={adminLoading}
                      className="p-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-slate-300 transition-colors border border-slate-700"
                      title="Refresh Data"
                    >
                      <RefreshCw size={16} className={adminLoading ? 'animate-spin' : ''} />
                    </button>
                    <button 
                      onClick={handleOpenModal}
                      className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-sm font-medium transition-colors shadow-lg shadow-emerald-600/20"
                    >
                      <Plus size={16} />
                      <span className="hidden sm:inline">Add New</span>
                    </button>
                  </div>
                </div>

                {/* Table Content */}
                <div className="flex-1 overflow-auto custom-scrollbar p-0">
                  {adminLoading ? (
                    <div className="flex items-center justify-center h-full">
                      <div className="flex flex-col items-center gap-4 text-slate-400">
                        <RefreshCw size={32} className="animate-spin text-blue-500" />
                        <p>Memuat data dari server...</p>
                      </div>
                    </div>
                  ) : adminData[adminSubTab] && adminData[adminSubTab].length > 0 ? (
                    <table className="w-full text-left text-sm text-slate-300">
                      <thead className="text-xs text-slate-400 uppercase bg-slate-900/50 sticky top-0 z-10 backdrop-blur-sm">
                        <tr>
                          {Object.keys(adminData[adminSubTab][0]).map(key => (
                             <th key={key} className="px-6 py-4 font-semibold border-b border-slate-800/80">
                               {key.replace('_', ' ')}
                             </th>
                          ))}
                          <th className="px-6 py-4 font-semibold border-b border-slate-800/80 text-right">Actions</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/60">
                        {adminData[adminSubTab].map((item, idx) => (
                          <tr key={item.id || idx} className="hover:bg-slate-800/30 transition-colors">
                            {Object.entries(item).map(([key, val]) => (
                              <td key={key} className="px-6 py-4 whitespace-nowrap overflow-hidden text-ellipsis max-w-xs">
                                {typeof val === 'object' ? JSON.stringify(val) : String(val)}
                              </td>
                            ))}
                            <td className="px-6 py-4 text-right">
                              <div className="flex justify-end gap-2">
                                <button className="p-1.5 text-blue-400 hover:bg-blue-400/10 rounded-md transition-colors" title="Edit">
                                  <Edit size={16} />
                                </button>
                                <button 
                                  onClick={() => handleDelete(item.id)}
                                  className="p-1.5 text-rose-400 hover:bg-rose-400/10 rounded-md transition-colors" 
                                  title="Delete"
                                >
                                  <Trash2 size={16} />
                                </button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <div className="flex flex-col items-center justify-center h-full text-slate-500 p-8 text-center">
                      <Database size={48} className="mb-4 text-slate-600 opacity-50" />
                      <p className="text-lg font-medium mb-1">Data Kosong</p>
                      <p className="text-sm">Tidak ada rekaman ditemukan untuk {adminSubTab.replace('_', ' ')}. Silakan tambahkan data baru atau refresh.</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

        </div>
      </main>

      {/* --- CRUD Modal --- */}
      {isModalOpen && (
        <div className="absolute inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-lg shadow-2xl overflow-hidden flex flex-col">
            <div className="flex justify-between items-center px-6 py-4 border-b border-slate-800 bg-slate-800/50">
              <h3 className="font-bold text-lg text-slate-100 capitalize">
                Add New {adminSubTab.replace('_', ' ')}
              </h3>
              <button 
                onClick={() => setIsModalOpen(false)}
                className="text-slate-400 hover:text-white transition-colors p-1"
              >
                <X size={20} />
              </button>
            </div>
            
            <form onSubmit={handleFormSubmit} className="flex-1 overflow-y-auto p-6 space-y-4 custom-scrollbar max-h-[60vh]">
              {schemaMap[adminSubTab] && schemaMap[adminSubTab].map((field) => (
                <div key={field.name} className="flex flex-col gap-1.5">
                  <label className="text-sm font-medium text-slate-300">
                    {field.label} {field.required && <span className="text-rose-500">*</span>}
                  </label>
                  {field.type === 'textarea' ? (
                    <textarea
                      name={field.name}
                      value={formData[field.name] || ''}
                      onChange={handleInputChange}
                      required={field.required}
                      rows={3}
                      className="w-full bg-slate-950 border border-slate-700 rounded-xl p-3 text-sm text-slate-200 outline-none focus:border-blue-500 transition-colors custom-scrollbar"
                      placeholder={`Enter ${field.label.toLowerCase()}...`}
                    />
                  ) : (
                    <input
                      type={field.type}
                      name={field.name}
                      value={formData[field.name] || ''}
                      onChange={handleInputChange}
                      required={field.required}
                      step={field.step}
                      className="w-full bg-slate-950 border border-slate-700 rounded-xl p-3 text-sm text-slate-200 outline-none focus:border-blue-500 transition-colors"
                      placeholder={`Enter ${field.label.toLowerCase()}...`}
                    />
                  )}
                </div>
              ))}
            </form>
            
            <div className="px-6 py-4 border-t border-slate-800 bg-slate-900 flex justify-end gap-3">
              <button
                type="button"
                onClick={() => setIsModalOpen(false)}
                className="px-4 py-2 rounded-xl text-sm font-medium text-slate-300 hover:bg-slate-800 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleFormSubmit}
                disabled={isSubmitting}
                className="px-6 py-2 rounded-xl text-sm font-medium bg-blue-600 hover:bg-blue-500 text-white transition-colors disabled:opacity-50 flex items-center gap-2"
              >
                {isSubmitting ? (
                  <><RefreshCw size={16} className="animate-spin" /> Saving...</>
                ) : (
                  'Save Data'
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      <style>{`
        .custom-scrollbar::-webkit-scrollbar { width: 6px; height: 6px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(51, 65, 85, 0.5); border-radius: 10px; }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: rgba(71, 85, 105, 0.8); }
      `}</style>
    </div>
  );
};

export default App;